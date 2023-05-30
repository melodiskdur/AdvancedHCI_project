from ..Utils import LabelParser
import numpy as np
# from sklearn.cluster import DBSCAN


def group_category_by_position(parsed_data: dict, category: str, threshold: float = 1000.0, max_distance: float = 100.0) -> dict:
    frames = parsed_data['frames']
    frames = LabelParser.select_parsed_data_by_category(parsed_data=frames, category=category)
    frames = [_calculate_boundingbox_areas(frame_data=frames[i]) for i, _ in enumerate(frames)]
    frames = [_calculate_centers(frame_data=frames[i]) for i, _ in enumerate(frames)]
    groupings = {'frames': []}
    for frame in frames:
        frame_groupings = []
        for i, box in enumerate(frame['labels']):
            for j in range(len(frame['labels'])):
                if i >= j:
                    continue
                if _group_analyzer(box['box2d'],frame['labels'][j]['box2d'], threshold, max_distance):
                    frame_groupings.append((box,frame['labels'][j]))
        groupings['frames'].append(frame_groupings)

    return { 'frames': [_finalize_groups_frame(groupings_frame=groupings['frames'][i]) for i, _ in enumerate(groupings['frames'])]}


def regroup_by_attribute_state(grouped_data: dict, attribute: str, state: str) -> dict:
    frames = grouped_data['frames']
    groupings = {'frames': []}
    for frame in frames:
        frame_groupings = [[obj for obj in group if obj['attributes'].get(attribute) and obj['attributes'][attribute] == state]
                           for group in frame]
        groupings['frames'].append([group for group in frame_groupings if len(group) > 1])
    return groupings


def _finalize_groups_frame(groupings_frame: list) -> list:
    finalized_groups = []
    for pair in groupings_frame:
        group_found = False
        for i, group in enumerate(finalized_groups):
            if _in_group(pair[0], group) and not _in_group(pair[1], group):
                finalized_groups[i].append(pair[1])
                group_found = True
                break
            elif not _in_group(pair[0], group) and _in_group(pair[1], group):
                finalized_groups[i].append(pair[0])
                group_found = True
                break
            elif _in_group(pair[0], group) and _in_group(pair[1], group):
                group_found = True
                break
        if not group_found:
            finalized_groups.append([pair[0], pair[1]])
    return finalized_groups


def _in_group(obj: dict, group: set) -> bool:
    return obj['id'] in { o['id'] for o in group }


def _calculate_boundingbox_areas(frame_data: dict) -> dict:
    for i, obj in enumerate(frame_data['labels']):
        # Calculate width and height for each bounding box in the frame.
        w, h = obj['box2d']['x2'] - obj['box2d']['x1'], obj['box2d']['y2'] - obj['box2d']['y1']
        frame_data['labels'][i]['box2d']['area'] = w*h
    return frame_data


def _calculate_centers(frame_data: dict) -> dict:
    for i, obj in enumerate(frame_data['labels']):
        # Retrieve center points for each bounding box.
        w, h = obj['box2d']['x2'] - obj['box2d']['x1'], obj['box2d']['y2'] - obj['box2d']['y1']
        frame_data['labels'][i]['box2d']['center'] = (obj['box2d']['x1'] + 0.5 * w, obj['box2d']['y1'] + 0.5 * h)
    return frame_data


def _group_analyzer(box2d_A: dict, box2d_B: dict, threshold: float=1000.0, max_distance: float=100.0) -> bool:
    if min(box2d_A['area'], box2d_B['area']) / max(box2d_A['area'], box2d_B['area']) < 0.70:
        return False
    if (norm := np.linalg.norm(np.array(box2d_A['center']) - np.array(box2d_B['center']))) > max_distance*(box2d_A['area']/10):
        return False
    return True


def _overlap(box2d_A: dict, box2d_B: dict) -> bool:
    # Check if the two boxed do NOT overlap, and return the opposite bool.
    return not (box2d_A['x1'] > box2d_B['x2'] or box2d_B['x1'] > box2d_A['x2']) or \
                (box2d_A['y1'] > box2d_B['y2'] or box2d_B['y1'] > box2d_A['y2'])
