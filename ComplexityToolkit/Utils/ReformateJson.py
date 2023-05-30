import json

# CONSTANTS
LABEL_CONFIG_STANDARD_V1 = {"attributes": [{"name": "Occluded", "type": "switch", "tag": "O"},
                                        {"name": "Truncated", "type": "switch", "tag": "T"},
                                        {"name": "InMotion", "type": "switch", "tag": "M"},
                                        {"name": "Speed", "type": "list", "tag": "spd", "values": ["Slow", "Moderate", "Fast", "VeryFast"], "tagPrefix": "", "tagSuffixes": ["S", "M", "F", "V"]},
                                        {"name": "Direction", "type": "list", "tag": "dir", "values": ["UL", "U", "UR", "L", "NA", "R", "DL", "D", "DR"], "tagPrefix": "", "tagSuffixes": ["UL", "U", "UR", "L", "NA", "R", "DL", "D", "DR"]}],
                                        "categories": [{"name": "vehicle"}, {"name": "pedestrian"}]}

VEHICLES = ["car","bus","truck", "train", "trailer", "other vehicle", "motorcycle", "bicycle"]
PEDESTRIANS = ["pedestrian", "other person"]
OTHERS = ["dog", "rider", "traffic sign", "traffic light"]


# replace config to our standard config we are using
def replace_config(data):
        data['config'] = LABEL_CONFIG_STANDARD_V1
        return data

# change the categories to our categories we have in our config. If set attributes to true also clean the attributes already on
def change_categories_attributes(data,attributes = False):
    for i, frame_data in enumerate(data['frames']):
        indices_to_remove = []
        for j in range(len(frame_data['labels'])):
            if frame_data['labels'][j]['category'] in VEHICLES or "vehicle" in frame_data['labels'][j]['category']:
                frame_data['labels'][j]['category'] = "vehicle"
            elif frame_data['labels'][j]['category'] in PEDESTRIANS or "pedestrian" in frame_data['labels'][j]['category']:
                frame_data['labels'][j]['category'] = "pedestrian"
            else:
                indices_to_remove.append(j)
            if attributes:
                frame_data['labels'][j]['attributes'] = {}
        frame_data['labels'] = [frame_data['labels'][j] for j in range(len(frame_data['labels'])) if j not in indices_to_remove]
        data['frames'][i] = frame_data

    return data