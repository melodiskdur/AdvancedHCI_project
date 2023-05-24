from ..Utils import FrameSegmenter
from PIL import Image
import visual_clutter as vc
import numpy as np


class VCFrameAnalyzer():
    def __init__(self, input_image=None, num_segments: tuple = (1, 1)):
        self.image: Image
        self.num_segments: tuple
        self.vc_settings: dict
        self.frame_clutter: dict = dict()
        self.string_path: str = ""
        self.feature_congestion_on: bool = True
        self.subband_entropy_on: bool = True

        if input_image:
            self.load_image(input_image=input_image)
        self.set_num_segments(num_segments=num_segments)
        self.load_visual_clutter_settings(settings={'numlevels': 3, 'contrast_filt_sigma': 1, 'contrast_pool_sigma': None, 'color_pool_sigma': 3})

    def calculate_clutter(self, retrieve_sub_image: bool = False, verbose: int = 0):
        '''
        Calculates the Feature Congestion and Subband Entropy of the loaded
        frame image, using the functionality provided in the visual_clutter library.
        See https://github.com/kargaranamir/visual-clutter for details.

        Output
        -----
        The data is stored in VCFramAnalyzer.frame_clutter in the format
        {
            (row_i, col_j): {
                'feature_congestion': float,\n
                'subband_entropy: float',\n
                'top': int,\n
                'left' int,\n
                'center_xy' (float, float),\n
                'width': int,\n
                'height': int},\n
                }\n
        }

        Notes
        -----
        if 'feature_congestion' or 'subband_entropy' has been toggled to False (i.e 'Off'), the corresponding dict field
        value will be set to -1.
        '''
        # Segment the image.
        segments = FrameSegmenter.segment_frame(image=self.image, num_segments=self.num_segments)
        # Perform FC & SE on each segment.
        for key, val in segments.items():
            if verbose > 0:
                print(f"Calculating clutter for {key}")
            self.frame_clutter[str(key)] = self._calculate_subframe_clutter(subframe_dict=val)
        if verbose > 0:
            print("Clutter calculations done.")

    def clutter_data_dict(self, verbose: int = 1) -> dict:
        '''
        Returns a dictionary with all the rows and cols as well as the original image size
        and (if it was loaded from a string path) the path to the original image.

        Notes
        ---
        By default, 'verbose' is set to 1. This adds 'image_width' and 'image_height' to the
        data dict. Set 'verbose' = 0 to remove those fields.
        '''
        if not self.frame_clutter:
            return {'image_width': None, 'image_height': None, 'clutter_data': None, 'file_path': ""}
        output = {'file_path': self.string_path, 'clutter_data': self.frame_clutter}
        return {**output, 'image_width': self.image.size[0], 'image_height': self.image.size[1]} \
                if verbose > 0 else output

    def load_image(self, input_image):
        '''
        Store an image in the VCFrameAnalyzer object. 'input_image' can be
        either a string path to an image file, or a PIL.Image object.
        '''
        if isinstance(input_image, str):
            self.image = Image.open(input_image)
            self.string_path = input_image
        elif isinstance(input_image, Image.Image):
            self.image = input_image
        else:
            raise TypeError(f"VCFrameAnalyzer.load_image(): input_image cannot \
                            be of type '{type(input_image)}'. Allowed types are str (path to file) \
                            or PIL.Image.")

    def set_num_segments(self, num_segments: tuple = (1, 1)):
        '''
        Set the amount of segments, specified as number of rows & columns.
        '''
        if isinstance(num_segments, tuple):
            self.num_segments = num_segments
        else:
            raise TypeError(f"VCFrameAnalyzer.set_num_segments(): 'num_segments' cannot \
                            be of type '{type(num_segments)}'. Allowed type is tuple(int,int).")

    def toggle_feature_congestion(self, value: bool):
        '''
        Determines whether or not the Feature Congestion-type clutter should
        be calculated. Default is True.
        '''
        if isinstance(value, bool):
            self.feature_congestion_on = value

    def toggle_subband_entropy(self, value: bool):
        '''
        Determines whether or not the Subband Entropy-type clutter should
        be calculated. Default is True.
        '''
        if isinstance(value, bool):
            self.subband_entropy_on = value

    def load_visual_clutter_settings(self, settings: dict):
        '''
        Allows the user to specify the parameters used in the visual_clutter.Vlc object. Will
        be set to the visual_clutter default parameter values. Make sure to read the documentation
        for visual_clutter for more information on the parameters: https://github.com/kargaranamir/visual-clutter.

        settings = {
            'numlevels': int,\n
            'contrast_filt_sigma': int,\n
            'contrast_pool_sigma': int,\n
            'color_pool_sigma': int\n
        }

        '''
        if not isinstance(settings, dict):
            raise TypeError(f"VCFrameAnalyzer.load_visual_clutter_settings(): 'settings' cannot \
                            be of type '{type(settings)}'. Allowed type is dict. See documentation \
                            for required fields.")
        required_fields = {'numlevels', 'contrast_filt_sigma', 'contrast_pool_sigma', 'color_pool_sigma'}
        if required_fields.intersection(set(settings.keys())) == required_fields:
            self.vc_settings = settings
        else:
            raise KeyError(f"VCFrameAnalyzer.load_visual_clutter_settings(): Missing keys \
                        {required_fields.difference(set(settings.keys()))}. See documentation for \
                            required fields.")

    def _calculate_subframe_clutter(self, subframe_dict: dict) -> dict:
        segment_vlc = vc.Vlc(inputImage=np.array(subframe_dict['image']),
                             numlevels=self.vc_settings['numlevels'],
                             contrast_filt_sigma=self.vc_settings['contrast_filt_sigma'],
                             contrast_pool_sigma=self.vc_settings['contrast_pool_sigma'],
                             color_pool_sigma=self.vc_settings['color_pool_sigma'])
        segment_fc, _ = segment_vlc.getClutter_FC() if self.feature_congestion_on else (-1, -1)
        segment_se = segment_vlc.getClutter_SE() if self.subband_entropy_on else -1
        return {'feature_congestion': segment_fc, 'subband_entropy': segment_se,
                'top': subframe_dict['top'],
                'left': subframe_dict['left'],
                'width': subframe_dict['width'],
                'height': subframe_dict['height'],
                'center_xy': (float(subframe_dict['left'] + subframe_dict['width'] // 2),
                              float(subframe_dict['top'] + subframe_dict['height'] // 2))}
