import visual_clutter as VC
import time

''' FEATURE CONGESTION
Analogy from (Rozenholtz et al, 2007)
You have put an important note
at your colleague's desk for them to read when they get back. How
sure can you be that the note grabs your colleague's attention? It
depends on how much the note stands out to the background clutter (i.e
the rest of the features on the desk). High level of clutter (for example
a lot of other notes and papers cluttering the desk) means the feature space
is congested, and the note will be difficult to see.

--- How to measure feature congestion with Visual Clutter Tool? ---

1. Create a visual_clutter.Vlc class instance.
    Constructor: visual_clutter.Vlc()
    Returns: Vlc object.
    Params:
        - inputImage: Path to the image (only one image at a time unfortunately).
        - numlevels: Number of scales to perform the measurement on (Badly specificed in source code).
        - contrast_filt_sigma, contrast_pool_sigma, color_pool_sigma: Just a few
        filterig parameters (may not be very important to us).

2. Perform the FC measurement.
    Method: Vlc.getClutter_FC()
    Returns:
        - Global clutter of the image (scalar).
        - Map of clutter values for each pixel (np.array of same dimensions as input image).
    Params:
        - p: Miskowski distance of order p (Probably not very important for our project).
        - pix: If an image file should be generated (0: No, 1: Yes).
'''

# PARAMS.
_NUM_LEVELS = 3
_CONT_FILT = 1
_CONT_POOL = 3
_COLOR_POOL = 3
_OUTPUT_TO_IMAGE = 0

# SPECIFY IMAGE PATH HERE. NOTE: You need to add the file locally.
_IMAGE_PATH = ""    # '309.jpg'.

# 1. Make visual clutter object and load test map and set parameters.
clutter_object = VC.Vlc(inputImage=_IMAGE_PATH, numlevels=_NUM_LEVELS,
                        contrast_filt_sigma=_CONT_FILT, contrast_pool_sigma=_CONT_POOL, color_pool_sigma=_COLOR_POOL)

# 2. Perform FC measurement.
time_start = time.time()
global_clutter, local_clutter_map = clutter_object.getClutter_FC(p=1, pix=_OUTPUT_TO_IMAGE)
processing_time = time.time() - time_start

print(f"Feature Congestion calculation time: {processing_time} [s]")
print(f"global_clutter: {global_clutter}")
print("local_clutter_map:")
print(f"\tsize: {local_clutter_map.shape}")
print(f"\tdata: {local_clutter_map}")
