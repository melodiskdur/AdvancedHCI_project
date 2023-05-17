import visual_clutter as VC
import numpy as np
from PIL import Image

''' Example on using a PIL image object rather than
loading an image directly from a path-string.

STEPS.

1. Read full image into a PIL.Image object.
2. Use Image.crop() to create segmented images.
3. Convert segmented image to MxNx3 nd-array by using np.array(img).
4. Load the segmented image into a visual_clutter.Vlc object.
5. Done! Now we can perform visual clutter on part of the image.

'''

# CLUTTER PARAMS.
_NUM_LEVELS = 3
_CONT_FILT = 1
_CONT_POOL = 3
_COLOR_POOL = 3
_OUTPUT_TO_IMAGE = 0

# IMAGE PARAMTERS & VARIABLES.
_IMAGE_PATH = "" # "309.jpg"
full_image = Image.open(_IMAGE_PATH)
width, height = full_image.size
# Sub-boxes of the original image.
boxes = {'UL': (0, 0, width // 2, height // 2),                     # Upper-Left.
         'UR': (1 + width//2, 0, width, height // 2),               # Etc...
         'LL': (0, 1 + height // 2, width // 2, height),
         'LR': (1 + width // 2, 1 + height // 2, width, height)}

# Use Image.crop() to create new images.
UL = full_image.crop(box=boxes['UL'])           # Upper-Left
UR = full_image.crop(box=boxes['UR'])           # Etc...
LL = full_image.crop(box=boxes['LL'])
LR = full_image.crop(box=boxes['LR'])

# UNCOMMENT TO SEE THE SEGMENTED IMAGES.
# [ img.save(f"{segment}.png") for img, segment in zip((UL, UR, LL, LR), boxes.keys())]

# Convert to nd-arrays for using the images as arguments for Vlc.
arr_UL = np.array(UL)
arr_UR = np.array(UR)
arr_LL = np.array(LL)
arr_LR = np.array(LR)

# Try loading the image into Vlc.
cobject_UL = VC.Vlc(inputImage=arr_UL, numlevels=_NUM_LEVELS, contrast_filt_sigma=_CONT_FILT, contrast_pool_sigma=_CONT_POOL, color_pool_sigma=_COLOR_POOL,
                    prefix="segmentUL")
cobject_UR = VC.Vlc(inputImage=arr_UR, numlevels=_NUM_LEVELS, contrast_filt_sigma=_CONT_FILT, contrast_pool_sigma=_CONT_POOL, color_pool_sigma=_COLOR_POOL,
                    prefix="segmentUR")
cobject_LL = VC.Vlc(inputImage=arr_LL, numlevels=_NUM_LEVELS, contrast_filt_sigma=_CONT_FILT, contrast_pool_sigma=_CONT_POOL, color_pool_sigma=_COLOR_POOL,
                    prefix="segmentLL")
cobject_LR = VC.Vlc(inputImage=arr_LR, numlevels=_NUM_LEVELS, contrast_filt_sigma=_CONT_FILT, contrast_pool_sigma=_CONT_POOL, color_pool_sigma=_COLOR_POOL,
                    prefix="segmentLR")

# Try calculating FC clutter. NOTE: Commented out because this takes quite some time.
'''
global_clutterUL, local_clutter_mapUL = cobject_UL.getClutter_FC(p=1, pix=_OUTPUT_TO_IMAGE)
global_clutterUR, local_clutter_mapUR = cobject_UR.getClutter_FC(p=1, pix=_OUTPUT_TO_IMAGE)
global_clutterLL, local_clutter_mapLL = cobject_LL.getClutter_FC(p=1, pix=_OUTPUT_TO_IMAGE)
global_clutterLR, local_clutter_mapLR = cobject_LR.getClutter_FC(p=1, pix=_OUTPUT_TO_IMAGE)
print(f"global_clutterUL: {global_clutterUL}")
print(f"global_clutterUR: {global_clutterUR}")
print(f"global_clutterLL: {global_clutterLL}")
print(f"global_clutterLR: {global_clutterLR}")
'''
