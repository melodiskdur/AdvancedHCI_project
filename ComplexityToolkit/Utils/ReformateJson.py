import json
import label_parser as parser

#constants

LABEL_CONFIG_STANDARD_V1 = {"attributes": [{"name": "Occluded", "type": "switch", "tag": "O"}, 
                                        {"name": "Truncated", "type": "switch", "tag": "T"}, 
                                        {"name": "InMotion", "type": "switch", "tag": "M"}, 
                                        {"name": "Speed", "type": "list", "tag": "spd", "values": ["Slow", "Moderate", "Fast", "VeryFast"], "tagPrefix": "", "tagSuffixes": ["S", "M", "F", "V"]}, 
                                        {"name": "Direction", "type": "list", "tag": "dir", "values": ["UL", "U", "UR", "L", "NA", "R", "DL", "D", "DR"], "tagPrefix": "", "tagSuffixes": ["UL", "U", "UR", "L", "NA", "R", "DL", "D", "DR"]}], 
                                        "categories": [{"name": "veichle"}, {"name": "pedestrian"}]}

VEHICLES = ["car","bus","truck", "train", "trailer", "other vehicle", "motorcycle", "bicycle"]
PEDESTRIANS = ["pedestrian", "other person"]
OTHERS = ["trailer","dog", "rider", "traffic sign", "traffic light"]

    
# replace config to our standard config we are using
def replace_config(data):
        data['config'] = LABEL_CONFIG_STANDARD_V1
        return data

# change the categories to our categories we have in our config. If set attributes to true also clean the attributes already on
def change_categories_attributes(data,attributes = False):
    for i, frame_data in enumerate(data['frames']):
        for i in range(len(frame_data['labels'])):
            if frame_data['labels'][i]['category'] in VEHICLES:
                frame_data['labels'][i]['category'] = "vehicle"
            elif frame_data['labels'][i]['category'] in PEDESTRIANS:
                frame_data['labels'][i]['category'] = "pedestrian"
            else:
                del frame_data['labels'][i]
            if attributes:
                frame_data['labels'][i]['attributes'] = {}
        data['frames'][i] = frame_data

    return data

#save to a json file
def save_json(data,file_path):
     with open(file_path, 'w') as file:
        json.dump(data, file)


if __name__ == "__main__":
    data = replace_config(change_categories_attributes(parser.read_json("Ibiza_Original.json"),True))
    save_json(data,"Ibiza_Original_Parsed.json")
