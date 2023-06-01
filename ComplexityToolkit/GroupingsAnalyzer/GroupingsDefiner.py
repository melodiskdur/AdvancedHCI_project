from ..Utils import LabelParser
import numpy as np
# from sklearn.cluster import DBSCAN


def group_category_by_position(parsed_data, category: str, threshold: float = 1000.0, max_distance: float = 100.0) -> dict:
    frames = parsed_data['frames']
    frames = LabelParser.select_parsed_data_by_category(parsed_data=frames, category=category)
    frames = [_calculate_boundingbox_areas(frame_data=frames[i]) for i, _ in enumerate(frames)]
    frames = [_calculate_centers(frame_data=frames[i]) for i, _ in enumerate(frames)]
    groupings = []
    for frame in frames:
        frame_groupings = []
        for i, box in enumerate(frame['labels']):
            for j in range(len(frame['labels'])):
                if i >= j:
                    continue
                if _group_analyzer(box['box2d'],frame['labels'][j]['box2d'], threshold, max_distance):
                    frame_groupings.append((box,frame['labels'][j]))
        groupings.append(frame_groupings)

    return { 'frames': [_finalize_groups_frame(groupings_frame=groupings[i]) for i in range(len(groupings))]}


def regroup_by_attribute_state(grouped_data: dict, attribute: str, state: str) -> dict:
    frames = grouped_data['frames']
    groupings = {'frames': []}
    for frame in frames:
        frame_groupings = [[obj for obj in group if obj['attributes'].get(attribute) and obj['attributes'][attribute] == state]
                           for group in frame]
        groupings['frames'].append([group for group in frame_groupings if len(group) > 1])
    return groupings


def group_centers_n_radii(grouped_data: dict) -> tuple:
    frames = grouped_data['frames']
    # Same format as everywhere else.
    groupings_centers = {'frames': []}
    groupings_radii = {'frames': []}
    for frame in frames:
        frame_grouping_centers = [_center_of_mass_group(group=group) for group in frame]
        frame_grouping_radii = [_radius_group(group=group, center_of_mass=mass) for group, mass in zip(frame, frame_grouping_centers)]
        groupings_centers['frames'].append([group for group in frame_grouping_centers])
        groupings_radii['frames'].append([group for group in frame_grouping_radii])
    return groupings_centers, groupings_radii


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


def _group_analyzer(box2d_A: dict, box2d_B: dict, threshold: float=0.70, max_distance: float=100.0) -> bool:
    if min(box2d_A['area'], box2d_B['area']) / max(box2d_A['area'], box2d_B['area']) < threshold:
        return False
    if (norm := np.linalg.norm(np.array(box2d_A['center']) - np.array(box2d_B['center']))) > max_distance*(box2d_A['area']/1):
        return False
    return True


def _center_of_mass_group(group: list) -> tuple:
    groupx = list()
    groupy = list()
    for box in group:
        groupx.append(box['box2d']['center'][0])
        groupy.append(box['box2d']['center'][1])
    return (np.mean(groupx, axis = 0), np.mean(groupy, axis = 0))


def _radius_group(group: list, center_of_mass: tuple) -> float:
    # Select the corner that is furthest away from the center of mass.
    point_list = [(obj['box2d']['x1'], obj['box2d']['y1']) for obj in group] + \
                 [(obj['box2d']['x2'], obj['box2d']['y2']) for obj in group] + \
                 [(obj['box2d']['x1'], obj['box2d']['y2']) for obj in group] + \
                 [(obj['box2d']['x2'], obj['box2d']['y1']) for obj in group]
    
    # Do radius thing.
    point_list_sorted = sorted(point_list, key=lambda p: (center_of_mass[0] - p[0])**2+(center_of_mass[1] - p[1])**2)

    # Return the radius that correpsonds to the largest distance between com and box corner.
    return np.sqrt((center_of_mass[0] - point_list_sorted[-1][0])**2+(center_of_mass[1] - point_list_sorted[-1][1])**2)
    
    
#NOTE: Out of Service
def _overlap(box2d_A: dict, box2d_B: dict) -> bool:
    # Check if the two boxed do NOT overlap, and return the opposite bool.
    return not (box2d_A['x1'] > box2d_B['x2'] or box2d_B['x1'] > box2d_A['x2']) or \
                (box2d_A['y1'] > box2d_B['y2'] or box2d_B['y1'] > box2d_A['y2'])
