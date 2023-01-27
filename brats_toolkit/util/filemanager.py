#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module containing functions to manage the BRATS files

"""
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

import os
import numpy as np
import glob
import shutil
import fnmatch
from . import own_itk as oitk

modalities = ['fla','t1','t1c','t2']

def bratsNormalize(image=None, bm=None, bias=0.0001):
    '''
    Provides normalization of BRATS images to the
    intensity interval 0...1 and ensures that the background is
    entirely 0
    The bias value ensures that no brain voxel becomes 0
    '''
    if bm is None or image is None:
        print('[Normalize][Error] You have to pass an image and a corresponding brain mask!')
        return None
    if bm.shape != image.shape:
        print('[Normalize][Error] Your image and mask dimensions don\'t match!')
        return None
    # set bg to zero before calculating anything
    image = np.multiply(image,bm)
    # shift range to 0...x
    image = image - image.min()
    # add bias value to avoid 0 voxels
    image += bias
    # adjust range to bias...1
    image = np.divide(image, image.max())
    # nultiply with mask again to get a bg of 0
    image = np.multiply(image, bm)
    return image

def loadGT(path, patid, file='gt.nii.gz', verbose=True):
    """ Loads the Ground Truth for a specified patient
    from a given Ground Truth root directory
    In:     dir, path to the GT folder
            patid, patient ID
            verbose: True/False terminal output
    Out:    itk image! -> convert to numpy array
    """
    for directory in os.listdir(path):
        if not os.path.isdir(os.path.join(path, directory)):
            continue # Not a directory
        if patid == directory:
            if verbose:
                print('Loading GT for Patient', patid, 'now..')
            patpath = os.path.join(path, patid)
            #TODO change loading to support GT for different methods
            groundtruth = oitk.get_itk_image(os.path.join(patpath, file))
            break
    return groundtruth

def convertLabels(originalFile, oldlabels, newlabels=[0,1,2,4]):
    proto_img = oitk.get_itk_image(originalFile)
    labelfile = oitk.get_itk_array(proto_img)
    # segm_im = oitk.make_itk_image(proto_image, proto_image)
    converted = np.zeros(labelfile.shape)
    for oldlabel, newlabel in zip(oldlabels, newlabels):
        converted[labelfile == oldlabel] = newlabel
    oitk.write_itk_image(oitk.make_itk_image(converted, proto_img), originalFile)

def fileFinder(srcPath, filetofind, func=convertLabels, verbose=True):
    """ finds a file starting from the source path in subdirectories
    and runs an arbitrary function on them
    """
    if verbose:
        print(srcPath)
        print(filetofind)
    for filename in glob.iglob(srcPath+'/**/'+filetofind, recursive=True):
        func(filename, [0,1,2,4], [0,2,1,4])

def touchAndConvert(originalFile, gt, verbose=True):
    """ Loads the ITK image and saves it with proper
    header data (and conversion to 8-bit unint)
    """
    proto_img = oitk.get_itk_image(originalFile)
    labelfile = oitk.get_itk_array(proto_img)
    segm_img = oitk.make_itk_image(labelfile, gt)
    oitk.write_itk_image(segm_img, originalFile)

def fileIterator(directory, gt_root, verbose=True):
    for patient in os.listdir(directory):
        patpath = os.path.join(directory, patient)
        if not os.path.isdir(patpath):
            continue # Not a directory
        if 'brats' in patient:
            #loads itk ground truth
            gt = loadGT(gt_root, patient, file='gt.nii')
            if verbose:
                print ('Current patient:', patient)
            # loop through patient folder
            for result in os.listdir(patpath):
                if not os.path.isdir(os.path.join(patpath, result)):
                    continue # Not a directory
                respath = os.path.join(patpath, result)
                paths = os.listdir(respath)
                for result in paths:
                    # if there is a results file, run the conversion
                    if fnmatch.fnmatch(result, '*.nii*'):
                        if verbose:
                            print('Will convert the following file:', result)
                        touchAndConvert(os.path.join(respath, result), gt, True)

def remove_nii(root):
    for fn in os.listdir(root):
        if not os.path.isdir(os.path.join(root, fn)):
            continue # Not a directory
        if 'brats' in fn:
            files = os.listdir(os.path.join(root, fn))
            subdir = os.path.join(root, fn)
            for file in files:
                if file+'.nii' in modalities:
                    os.remove(os.path.join(subdir, file+'.nii'))

def create_files(root, gz=False):
    # create nii.gz versions from nii for compatibility
    print(root)
    for fn in os.listdir(root):
        if not os.path.isdir(os.path.join(root, fn)):
            continue # Not a directory
        if 'brats' in fn:
            # files = os.listdir(os.path.join(root, fn))
            for file in modalities:
                path = os.path.join(os.path.join(root, fn), file)
                proto_image = oitk.get_itk_image(path+str('.nii'))
                # segm_im = oitk.make_itk_image(proto_image, proto_image)
                oitk.write_itk_image(proto_image, path+str('.nii.gz'))

def clean(root, gz=False, dir=False):
    """ Removes all subfolders and leaves only .nii and .nii.gz input
    files untouched
    root: path to folder with subfolers
    gz: If True, compressed Nifti files are also removed
    """
    # Remove subfolders
    for fn in os.listdir(root):
        subdir = os.path.join(root, fn)
        if not os.path.isdir(subdir):
            continue
        for file in os.listdir(subdir):
            if dir and os.path.isdir(os.path.join(subdir, file)):
                shutil.rmtree(os.path.join(subdir, file))
            if gz and '.nii.gz' in file:
                os.remove(os.path.join(subdir, file))

def validate_files(root):
    """ Checks if all input directories contain the right files
    """
    print('Looking for BRATS data directory..')
    for fn in os.listdir(root):
        if not os.path.isdir(os.path.join(root, fn)):
            continue # Not a directory
        if 'brats' in fn:
            print('Found pat data:', fn)
            print('Checking data validity now')
            files = os.listdir(os.path.join(root, fn))
            if not set(modalities).issubset(files):
                print('Not all required files are present!')
                return False
    print('File check okay!')
    return True

def rename_flair(root):
    """ Renames flair.nii files to fla.nii if required
    """
    for fn in os.listdir(root):
        if not os.path.isdir(os.path.join(root, fn)):
            continue # Not a directory
        if 'brats' in fn:
            files = os.listdir(os.path.join(root, fn))
            subdir = os.path.join(root, fn)
            for file in files:
                if 'flair' in file:
                    os.rename(os.path.join(subdir, file),
                    os.path.join(subdir, file.replace('flair', 'fla')))

def rename_fla(root):
    """ Renames fla.nii files to flair.nii if required
    """
    for fn in os.listdir(root):
        if not os.path.isdir(os.path.join(root, fn)):
            continue # Not a directory
        if 'brats' in fn:
            files = os.listdir(os.path.join(root, fn))
            subdir = os.path.join(root, fn)
            for file in files:
                if 'fla.nii' == file:
                    os.rename(os.path.join(subdir, file),
                    os.path.join(subdir,
                    file.replace('fla.nii', 'flair.nii')))
                if 'fla.nii.gz' == file:
                    os.rename(os.path.join(subdir, file),
                    os.path.join(subdir,
                    file.replace('fla.nii.gz', 'flair.nii.gz')))

def reduce_filesize(root, gz=False):
    # create nii.gz versions from nii for compatibility
    for fn in os.listdir(root):
        if not os.path.isdir(os.path.join(root, fn)):
            continue # Not a directory
        if 'brats' in fn:
            # files = os.listdir(os.path.join(root, fn))
            for file in modalities:
                path = os.path.join(os.path.join(root, fn), file)
                proto_image = oitk.get_itk_image(path+str('.nii'))
                # segm_im = oitk.make_itk_image(proto_image, proto_image)
                oitk.write_itk_image(proto_image, path+str('.nii.gz'))

def completeclean(root):
    # maybe remove the root-results folder as well
    clean(root, False, True)

def conversion(segmentations, verbose=True):
    gt_root = '/Users/christoph/Documents/Uni/Bachelorarbeit/Testdaten/testing_nii_LABELS'
    #segmentations = '/Users/christoph/Documents/Uni/Bachelorarbeit/Testdaten/Complete_Results'
    fileIterator(segmentations, gt_root)
