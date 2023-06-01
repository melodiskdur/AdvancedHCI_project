import sys
import json

import os


sys.path.append("../AdvancedHCI_project/")
cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))
from ComplexityToolkit.ClutterAnalyzer import VCBatchAnalyzer
from ComplexityToolkit.Utils import LabelParser, ReformateJson
print(sys.path)
#find . -name "*:Zone.Identifier" -type f -delete
#convert '*.jpg[200x]' resized%03d.png
if __name__ == "__main__":
    folder = "cairo"
    grid_dimensions = (10, 20)
    batchAnalyzer = VCBatchAnalyzer(folder_path=folder, grid_dimensions=grid_dimensions)
    batchAnalyzer.calculate_clutter(verbose=1)

