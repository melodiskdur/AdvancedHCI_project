import sys
import json
#/home/antjad/ACHI/AdvancedHCI_project/ComplexityToolkit
sys.path.append("../AdvancedHCI_project/")
#print(sys.path)
from ComplexityToolkit.ClutterAnalyzer import VCBatchAnalyzer
from ComplexityToolkit.Utils import LabelParser, ReformateJson
from ComplexityToolkit.GroupingsAnalyzer import GroupingsDefiner

if __name__ == "__main__":
    jsonfile = "Dublin1_Annotated.json"
    
    json_reformatted = ReformateJson.change_categories_attributes(data = LabelParser.read_json(jsonfile), attributes = True)
    json_reformatted = ReformateJson.replace_config(json_reformatted)
    LabelParser.save_json(json_reformatted, "Dublin1_Annotated.json")
