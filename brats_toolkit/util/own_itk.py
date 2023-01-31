# -*- coding: UTF-8 -*-
"""Module containing functions enabling to read, make and
write ITK images.

"""
__version__ = '0.2'
__author__ = 'Esther Alberts'

import os
import numpy as np
import SimpleITK as itk

def reduce_arr_dtype(arr, verbose=False):
    """ Change arr.dtype to a more memory-efficient dtype, without changing
    any element in arr. """
    
    if np.all(arr-np.asarray(arr,'uint8') == 0):
        if arr.dtype != 'uint8':
            if verbose:
                print('Converting '+str(arr.dtype)+' to uint8 np.ndarray')
            arr = np.asarray(arr, dtype='uint8')
    elif np.all(arr-np.asarray(arr,'int8') == 0):
        if arr.dtype != 'int8':
            if verbose:
                print('Converting '+str(arr.dtype)+' to int8 np.ndarray')
            arr = np.asarray(arr, dtype='int8')
    elif np.all(arr-np.asarray(arr,'uint16') == 0):
        if arr.dtype != 'uint16':
            if verbose:
                print('Converting '+str(arr.dtype)+' to uint16 np.ndarray')
            arr = np.asarray(arr, dtype='uint16')
    elif np.all(arr-np.asarray(arr,'int16') == 0):
        if arr.dtype != 'int16':
            if verbose:
                print('Converting '+str(arr.dtype)+' to int16 np.ndarray')
            arr = np.asarray(arr, dtype='int16')
    
    return arr

def make_itk_image(arr, proto_image=None, verbose=True):
    """Create an itk image given an image array.

    Parameters
    ----------
    arr : ndarray
        Array to create an itk image with.
    proto_image : itk image, optional
        Proto itk image to provide Origin, Spacing and Direction.

    Returns
    -------
    image : itk image
        The itk image containing the input array `arr`.

    """
    
    arr = reduce_arr_dtype(arr, verbose=verbose)

    image = itk.GetImageFromArray(arr)
    if proto_image != None:
        image.CopyInformation(proto_image)

    return image

def write_itk_image(image, path):
    """Write an itk image to a path.

    Parameters
    ----------
    image : itk image or np.ndarray
        Image to be written.
    path : str
        Path where the image should be written to.

    """

    if isinstance(image, np.ndarray):
        image = make_itk_image(image)

    writer = itk.ImageFileWriter()
    writer.SetFileName(path)

    if os.path.splitext(path)[1] == '.nii':
        Warning('You are converting nii, ' + \
                'be careful with type conversions')

    writer.Execute(image)

def get_itk_image(path_or_image):
    """Get an itk image given a path.

    Parameters
    ----------
    path : str or itk.Image
        Path pointing to an image file with extension among
        *TIFF, JPEG, PNG, BMP, DICOM, GIPL, Bio-Rad, LSM, Nifti (.nii and .nii.gz), 
        Analyze, SDT/SPR (Stimulate), Nrrd or VTK images*.

    Returns
    -------
    image : itk image
        The itk image.

    """
    if isinstance(path_or_image, itk.Image):
        return path_or_image

    if not os.path.exists(path_or_image):
        err = path_or_image + ' doesnt exist'
        raise AttributeError(err)

    reader = itk.ImageFileReader()
    reader.SetFileName(path_or_image)

    image = reader.Execute()

    return image

def get_itk_array(path_or_image):
    """ Get an image array given a path or itk image.

    Parameters
    ----------
    path_or_image : str or itk image
        Path pointing to an image file with extension among
        *TIFF, JPEG, PNG, BMP, DICOM, GIPL, Bio-Rad, LSM, Nifti (.nii and .nii.gz), 
        Analyze, SDT/SPR (Stimulate), Nrrd or VTK images* or an itk image.

    Returns
    -------
    arr : ndarray
        Image ndarray contained in the given path or the itk image.

    """

    if isinstance(path_or_image, np.ndarray):
        return path_or_image

    elif isinstance(path_or_image, str):
        image = get_itk_image(path_or_image)

    elif isinstance(path_or_image, itk.Image):
        image = path_or_image

    else:
        err = 'Image type not recognized: ' + str(type(path_or_image))
        raise RuntimeError(err)

    arr = itk.GetArrayFromImage(image)

    return arr

