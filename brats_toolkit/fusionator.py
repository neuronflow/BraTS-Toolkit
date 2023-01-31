# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for the fusion of segmentation labels
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.
import os
import logging
import itertools
import math

import numpy as np
import os.path as op
from .util import own_itk as oitk
from .util import filemanager as fm

class Fusionator(object):
    def __init__(self, verbose=True):
        self.verbose = verbose

    def binaryMav(self, candidates, weights=None):
        '''
        binaryMav performs majority vote fusion on an arbitary number of input segmentations with
        only two classes each (1 and 0).
        
        Args:
            candidates (list): the candidate segmentations as binary numpy arrays of same shape
            weights (list, optional): associated weights for each segmentation in candidates. Defaults to None.
        
        Return
            array: a numpy array with the majority vote result
        '''       
        num = len(candidates)
        if weights == None:
            weights = itertools.repeat(1,num)
        # manage empty calls
        if num == 0:
            print('ERROR! No segmentations to fuse.')
        elif num == 1: 
            return candidates[0]
        if self.verbose:
            print ('Number of segmentations to be fused using compound majority vote is: ', num)
            for c in candidates:
                print('Candidate with shape {} and values {} and sum {}'.format(c.shape, np.unique(c), np.sum(c)))
        # load first segmentation and use it to create initial numpy arrays
        temp = candidates[0]
        result = np.zeros(temp.shape)
        #loop through all available segmentations and tally votes for each class
        label = np.zeros(temp.shape)
        for c, w in zip(candidates, weights):
            if c.max() != 1 or c.min() != 0:
                logging.warning('The passed segmentation contains labels other than 1 and 0.')
            print('weight is: ' + str(w))
            label[c == 1] += 1.0*w
        num = sum(weights)
        result[label >= (num/2.0)] = 1
        if self.verbose:
            print('Shape of result:', result.shape)
            print('Shape of current input array:', temp.shape)
            print('Labels and datatype of current output:', result.max(), 
                                            result.min(), result.dtype)
        return result

    def mav(self, candidates, labels=None, weights=None):
        '''
        mav performs majority vote fusion on an arbitary number of input segmentations with
        an arbitrary number of labels. 
        
        Args:
            candidates (list): the candidate segmentations as binary numpy arrays of same shape
            labels (list, optional): a list of labels present in the candidates. Defaults to None.
            weights (list, optional): weights for the fusion. Defaults to None.
        
        Returns:
            array: a numpy array with the majority vote result
        '''
        num = len(candidates)
        if weights == None:
            weights = itertools.repeat(1,num)
        # manage empty calls
        if num == 0:
            print('ERROR! No segmentations to fuse.')
        if self.verbose:
            print ('Number of segmentations to be fused using compound majority vote is: ', num)
        # if no labels are passed, get the labels from the first input file (might lead to misisng labels!)
        if labels == None:
            labels = np.unique(candidates[0])
            for c in candidates:
                labels = np.append(labels, np.unique(c))
                print('Labels of current candidate: {}, dtype: {}'.format(np.unique(c), c.dtype))
            labels = np.unique(labels).astype(int)
            logging.warning('No labels passed, choosing those labels automatically: {}'.format(labels))
        # remove background label
        if 0 in labels:
            labels = np.delete(labels, 0)
        # load first segmentation and use it to create initial numpy arrays
        temp = candidates[0]
        result = np.zeros(temp.shape)
        #loop through all available segmentations and tally votes for each class
        print('Labels: {}'.format(labels))
        for l in sorted(labels, reverse=True):
            label = np.zeros(temp.shape)
            num = 0
            for c, w in zip(candidates, weights):
                print('weight is: ' + str(w))
                label[c == l] += 1.0*w
            num = sum(weights)
            print(num)
            result[label >= (num/2.0)] = l
        if self.verbose:
            print('Shape of result:', result.shape)
            print('Labels and datatype of result:', result.max(), 
                                            result.min(), result.dtype)
        return result

    def brats_simple(self, candidates, weights=None, t=0.05, stop=25, inc=0.07, method='dice', iterations=25):
        '''
        BRATS DOMAIN ADAPTED!!!!! simple implementation using DICE scoring
        Iteratively estimates the accuracy of the segmentations and dynamically assigns weights 
        for the next iteration. Continues for each label until convergence is reached. 

        Args:
            candidates (list): [description]
            weights (list, optional): [description]. Defaults to None.
            t (float, optional): [description]. Defaults to 0.05.
            stop (int, optional): [description]. Defaults to 25.
            inc (float, optional): [description]. Defaults to 0.07.
            method (str, optional): [description]. Defaults to 'dice'.
            iterations (int, optional): [description]. Defaults to 25.
            labels (list, optional): [description]. Defaults to None.
        
        Raises:
            IOError: If no segmentations to be fused are passed
        
        Returns:
            array: a numpy array with the SIMPLE fusion result
        '''
        # manage empty calls
        num = len(candidates)
        if num == 0:
            print('ERROR! No segmentations to fuse.')
            raise IOError('No valid segmentations passed for SIMPLE Fusion')
        if self.verbose:
            print ('Number of segmentations to be fused using SIMPLE is: ', num)
        # handle unpassed weights
        if weights == None:
            weights = itertools.repeat(1,num)
        backup_weights = weights # ugly save to reset weights after each round
        # get unique labels for multi-class fusion
        
        result = np.zeros(candidates[0].shape)
        labels = [2,1,4]
        logging.info('Fusing a segmentation with the labels: {}'.format(labels))
        # loop over each label
        for l in labels:
            if self.verbose:
                print('Currently fusing label {}'.format(l))
            # load first segmentation and use it to create initial numpy arrays IFF it contains labels
            if l == 2:
                # whole tumor
                bin_candidates = [(c > 0).astype(int) for c in candidates]
            elif l == 1: 
                # tumor core
                bin_candidates = [((c == 1) | (c == 4)).astype(int) for c in candidates]
            else: 
                #active tumor
                bin_candidates = [(c == 4).astype(int) for c in candidates]
            if self.verbose:
                print(bin_candidates[0].shape)
            # baseline estimate
            estimate = self.binaryMav(bin_candidates, weights)
            #initial convergence baseline
            conv = np.sum(estimate)
            # check if the estimate was reasonable
            if conv == 0:
                logging.error('Majority Voting in SIMPLE returned an empty array')
                # return np.zeros(candidates[0].shape)
            # reset tau before each iteration
            tau = t
            for i in range(iterations):
                t_weights = [] # temporary weights
                for c in bin_candidates:
                    # score all canidate segmentations
                    t_weights.append((self._score(c, estimate, method)+1)**2) #SQUARED DICE!
                weights = t_weights
                # save maximum score in weights
                max_phi = max(weights)
                # remove dropout estimates
                bin_candidates = [c for c, w in zip(bin_candidates, weights) if (w > t*max_phi)]
                # calculate new estimate
                estimate = self.binaryMav(bin_candidates, weights)
                # increment tau 
                tau = tau+inc
                # check if it converges
                if np.abs(conv-np.sum(estimate)) < stop:
                    if self.verbose: 
                        print('Convergence for label {} after {} iterations reached.'.format(l, i))
                    break
                conv = np.sum(estimate)
            # assign correct label to result
            result[estimate == 1] = l
            # reset weights
            weights = backup_weights
        if self.verbose:
            print('Shape of result:', result.shape)
            print('Shape of current input array:', bin_candidates[0].shape)
            print('Labels and datatype of current output:', result.max(), 
                                                result.min(), result.dtype)
        return result

    def simple(self, candidates, weights=None, t=0.05, stop=25, inc=0.07, method='dice', iterations=25, labels=None):
        '''
        simple implementation using DICE scoring
        Iteratively estimates the accuracy of the segmentations and dynamically assigns weights 
        for the next iteration. Continues for each label until convergence is reached. 

        Args:
            candidates (list): [description]
            weights (list, optional): [description]. Defaults to None.
            t (float, optional): [description]. Defaults to 0.05.
            stop (int, optional): [description]. Defaults to 25.
            inc (float, optional): [description]. Defaults to 0.07.
            method (str, optional): [description]. Defaults to 'dice'.
            iterations (int, optional): [description]. Defaults to 25.
            labels (list, optional): [description]. Defaults to None.
        
        Raises:
            IOError: If no segmentations to be fused are passed
        
        Returns:
            array: a numpy array with the SIMPLE fusion result
        '''
        # manage empty calls
        num = len(candidates)
        if num == 0:
            print('ERROR! No segmentations to fuse.')
            raise IOError('No valid segmentations passed for SIMPLE Fusion')
        if self.verbose:
            print ('Number of segmentations to be fused using SIMPLE is: ', num)
        # handle unpassed weights
        if weights == None:
            weights = itertools.repeat(1,num)
        backup_weights = weights # ugly save to reset weights after each round
        # get unique labels for multi-class fusion
        if labels == None:
            labels = np.unique(candidates[0])
            for c in candidates:
                labels = np.append(labels, np.unique(c))
                print('Labels of current candidate: {}, dtype: {}'.format(np.unique(c), c.dtype))
            labels = np.unique(labels).astype(int)
            logging.warning('No labels passed, choosing those labels automatically: {}'.format(labels))
        result = np.zeros(candidates[0].shape)
        # remove background label
        if 0 in labels:
            labels = np.delete(labels, 0)
        logging.info('Fusing a segmentation with the labels: {}'.format(labels))
        # loop over each label
        for l in sorted(labels):
            if self.verbose:
                print('Currently fusing label {}'.format(l))
            # load first segmentation and use it to create initial numpy arrays IFF it contains labels
            bin_candidates = [(c == l).astype(int) for c in candidates]
            if self.verbose:
                print(bin_candidates[0].shape)
            # baseline estimate
            estimate = self.binaryMav(bin_candidates, weights)
            #initial convergence baseline
            conv = np.sum(estimate)
            # check if the estimate was reasonable
            if conv == 0:
                logging.error('Majority Voting in SIMPLE returned an empty array')
                # return np.zeros(candidates[0].shape)
            # reset tau before each iteration
            tau = t
            for i in range(iterations):
                t_weights = [] # temporary weights
                for c in bin_candidates:
                    # score all canidate segmentations
                    t_weights.append((self._score(c, estimate, method)+1)**2) #SQUARED DICE!
                weights = t_weights
                # save maximum score in weights
                max_phi = max(weights)
                # remove dropout estimates
                bin_candidates = [c for c, w in zip(bin_candidates, weights) if (w > t*max_phi)]
                # calculate new estimate
                estimate = self.binaryMav(bin_candidates, weights)
                # increment tau 
                tau = tau+inc
                # check if it converges
                if np.abs(conv-np.sum(estimate)) < stop:
                    if self.verbose: 
                        print('Convergence for label {} after {} iterations reached.'.format(l, i))
                    break
                conv = np.sum(estimate)
            # assign correct label to result
            result[estimate == 1] = l
            # reset weights
            weights = backup_weights
        if self.verbose:
            print('Shape of result:', result.shape)
            print('Shape of current input array:', bin_candidates[0].shape)
            print('Labels and datatype of current output:', result.max(), 
                                                result.min(), result.dtype)
        return result

    def dirFuse(self, directory, method='mav', outputPath=None, labels=None):
        '''
        dirFuse [summary] 
        
        Args:
            directory ([type]): [description]
            method (str, optional): [description]. Defaults to 'mav'.
            outputName ([type], optional): [description]. Defaults to None.
        '''
        if method == 'all':
            return
        candidates = []
        weights = []
        temp = None
        for file in os.listdir(directory):
            if file.endswith('.nii.gz'):
                # skip existing fusions
                if 'fusion' in file:
                    continue
                temp = op.join(directory, file)
                try:
                    candidates.append(oitk.get_itk_array(oitk.get_itk_image(temp)))
                    weights.append(1)
                    print('Loaded: ' + os.path.join(directory, file))
                except Exception as e:
                    print('Could not load this file: ' + file + ' \nPlease check if this is a valid path and that the files exists. Exception: ' + e)
        if method == 'mav':
            print('Orchestra: Now fusing all .nii.gz files in directory {} using MAJORITY VOTING. For more output, set the -v or --verbose flag or instantiate the fusionator class with verbose=true'.format(directory))
            result = self.mav(candidates, labels, weights)
        elif method == 'simple':
            print('Orchestra: Now fusing all .nii.gz files in directory {} using SIMPLE. For more output, set the -v or --verbose flag or instantiate the fusionator class with verbose=true'.format(directory))
            result = self.simple(candidates, weights)
        elif method == 'brats-simple':
            print('Orchestra: Now fusing all .nii.gz files in directory {} using BRATS-SIMPLE. For more output, set the -v or --verbose flag or instantiate the fusionator class with verbose=true'.format(directory))
            result = self.brats_simple(candidates, weights)
        try:
            if outputPath == None:
                oitk.write_itk_image(oitk.make_itk_image(result, proto_image=oitk.get_itk_image(temp)), op.join(directory, method + '_fusion.nii.gz'))
            else:
                outputDir = op.dirname(outputPath)
                os.makedirs(outputDir, exist_ok=True)
                oitk.write_itk_image(oitk.make_itk_image(result, proto_image=oitk.get_itk_image(temp)), outputPath)
            logging.info('Segmentation Fusion with method {} saved in directory {}.'.format(method, directory))
        except Exception as e:
            print('Very bad, this should also be logged somewhere: ' + str(e))
            logging.exception('Issues while saving the resulting segmentation: {}'.format(str(e)))
    
    def fuse(self, segmentations, outputPath, method='mav', weights=None, labels=None):
        '''
        fuse [summary]
        
        Args:
            segmentations ([type]): [description]
            outputPath ([type]): [description]
            method (str, optional): [description]. Defaults to 'mav'.
            weights ([type], optional): [description]. Defaults to None.
        
        Raises:
            IOError: [description]
        '''
        candidates = []
        if weights is not None: 
            if len(weights) != len(segmentations):
                raise IOError('Please pass a matching number of weights and segmentation files')
            w_weights = weights
        else:
            w_weights = []
        for seg in segmentations:
            if seg.endswith('.nii.gz'):
                try:
                    candidates.append(oitk.get_itk_array(oitk.get_itk_image(seg)))
                    if weights is None:
                        w_weights.append(1)
                    print('Loaded: ' + seg)
                except Exception as e:
                    print('Could not load this file: ' + seg + ' \nPlease check if this is a valid path and that the files exists. Exception: ' + str(e))
                    raise
        if method == 'mav':
            print('Orchestra: Now fusing all passed .nii.gz files using MAJORITY VOTING. For more output, set the -v or --verbose flag or instantiate the fusionator class with verbose=true')
            result = self.mav(candidates, labels=labels, weights=w_weights)
        elif method == 'simple':
            print('Orchestra: Now fusing all passed .nii.gz files in using SIMPLE. For more output, set the -v or --verbose flag or instantiate the fusionator class with verbose=true')
            result = self.simple(candidates, w_weights)
        elif method == 'brats-simple':
            print('Orchestra: Now fusing all .nii.gz files in directory {} using BRATS-SIMPLE. For more output, set the -v or --verbose flag or instantiate the fusionator class with verbose=true')
            result = self.brats_simple(candidates, w_weights)
        try:
            outputDir = op.dirname(outputPath)
            os.makedirs(outputDir, exist_ok=True)
            oitk.write_itk_image(oitk.make_itk_image(result, proto_image=oitk.get_itk_image(seg)), outputPath)
            logging.info('Segmentation Fusion with method {} saved as {}.'.format(method, outputPath))
        except Exception as e:
            print('Very bad, this should also be logged somewhere: ' + str(e))
            logging.exception('Issues while saving the resulting segmentation: {}'.format(str(e)))
    
    def _score(self, seg, gt, method='dice'):
        ''' Calculates a similarity score based on the
        method specified in the parameters
        Input: Numpy arrays to be compared, need to have the 
        same dimensions (shape)
        Default scoring method: DICE coefficient
        method may be:  'dice'
                        'auc'
                        'bdice'
        returns: a score [0,1], 1 for identical inputs
        '''
        try: 
            # True Positive (TP): we predict a label of 1 (positive) and the true label is 1.
            TP = np.sum(np.logical_and(seg == 1, gt == 1))
            # True Negative (TN): we predict a label of 0 (negative) and the true label is 0.
            TN = np.sum(np.logical_and(seg == 0, gt == 0))
            # False Positive (FP): we predict a label of 1 (positive), but the true label is 0.
            FP = np.sum(np.logical_and(seg == 1, gt == 0))
            # False Negative (FN): we predict a label of 0 (negative), but the true label is 1.
            FN = np.sum(np.logical_and(seg == 0, gt == 1))
            FPR = FP/(FP+TN)
            FNR = FN/(FN+TP)
            TPR = TP/(TP+FN)
            TNR = TN/(TN+FP)
        except ValueError:
            print('Value error encountered!')
            return 0
        # faster dice? Oh yeah!
        if method == 'dice':
            # default dice score
            score = 2*TP/(2*TP+FP+FN)
        elif method == 'auc':
            # AUC scoring
            score = 1 - (FPR+FNR)/2
        elif method == 'bdice':
            # biased dice towards false negatives
            score = 2*TP/(2*TP+FN)
        elif method == 'spec':
            #specificity
            score = TN/(TN+FP)
        elif method == 'sens':
            # sensitivity
            score = TP/(TP+FN)
        elif method == 'toterr':
            score = (FN+FP)/(155*240*240)
        elif method == 'ppv':
            prev = np.sum(gt)/(155*240*240)
            temp = TPR*prev
            score = (temp)/(temp + (1-TNR)*(1-prev))
        else:
            score = 0
        if np.isnan(score) or math.isnan(score):
            score = 0
        return score
