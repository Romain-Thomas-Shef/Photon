'''
The photon project
-------------------
This is the file that make the ds9 zscale algorithm
in python.

@author: ?
@year: 2016
@place: STScI, https://trac.stsci.edu/ssb/stsci_python/browser/stsci_python/branches/setup_refactoring/numdisplay/lib/zscale.py?rev=12607
@License: ? (MIT is assumed)
'''


####Python libraries
from __future__ import division # confidence high
import numpy
import math


#-----------------------------
class zscale_algo:
    '''
    zscale algorithm to make ds9-like zscale plots
    '''

    def __init__(self,MAX_REJECT =0.5,MIN_NPIXELS=5,\
            GOOD_PIXEL=0,BAD_PIXEL=1,KREJ=2.5,MAX_ITERATIONS=5):
        '''
        Class intiailisation define the attributes
        '''
        ###
        self.MAX_REJECT  = MAX_REJECT 
        self.MIN_NPIXELS = MIN_NPIXELS
        self.GOOD_PIXEL = GOOD_PIXEL
        self.BAD_PIXEL = BAD_PIXEL
        self.KREJ = KREJ
        self.MAX_ITERATIONS = MAX_ITERATIONS



    def zscale(self,image, nsamples=1000, contrast=0.25, bpmask=None, zmask=None):
        """Implement IRAF zscale algorithm
        nsamples=1000 and contrast=0.25 are the IRAF display task defaults
        bpmask and zmask not implemented yet
        image is a 2-d numpy array
        returns (z1, z2)
        """
        # Sample the image
        samples = self.zsc_sample(image, nsamples, bpmask, zmask)
        npix = len(samples)
        samples.sort()
        zmin = samples[0]
        zmax = samples[-1]
        # For a zero-indexed array
        center_pixel = (npix - 1) // 2
        if npix%2 == 1:
	        median = samples[center_pixel]
        else:
	        median = 0.5 * (samples[center_pixel] + samples[center_pixel + 1])
        #
        # Fit a line to the sorted array of samples
        minpix = max(self.MIN_NPIXELS, int(npix * self.MAX_REJECT ))
        ngrow = max (1, int (npix * 0.01))
        ngoodpix, zstart, zslope = self.zsc_fit_line(samples, npix, self.KREJ, ngrow,
		                                 self.MAX_ITERATIONS)
        if ngoodpix < minpix:
            z1 = zmin
            z2 = zmax
        else:
            if contrast > 0: zslope = zslope / contrast
            z1 = max (zmin, median - (center_pixel - 1) * zslope)
            z2 = min (zmax, median + (npix - center_pixel) * zslope)
        return z1, z2
    def zsc_sample(self, image, maxpix, bpmask=None, zmask=None):
       
        # Figure out which pixels to use for the zscale algorithm
        # Returns the 1-d array samples
        # Don't worry about the bad pixel mask or zmask for the moment
        # Sample in a square grid, and return the first maxpix in the sample
        nc = image.shape[0]
        nl = image.shape[1]
        stride = max (1.0, math.sqrt((nc - 1) * (nl - 1) / float(maxpix)))
        stride = int (stride)
        samples = image[::stride,::stride].flatten()
        return samples[:maxpix]
       
    def zsc_fit_line(self,samples, npix, KREJ, ngrow, maxiter):
        #
        # First re-map indices from -1.0 to 1.0
        xscale = 2.0 / (npix - 1)
        xnorm = numpy.arange(npix)
        xnorm = xnorm * xscale - 1.0
        ngoodpix = npix
        minpix = max (self.MIN_NPIXELS, int (npix*self.MAX_REJECT ))
        last_ngoodpix = npix + 1
        # This is the mask used in k-sigma clipping.  0 is good, 1 is bad
        badpix = numpy.zeros(npix, dtype="int32")
        #
        #  Iterate
        for niter in range(maxiter):
            if (ngoodpix >= last_ngoodpix) or (ngoodpix < minpix):
                break
            # Accumulate sums to calculate straight line fit
            goodpixels = numpy.where(badpix == self.GOOD_PIXEL)
            sumx = xnorm[goodpixels].sum()
            sumxx = (xnorm[goodpixels]*xnorm[goodpixels]).sum()
            sumxy = (xnorm[goodpixels]*samples[goodpixels]).sum()
            sumy = samples[goodpixels].sum()
            sum = len(goodpixels[0])
            delta = sum * sumxx - sumx * sumx
            # Slope and intercept
            intercept = (sumxx * sumy - sumx * sumxy) / delta
            slope = (sum * sumxy - sumx * sumy) / delta
            # Subtract fitted line from the data array
            fitted = xnorm*slope + intercept
            flat = samples - fitted
            # Compute the k-sigma rejection threshold
            ngoodpix, mean, sigma = self.zsc_compute_sigma(flat, badpix, npix)
            threshold = sigma * self.KREJ
            # Detect and reject pixels further than k*sigma from the fitted lin
            lcut = -threshold
            hcut = threshold
            below = numpy.where(flat < lcut)
            above = numpy.where(flat > hcut)
            badpix[below] = self.BAD_PIXEL
            badpix[above] = self.BAD_PIXEL

            # Convolve with a kernel of length ngrow
            kernel = numpy.ones(ngrow,dtype="int32")
            badpix = numpy.convolve(badpix, kernel, mode='same')
            ngoodpix = len(numpy.where(badpix == self.GOOD_PIXEL)[0])
            niter += 1
        # Transform the line coefficients back to the X range [0:npix-1]
        zstart = intercept - slope
        zslope = slope * xscale
        return ngoodpix, zstart, zslope
    
    def zsc_compute_sigma(self,flat, badpix, npix):
        # Compute the rms deviation from the mean of a flattened array.
        # Ignore rejected pixels
        # Accumulate sum and sum of squares
        goodpixels = numpy.where(badpix == self.GOOD_PIXEL)
        sumz = flat[goodpixels].sum()
        sumsq = (flat[goodpixels]*flat[goodpixels]).sum()
        ngoodpix = len(goodpixels[0])
        if ngoodpix == 0:
            mean = None
            sigma = None
        elif ngoodpix == 1:
            mean = sumz
            sigma = None
        else:
            mean = sumz / ngoodpix
            temp = sumsq / (ngoodpix - 1) - sumz*sumz / (ngoodpix * (ngoodpix - 1))
            if temp < 0:
                sigma = 0.0
            else:
                sigma = math.sqrt (temp)
        return ngoodpix, mean, sigma