def copy_image_info(input_path, ref_path):
    """ Copy origin, direction and spacing information from ref_path 
    into the header in input_path. """
    
    print('OVerwriting '+input_path[-50:])
    
    ref_im = get_itk_image(ref_path)
    im = get_itk_image(input_path)
    
    dim = im.GetSize()
    if dim != ref_im.GetSize():
        err = 'Images are not of same dimension, I will not copy image info!'
        raise RuntimeError(err)
    
    im.SetOrigin(ref_im.GetOrigin())
    im.SetDirection(ref_im.GetDirection())
    im.SetSpacing(ref_im.GetSpacing())
    
    if im.GetSize() != dim:
        err = 'Dimension changed during copying image info: aborting'
        raise RuntimeError(err)
    
    write_itk_image(im, input_path)
    
def load_arr_from_paths(paths):
    """ For every str in paths (paths can consis of nested lists),
    load the image at this path. If any str is not a path, an error
    is thrown. All other objects are preserved. """
    
    if isinstance(paths, str):
        im_arrs = get_itk_array(paths)
    elif isinstance(paths, (list, tuple)):
        for i, sub_paths in enumerate(paths):
            paths[i] = load_arr_from_paths(sub_paths)
        im_arrs = paths
    else:
        im_arrs = paths
        
    return im_arrs

def get_itk_data(path_or_image, verbose=False):
    """Get the image array, image size and pixel dimensions given an itk
    image or a path.

    Parameters
    ----------
    path_or_image : str or itk image
        Path pointing to an image file with extension among
        *TIFF, JPEG, PNG, BMP, DICOM, GIPL, Bio-Rad, LSM, Nifti (.nii and .nii.gz), 
        Analyze, SDT/SPR (Stimulate), Nrrd or VTK images* or an itk image.
    verbose : boolean, optional
        If true, print image shape, spacing and data type of the image
        corresponding to `path_or_image.`

    Returns
    -------
    arr : ndarray
        Image array contained in the given path or the itk image.
    shape : tuple
        Shape of the image array contained in the given path or the itk
        image.
    spacing : tuple
        Pixel spacing (resolution) of the image array contained in the
        given path or the itk image.

    """

    if isinstance(path_or_image, np.ndarray):
        arr = path_or_image
        spacing = None
    else:
        if isinstance(path_or_image, str):
            image = get_itk_image(path_or_image)
        else:
            image = path_or_image
        arr = itk.GetArrayFromImage(image)
        spacing = image.GetSpacing()[::-1]

    shape = arr.shape
    data_type = arr.dtype

    if verbose:

        print('\t image shape: ' + str(shape))
        print('\t image spacing: ' + str(spacing))
        print('\t image data type: ' + str(data_type))

    return arr, shape, spacing

def read_dicom(source_path, verbose=True):
    '''Reads dicom series into an itk image.

    Parameters
    ----------
    source_path : string
        path to directory containing dicom series.
    verbose : boolean
        print out all series file names.

    Returns
    -------
    image : itk image
        image volume.
    '''

    reader = itk.ImageSeriesReader()
    names = reader.GetGDCMSeriesFileNames(source_path)
    if len(names) < 1:
        raise IOError('No Series can be found at the specified path!')
    elif verbose:
        print('image series with %d dicom files found in : %s' \
                % (len(names), source_path[-50:]))
    reader.SetFileNames(names)
    image = reader.Execute()
    if verbose:
        get_itk_data(image, verbose=True)

    return image
