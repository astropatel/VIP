#! /usr/bin/env python

"""
Module with the function of merit definitions.
"""

import numpy as np
from .post_proc import get_values_optimize
from ..phot import inject_fcs_cube


def chisquare(modelParameters, cube, angs, plsc, psfs_norm, annulus_width, ncomp, 
              aperture_radius, initialState, cube_ref=None, display=False):
    """
    Calculate the reduced chi2:
    \chi^2_r = \frac{1}{N-3}\sum_{j=1}^{N} |I_j|,
    where N is the number of pixels within a circular aperture centered on the 
    first estimate of the planet position, and I_j the j-th pixel intensity.
    
    Parameters
    ----------    
    modelParameters: tuple
        The model parameters, typically (r, theta, flux).
    cube: numpy.array
        The cube of fits images expressed as a numpy.array.
    angs: numpy.array
        The parallactic angle fits image expressed as a numpy.array. 
    plsc: float
        The platescale, in arcsec per pixel.
    psfs_norm: numpy.array
        The scaled psf expressed as a numpy.array.    
    annulus_width: float
        The width in pixel of the annulus on wich the PCA is performed.
    ncomp: int
        The number of principal components.
    aperture_radius: float
        The radius of the circular aperture.  
    initialState: numpy.array
        The initial guess for the position and the flux of the planet.
    cube_ref : array_like, 3d, optional
        Reference library cube. For Reference Star Differential Imaging.
    display: boolean
        If True, the cube is displayed with ds9.        

    Returns
    -------
    out: float
        The reduced chi squared.
        
    """    
    try:
        r, theta, flux = modelParameters
    except TypeError:
        print('paraVector must be a tuple, {} was given'.format(type(modelParameters)))    
    
    # Create the cube with the fake companing injected
    cube_negfc = inject_fcs_cube(cube, psfs_norm, angs, flevel=-modelParameters[2], 
                                 plsc=plsc, 
                                 rad_arcs=[modelParameters[0]*plsc],
                                 n_branches=1, theta=modelParameters[1])       
                                  
    # Perform PCA to generate the processed image and extract the zone of interest 
    values = get_values_optimize(cube_negfc,angs,ncomp,annulus_width,
                                 aperture_radius,initialState[0],initialState[1], 
                                 display=display, cube_ref=cube_ref)
    
    # Function of merit
    values = np.abs(values)
    chi2 = np.sum(values[values>0])
    N =len(values[values>0])    
    
    return chi2/(N-3)