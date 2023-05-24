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
        self.output_file_path: str = ""
        self.feature_congestion_on = True
        self.subband_entropy_on = True
        self._load_VCFrameAnalyzer_objects(suffix=suffix)

    def calculate_clutter(self, verbose: int = 0):
        '''
        Calculates Feature Congestion and Subband Entropy for a sequence of images
        present in VCBatchAnalyzer.folder_path. For each image, a VCFrameAnalyzer
        object is created and used internally to retrieve the clutter scalars. Finally,
        the data is stored in a .json-file create by the BatchAnalyzer object.

        Notes
        -----
        The output .json-file is created in the same directory as the main program.
        The name is "{time.time()}_{folder_path}.json" by default.

        TODO: Add functionality to specify own file output.
        '''
        self._create_json_file()
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
            self._add_framedata_to_json(frame_no=str(frame), frame_data=vc_object)
            if verbose > 0:
                print(f"Done in {time.time() - f_start} [s].")

        if verbose > 0:
            print(f"Done. Total execution time: {time.time() - start} [s].")

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

    def _add_framedata_to_json(self, frame_no: str, frame_data: dict):
        prev_data = {}
        with open(self.output_file_path, "r") as f:
            prev_data = json.load(f)
        prev_data['data'].update({frame_no: frame_data.clutter_data_dict(verbose=0)})
        with open(self.output_file_path, "w") as f:
            output = json.dumps(prev_data)
            f.write(output)

    def _create_json_file(self):
        main_fields = {'folder_name': self.folder_path,
                       'dimensions': self.grid_dimensions,
                       'number_of_frames': len(self.vc_frame_objects),
                       'image_width': self.vc_frame_objects[0].image.size[0],
                       'image_height': self.vc_frame_objects[0].image.size[1],
                       'data': dict() }
        self.output_file_path = f"{time.time()}_{self.folder_path}.json"
        init_json = json.dumps(main_fields)
        with open(self.output_file_path, "w") as f:
            f.write(init_json)

    def _load_VCFrameAnalyzer_objects(self, suffix: str = '.jpg'):
        file_paths = DirectoryParser.parse_directory(self.folder_path, suffix=suffix)
        ordered_files = DirectoryParser.order_parsed_files(file_paths=file_paths)
        self.vc_frame_objects = {i: VCFrameAnalyzer(input_image=ordered_files[i], num_segments=self.grid_dimensions)
                                 for i, _ in enumerate(ordered_files)}

    def _toggle_VCFA_clutter(self):
        if self.vc_frame_objects:
            [vcfa_object.toggle_feature_congestion(value=self.feature_congestion_on) for vcfa_object in self.vc_frame_objects.values()]
            [vcfa_object.toggle_subband_entropy(value=self.subband_entropy_on) for vcfa_object in self.vc_frame_objects.values()]
