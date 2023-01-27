# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

__version__ = '0.1'
__author__ = 'Christoph Berger'

import errno
import glob
import json
import logging
import os
import os.path as op
import subprocess
import sys
import tempfile

import numpy as np

from . import fusionator
from .util import filemanager as fm
from .util import own_itk as oitk


class Segmentor(object):
    '''
    Now does it all!
    '''

    def __init__(self, config=None, fileformats=None, verbose=True, tty=False, newdocker=True, gpu='0'):
        ''' Init the orchestra class with placeholders
        '''
        self.noOfContainers = 0
        self.config = []
        self.directory = None
        self.verbose = verbose
        self.tty = tty
        self.dockerGPU = newdocker
        self.gpu = gpu
        self.package_directory = op.dirname(op.abspath(__file__))
        # set environment variables to limit GPU usage
        os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'   # see issue #152
        os.environ['CUDA_VISIBLE_DEVICES'] = gpu
        if config is None:
            config = op.join(self.package_directory, 'config', 'dockers.json')
        if fileformats is None:
            self.fileformats = op.join(
                self.package_directory, 'config', 'fileformats.json')
        else:
            self.fileformats = fileformats
        try:
            configfile = open(config, 'r')
            self.config = json.load(configfile)
            self.noOfContainers = len(self.config.keys())
            configfile.close()
        except IOError as e:
            logging.exception(
                'I/O error({0}): {1}'.format(e.errno, e.strerror))
            raise
        except ValueError:
            logging.exception('Invalid configuration file')
            raise
        except:
            logging.exception('Unexpected Error!')
            raise

    def getFileFormat(self, index):
        return self.config[index]['fileformat']

    def getContainerName(self, index):
        return self.config[index]['name']

    def getNumberOfContainers(self):
        return len(self.config)

    def runDummyContainer(self, stop=False):
        command = 'docker run --rm -it hello-world'
        subprocess.check_call(command, shell=True)

    def runContainer(self, id, directory, outputDir, outputName):
        '''
        Runs one container on one patient folder
        '''
        logging.info(
            'Now running a segmentation with the Docker {}.'.format(id))
        logging.info('Output will be in {}.'.format(outputDir))

        params = self.config[id]  # only references, doesn't copy
        command = 'docker run --rm'
        # assemble the rest of the command
        flags = params.get('flags', '')
        # check if we need to map the user
        if params.get('user_mode', False):
            user_flags = '--user $(id -u):$(id -g)'
        else:
            user_flags = ''
        # assemble the gpu flags if needed
        if params['runtime'] == 'nvidia':
            if self.dockerGPU:
                # TODO clean this up
                gpu_flags = '--gpus device=' + str(self.gpu)
            else:
                gpu_flags = '--runtime=nvidia -e CUDA_VISIBLE_DEVICES=' + \
                    str(self.gpu)
        else:
            gpu_flags = ''
        # assemble directory mapping
        volume = '-v ' + str(directory) + ':' + str(params['mountpoint'])
        # assemble execution command
        call = str(params['command'])

        # stick everything together
        command = command + ' ' + user_flags + ' ' + gpu_flags + ' ' + \
            flags + ' ' + volume + ' ' + params['id'] + ' ' + call

        if self.verbose:
            print('Executing: {}'.format(command))
        try:
            with open(op.join(outputDir, '{}_output.log'.format(outputName.split('.')[0])), 'w') as f:
                subprocess.check_call(command, shell=True, stdout=f)
        except Exception as e:
            logging.error(
                'Segmentation failed for case {} with error: {}'.format(directory, e))
            if 'exit status 125' in str(e):
                logging.error(
                    'DOCKER DAEMON not running! Please start your Docker runtime.')
                sys.exit(125)
            return False
        if self.verbose:
            logging.info('Container exited without error')
        # fileh.close()
        return True

    def runIterate(self, dir, cid):
        ''' Iterates over a directory and runs the segmentation on each patient found
        '''
        logging.info('Looking for BRATS data directories..')
        for fn in os.listdir(dir):
            if not os.path.isdir(os.path.join(dir, fn)):
                continue  # Not a directory
            if 'DE_RI' in fn:
                logging.info('Found pat data: {}'.format(fn))
                try:
                    os.makedirs(os.path.join(os.path.join(dir, fn),
                                             'results'))
                except OSError as err:
                    if err.errno != errno.EEXIST:
                        raise
                logging.info('Calling Container: {}'.format(cid))
                if not self.runContainer(cid, os.path.join(dir, fn), dir):
                    logging.info(
                        'ERROR: Run failed for patient {} with container {}'.format(fn, cid))
                    return False
                # TODO: rename folder and prepend pat_id
                # rename_folder(img_id, os.path.join(directory, fn), fn)
        return True

    def multiSegment(self, tempDir, inputs, method, outputName, outputDir):
        '''
        multiSegment [summary]

        Args:
            tempDir ([type]): [description]
            inputs ([type]): [description]
            method ([type]): [description]
            outputName ([type]): [description]
            outputDir ([type]): [description]
        '''
        logging.debug('CALLED MULTISEGMENT')
        fusion = fusionator.Fusionator()
        for cid in self.config.keys():
            # replace this with a call to single-segment
            logging.info('[Orchestra] Segmenting with ' + cid)
            ff = self._format(self.getFileFormat(cid), self.fileformats)
            for key, img in inputs.items():
                savepath = op.join(tempDir, ff[key])
                img = oitk.get_itk_image(img)
                if self.verbose:
                    logging.info(
                        '[Weborchestra][Info] Writing to path {}'.format(savepath))
                oitk.write_itk_image(img, savepath)
            if self.verbose:
                logging.info('[Weborchestra][Info] Images saved correctly')
                logging.info(
                    '[Weborchestra][Info] Starting the Segmentation with container {} now'.format(cid))

            status = self.runContainer(cid, tempDir, outputDir)
            status = self.runContainer(cid, tempDir, outputDir, outputName)
            if status:
                if self.verbose:
                    logging.info('[Weborchestra][Success] Segmentation saved')
                resultsDir = op.join(tempDir, 'results/')
                saveLocation = op.join(outputDir, cid + '_tumor_seg.nii.gz')
                self._handleResult(cid, resultsDir, outputPath=saveLocation)
            else:
                logging.exception(
                    'Container run for CID {} failed!'.format(cid))
        fusion.dirFuse(outputDir, method=method,
                       outputPath=op.join(outputDir, outputName))

    def singleSegment(self, tempDir, inputs, cid, outputName, outputDir):
        '''
        singleSegment [summary]

        Args:
            tempDir ([type]): [description]
            inputs ([type]): [description]
            cid ([type]): [description]
            outputName ([type]): [description]
            outputDir ([type]): [description]
        '''
        ff = self._format(self.getFileFormat(cid), self.fileformats)
        for key, img in inputs.items():
            savepath = op.join(tempDir, ff[key])
            img = oitk.get_itk_image(img)
            if self.verbose:
                logging.info(
                    '[Weborchestra][Info] Writing to path {}'.format(savepath))
            oitk.write_itk_image(img, savepath)
        if self.verbose:
            logging.info('[Weborchestra][Info] Images saved correctly')
            logging.info(
                '[Weborchestra][Info] Starting the Segmentation with {} now'.format(cid))
        status = self.runContainer(cid, tempDir, outputDir, outputName)
        if status:
            if self.verbose:
                logging.info('[Weborchestra][Success] Segmentation saved')
            resultsDir = op.join(tempDir, 'results/')
            self._handleResult(
                cid, resultsDir, outputPath=op.join(outputDir, outputName))
            # delete tmp directory if result was saved elsewhere
        else:
            logging.error(
                '[Weborchestra][Error] Segmentation failed, see output!')

    def segment(self, t1=None, t1c=None, t2=None, fla=None, cid='mocker', outputPath=None):
        '''
        segment [summary]

        Args:
            t1 ([type], optional): [description]. Defaults to None.
            t1c ([type], optional): [description]. Defaults to None.
            t2 ([type], optional): [description]. Defaults to None.
            fla ([type], optional): [description]. Defaults to None.
            cid (str, optional): [description]. Defaults to 'mocker'.
            outputPath ([type], optional): [description]. Defaults to None.
        '''
        # Call output method here
        outputName, outputDir = self._whereDoesTheFileGo(outputPath, t1, cid)
        # set up logging (for all internal functions)
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=op.join(
            outputDir, 'segmentor_high_level.log'), level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler())
        logging.debug('DIRNAME is: ' + outputDir)
        logging.debug('FILENAME is: ' + outputName)
        logging.info(
            'Now running a new set of segmentations on input: {}'.format(op.dirname(t1)))
        # switch between
        inputs = {'t1': t1, 't2': t2, 't1c': t1c, 'fla': fla}
        # create temporary directory for storage
        storage = tempfile.TemporaryDirectory(dir=self.package_directory)
        # TODO this is a potential security hazzard as all users can access the files now, but currently it seems the only way to deal with bad configured docker installations
        os.chmod(storage.name, 0o777)
        tempDir = op.abspath(storage.name)
        resultsDir = op.join(tempDir, 'results')
        os.mkdir(resultsDir)
        # TODO this is a potential security hazzard as all users can access the files now, but currently it seems the only way to deal with bad configured docker installations
        os.chmod(resultsDir, 0o777)
        logging.debug(tempDir)
        logging.debug(resultsDir)

        if cid == 'mav' or cid == 'simple' or cid == 'all':
            # segment with all containers
            logging.info('Called singleSegment with method: ' + cid)
            self.multiSegment(tempDir, inputs, cid, outputName, outputDir)
        else:
            # segment only with a single container
            logging.info('Called singleSegment with docker: ' + cid)
            self.singleSegment(tempDir, inputs, cid, outputName, outputDir)

    ### Private utility methods below ###

    def _whereDoesTheFileGo(self, outputPath, t1path, cid):
        if outputPath is None:
            outputDir = op.join(op.dirname(t1path), 'output')
            outputName = cid + '_segmentation.nii.gz'
        elif outputPath.endswith('.nii.gz'):
            if '~' in outputPath:
                outputPath = op.expanduser(outputPath)
            # valid filename
            outputDir = op.dirname(outputPath)
            outputName = op.basename(outputPath)
            # if only a filename is passed, use the t1 directory
            if outputDir == '':
                outputDir = op.join(op.dirname(t1path), 'output')
        else:
            outputDir = outputName = None

        if outputDir is None or outputName is None:
            raise ValueError('The outputPath is ambiguous and cannot be determined! path: {}, t1path: {}, cid: {}'.format(
                outputPath, t1path, cid))
        # build abspaths:
        outputDir = op.abspath(outputDir)
        try:
            os.makedirs(outputDir, exist_ok=True)
        except Exception as e:
            print('could not create target directory: {}'.format(outputDir))
            raise e
        return outputName, outputDir

    def _handleResult(self, cid, directory, outputPath):
        '''
        This function handles the copying and renaming of the
        Segmentation result before returning
        '''
        # Todo: Find segmentation result
        contents = glob.glob(
            op.join(directory, 'tumor_' + cid + '_class.nii*'))
        if len(contents) == 0:
            contents = glob.glob(op.join(directory, 'tumor_*_class.nii*'))
        if len(contents) == 0:
            contents = glob.glob(op.join(directory, cid + '*.nii*'))
        if len(contents) == 0:
            contents = glob.glob(op.join(directory, '*tumor*.nii*'))
        if len(contents) < 1:
            logging.error(
                '[Weborchestra - Filehandling][Error] No segmentation saved, the container run has most likely failed.')
        elif len(contents) > 1:
            logging.warning(
                '[Weborchestra - Filehandling][Warning] Multiple Segmentations found')
            print('found files: {}'.format(contents))
            img = oitk.get_itk_image(contents[0])
            labels = 0
            exportImg = None
            for _, c in enumerate(contents):
                img = oitk.get_itk_image(c)
                if labels < len(np.unique(oitk.get_itk_array(img))):
                    exportImg = img
                    labels = len(np.unique(oitk.get_itk_array(img)))
            oitk.write_itk_image(exportImg, op.join(outputPath))
            logging.warning(
                '[Weborchestra - Filehandling][Warning] Segmentation with most labels ({}) for cid {} saved'.format(labels, cid))
            return
        img = oitk.get_itk_image(contents[0])
        for c in contents:
            os.remove(op.join(directory, c))
        oitk.write_itk_image(img, outputPath)

    def _format(self, fileformat, configpath, verbose=True):
        # load fileformat for a given container
        try:
            configfile = open(op.abspath(configpath), 'r')
            config = json.load(configfile)
            configfile.close()
        except IOError as e:
            logging.exception(
                'I/O error({0}): {1}'.format(e.errno, e.strerror))
            raise
        except ValueError:
            logging.exception('Invalid configuration file')
            raise
        except:
            logging.exception('Unexpected Error!')
            raise
        logging.info('[Weborchestra][Success]Loaded fileformat: {}'.format(
            config[fileformat]))
        return config[fileformat]
