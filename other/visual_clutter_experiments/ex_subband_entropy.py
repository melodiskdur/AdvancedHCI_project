import visual_clutter as VC
import time

''' SUBBAND ENTROPY
Definition: How much redundancy there is in different frequency
subbands of a scene. Essentially this means: How many bits do
we need to encode all the information of a subband? With lots of structure
and repetitions: fewer bits (low entropy). With no structure and repetitions:
more bits (high entropy).

Subband I think refers to orientations and spatial features rather than color wavelengths.

--- How to measure Subband Entropy with Visual Clutter Tool? ---

1. Create a visual_clutter.Vlc class instance.
    Constructor: visual_clutter.Vlc()
    Returns: Vlc object.
    Params:
        - inputImage: Path to the image (only one image at a time unfortunately).
        - numlevels: Number of scales to perform the measurement on (badly specificed in source code).
        - contrast_filt_sigma, contrast_pool_sigma, color_pool_sigma: Just a few
        filterig parameters (may not be very important to us).

2. Perform the SE measurement.
    Method: Vlc.getClutter_SE()
    Returns:
        - Subband entropy of the image (scalar).
    Params:
        - wlevels: Number of scales (badly specified in source code).
        - wght_chrom: Chrominance weight (may not be very important to us).
'''

# PARAMS.
_NUM_LEVELS = 3
_CONT_FILT = 1
_CONT_POOL = 3
_COLOR_POOL = 3

# SPECIFY IMAGE PATH HERE. NOTE: You need to add the file locally.
_IMAGE_PATH = ""    # '309.jpg'.

# 1. Make visual clutter object and load test map and set parameters.
clutter_object = VC.Vlc(inputImage=_IMAGE_PATH, numlevels=_NUM_LEVELS,
                        contrast_filt_sigma=_CONT_FILT, contrast_pool_sigma=_CONT_POOL, color_pool_sigma=_COLOR_POOL)

# 2. Perform FC measurement.
time_start = time.time()
clutter_se = clutter_object.getClutter_SE(wlevels=_NUM_LEVELS)
processing_time = time.time() - time_start

print(f"Subband Entropy calculation time: {processing_time} [s]")
print(f"clutter_se: {clutter_se}")
