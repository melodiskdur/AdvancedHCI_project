import json

# CONSTANTS.
_SCALABEL_FRAME_FIELDS = {'name', 'url', 'videoName', 'timestamp', 'attributes', 'labels', 'sensor'}
_SCALABEL_LABELS_FIELDS = {'id', 'category', 'attributes', 'manualShape', 'box2d', 'poly2d', 'box3d'}
_URL_TOKEN_STANDARD_WEB = "https://s3-us-west-2.amazonaws.com/scalabel-public/demo/frames/"
_URL_TOKEN_STANDARD_LOCAL = "http://localhost:8686/items/"


def select_parsed_data_by_category(parsed_data: dict, category: str) -> dict:
    category_data = dict()
    for frame, data in parsed_data.items():
        frame_category_data = [{ 'id': obj['id'], 'category': obj['category'], 'attributes': obj['attributes'], 'box2d': obj['box2d']}
                               for obj in data if obj['category'] == category]
        category_data[frame] = frame_category_data
    return category_data


def select_parsed_data_by_attribute(parsed_data: dict, attribute: str) -> dict:
    attribute_data = dict()
    for frame, data in parsed_data.items():
        frame_attribute_data = [{ 'id': obj['id'], 'category': obj['category'], 'state': obj['attributes'][attribute], 'box2d': obj['box2d']}
                                for obj in data if obj['attributes'].get(attribute, None)]
        attribute_data[frame] = frame_attribute_data
    return attribute_data


def select_attribute_by_state(attribute_data: dict, state: str) -> dict:
    state_data = dict()
    for frame, data in attribute_data.items():
        frame_state_data = [{'id': obj['id'], 'category': obj['category'], 'state': obj['state'], 'box2d': obj['box2d']}
                                for obj in data if obj['state'] == state]
        state_data[frame] = frame_state_data
    return state_data


def read_json(file_name):
    try:
        with open(file_name) as file:
            data = json.load(file)
            return data
    except FileNotFoundError as e:
        print(f"label_parser.read_json(): Couldn't read the file '{file_name}'")
        return None


def checkURL(url,token):
    if token in url:
        url = url.replace(token,"")
    return url


def parse_scalabel_json_data(data, url_token: str = _URL_TOKEN_STANDARD_LOCAL):
    if not data:
        return

    parsedData = dict()
    for frame_data in data['frames']:
        for i in range(len(frame_data['labels'])):
            try:
                del frame_data['labels'][i]['manualShape']
            except:
                print("frame_data['labels'][",i,"]['manualShape'] Dosen't exist")
            try:
                del frame_data['labels'][i]['poly2d']
            except:
                print("frame_data['labels'][",i,"]['poly2d'] Dosen't exist")
            try:
                del frame_data['labels'][i]['box3d']
            except:
                print("frame_data['labels'][",i,"]['box3d'] Dosen't exist")

        frame_data['url'] = checkURL(url=frame_data['url'], token=url_token)
        parsedData[frame_data['url']] = frame_data['labels']

    return parsedData


if __name__ == "__main__":
    parsedData = parse_scalabel_json_data(read_json("Ibiza_Original.json"),_URL_TOKEN_STANDARD_WEB )
    #print(parsedData)