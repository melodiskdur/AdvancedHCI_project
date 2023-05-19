import json


def readJson(file_name):
    try:
        with open(file_name) as file:
            data = json.load(file)
            return data

    except:
        print("readJson: couldn't read the file")



def checkURL(url,token):

    if token in url:
        url = url.replace(token,"")
    return url

def parseJsonData(data):
    parsedData = dict()
    token = "http://localhost:8686/items/"
    for frame_data in data['frames']:
        for i in range(len(frame_data['labels'])):
            del frame_data['labels'][i]['manualShape']
            del frame_data['labels'][i]['poly2d']
            del frame_data['labels'][i]['box3d']
        frame_data['url'] = checkURL(frame_data['url'],token)
        parsedData[frame_data['url']] = frame_data['labels']

    return parsedData


if __name__ == "__main__":
    parsedData = parseJsonData(readJson("test_project_export_2023-05-17_13-19-26.json"))
    print(parsedData)