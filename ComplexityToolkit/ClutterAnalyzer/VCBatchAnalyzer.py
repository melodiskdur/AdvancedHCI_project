from ..Utils import FrameSegmenter, DirectoryParser
from .VCFrameAnalyzer import VCFrameAnalyzer
import time
import json

class VCBatchAnalyzer():
    def __init__(self, folder_path: str, grid_dimensions: tuple = (1, 1), suffix: str = '.jpg'):
        self.frame_batch: dict = dict()
        self.vc_frame_objects: dict = dict()
        self.grid_dimensions: tuple = grid_dimensions
        self.folder_path: str = folder_path
        self.feature_congestion_on = True
        self.subband_entropy_on = True
        self._load_VCFrameAnalyzer_objects(suffix=suffix)

    def calculate_clutter(self, verbose: int = 0):
        '''
        Calculates Feature Congestion and Subband Entropy for a sequence of images
        present in VCBatchAnalyzer.folder_path. For each image, a VCFrameAnalyzer
        object is created and used internally to retrieve the clutter scalars.
        '''
        if verbose > 0:
            start = time.time()
            print(f"Calculating clutter for image set {self.folder_path}. A total of {len(self.vc_frame_objects)} images will be processed.")
            print(f"Dimensions: {self.grid_dimensions}.")
            print(f"Feature Congestion will be calculated: {self.feature_congestion_on}.")
            print(f"Subband Entropy will be calculated: {self.subband_entropy_on}.")

        self._toggle_VCFA_clutter()

        for frame, vc_object in self.vc_frame_objects.items():
            if verbose > 0:
                f_start = time.time()
                print(f"Calculating clutter for frame {frame}. ", end="")
            vc_object.calculate_clutter()
            if verbose > 0:
                print(f"Done in {time.time() - f_start} [s].")

        if verbose > 0:
            print(f"Done. Total execution time: {time.time() - start} [s].")

    def to_json(self, file_name: str = "default_output.json"):
        frame_data = {str(i): favc_object.clutter_data_dict() for i, favc_object in self.vc_frame_objects.items()}
        output = json.dumps(frame_data, indent=4)
        with open(file_name, "w") as f:
            f.write(output)

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

    def _load_VCFrameAnalyzer_objects(self, suffix: str = '.jpg'):
        file_paths = DirectoryParser.parse_directory(self.folder_path, suffix=suffix)
        ordered_files = DirectoryParser.order_parsed_files(file_paths=file_paths)
        self.vc_frame_objects = {i: VCFrameAnalyzer(input_image=ordered_files[i], num_segments=self.grid_dimensions)
                                 for i, _ in enumerate(ordered_files)}

    def _toggle_VCFA_clutter(self):
        if self.vc_frame_objects:
            [vcfa_object.toggle_feature_congestion(value=self.feature_congestion_on) for vcfa_object in self.vc_frame_objects.values()]
            [vcfa_object.toggle_subband_entropy(value=self.subband_entropy_on) for vcfa_object in self.vc_frame_objects.values()]
