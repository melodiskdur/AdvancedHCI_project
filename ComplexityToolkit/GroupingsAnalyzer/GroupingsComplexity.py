import sys
import json
from ..Utils import LabelParser, ReformateJson, FrameSegmenter
from ..GroupingsAnalyzer import GroupingsDefiner as gd
import copy
import math
import matplotlib.pyplot as plt


SPEED_FACTORS = {
    'Slow' : 0.3,
    'Moderate' : 0.4,
    'Fast' : 0.7,
    'VeryFast' : 1.0
}


DIR_FACTORS = {
    "UL" : 0.5,
    "U" : 0.5,
    "UR" : 0.5,
    "L" : 0.5,
    "NA" : 0.5,
    "R" : 0.5,
    "DL" : 0.5,
    "D" : 0.5,
    "DR" : 0.5
}


POS_FACTORS = {
    'center': 0.5
}


def _calc_gridc_groupings(pos_groups: dict, spd_groups: dict, dir_groups: dict, grid_centers: list, category:str):

    #{(123,123):{'pos':123,'spd':123,'dir':123}}
    # {'frames' : [ [[(1,2),(3,4)], [(1,2),(3,4)]], [[(1,2),(3,4)], [(1,2),(3,4)]] ]
    # {'frames' : [[],[],[(324,234),(324,234)]] }  (grid centers inside each group radius).

    # Complexity values

    grid_complexities = { 'frames':  [{(cell[0], cell[1]) : {'pos': [], 'spd': [], 'dir': []} for cell in grid_centers} for j in range(len(pos_groups[category]['pos']['frames']))] }

    #----Pos----
    for state_type in pos_groups[category].keys():
        pg_centers, pg_radii = gd.group_centers_n_radii(pos_groups[category][state_type])
        pg_within_radii = FrameSegmenter.points_within_radii(pg_centers, pg_radii, grid_centers)
        # For each grid center, apply the complexity of each group that contains the grid center.
        # Each frame(f) and pos_state.
        for i, (f, pos_state) in enumerate(zip(pg_within_radii['frames'], pos_groups[category][state_type]['frames'])):
            # Each group(cwr:center within radius).
            for cwr, p_group in zip(f, pos_state):
                p_c = _calc_attribute_group_complexity(p_group,POS_FACTORS['center'])
                # Each grid center(c) located within the group radius.
                for c in cwr:
                    grid_complexities['frames'][i][c]['pos'].append(p_c)

    #----Spd----
    for state_type in spd_groups[category].keys():
        sg_centers, sg_radii = gd.group_centers_n_radii(spd_groups[category][state_type])
        sg_within_radii = FrameSegmenter.points_within_radii(sg_centers, sg_radii, grid_centers)
        for i, (f, spd_state) in enumerate(zip(sg_within_radii['frames'], spd_groups[category][state_type]['frames'])):
            # Each group(cwr:center within radius).
            for cwr, s_group in zip(f, spd_state):
                s_c = _calc_attribute_group_complexity(s_group,SPEED_FACTORS[s_group[0]['attributes']['Speed']])
                # Each grid center(c) located within the group radius.
                for c in cwr:
                    grid_complexities['frames'][i][c]['spd'].append(s_c)

    #----Dir----
    for state_type in dir_groups[category].keys():
        dg_centers, dg_radii = gd.group_centers_n_radii(dir_groups[category][state_type])
        dg_within_radii = FrameSegmenter.points_within_radii(dg_centers, dg_radii, grid_centers)
        for i, (f, dir_state) in enumerate(zip(dg_within_radii['frames'], dir_groups[category][state_type]['frames'])):
            # Each group(cwr:center within radius).
            for cwr, d_group in zip(f, dir_state):
                d_c = _calc_attribute_group_complexity(d_group,DIR_FACTORS[d_group[0]['attributes']['Direction']])
                # Each grid center(c) located within the group radius.
                for c in cwr:
                    grid_complexities['frames'][i][c]['dir'].append(d_c)

    return grid_complexities


def _calc_gridc_boxes(pos_boxes: dict, spd_boxes: dict, dir_boxes: dict, grid_centers: list, category:str):

    #{(123,123):{'pos':123,'spd':123,'dir':123}}
    # {'frames' : [ [[(1,2),(3,4)], [(1,2),(3,4)]], [[(1,2),(3,4)], [(1,2),(3,4)]] ]
    # {'frames' : [[],[],[(324,234),(324,234)]] }  (grid centers inside each group radius).

    # Complexity values

    grid_complexities = { 'frames':  [{(cell[0], cell[1]) : {'pos': [], 'spd': [], 'dir': []} for cell in grid_centers} for j in range(len(pos_boxes[category]['pos']['frames']))] }

    #----Pos----
    for state_type in pos_boxes[category].keys():
        pg_centers, pg_radii = gd.centers_n_radii(pos_boxes[category][state_type])
        pg_within_radii = FrameSegmenter.points_within_radii(pg_centers, pg_radii, grid_centers)
        # For each grid center, apply the complexity of each group that contains the grid center.
        # Each frame(f) and pos_state.
        for i, (f, pos_state) in enumerate(zip(pg_within_radii['frames'], pos_boxes[category][state_type]['frames'])):
            # Each group(cwr:center within radius).
            for cwr, p_group in zip(f, pos_state):
                p_c = _calc_attribute_group_complexity(p_group,POS_FACTORS['center'])
                # Each grid center(c) located within the group radius.
                for c in cwr:
                    grid_complexities['frames'][i][c]['pos'].append(p_c)

    #----Spd----
    for state_type in spd_boxes[category].keys():
        sg_centers, sg_radii = gd.centers_n_radii(spd_boxes[category][state_type])
        sg_within_radii = FrameSegmenter.points_within_radii(sg_centers, sg_radii, grid_centers)
        for i, (f, spd_state) in enumerate(zip(sg_within_radii['frames'], spd_boxes[category][state_type]['frames'])):
            # Each group(cwr:center within radius).
            for cwr, s_group in zip(f, spd_state):
                s_c = _calc_attribute_group_complexity(s_group,SPEED_FACTORS[s_group['attributes']['Speed']])
                # Each grid center(c) located within the group radius.
                for c in cwr:
                    grid_complexities['frames'][i][c]['spd'].append(s_c)
    #----Dir----
    for state_type in dir_boxes[category].keys():
        dg_centers, dg_radii = gd.centers_n_radii(dir_boxes[category][state_type])
        dg_within_radii = FrameSegmenter.points_within_radii(dg_centers, dg_radii, grid_centers)
        for i, (f, dir_state) in enumerate(zip(dg_within_radii['frames'], dir_boxes[category][state_type]['frames'])):
            # Each group(cwr:center within radius).
            for cwr, d_group in zip(f, dir_state):
                d_c = _calc_attribute_group_complexity(d_group,DIR_FACTORS[d_group['attributes']['Direction']])
                # Each grid center(c) located within the group radius.
                for c in cwr:
                    grid_complexities['frames'][i][c]['dir'].append(d_c)

    return grid_complexities


def subtract_groupc_from_objc(group_frames, obj_frames) -> list:
    subtracted_complexity = []
    for groupsc, objsc in zip(group_frames, obj_frames):
        subtracted_frame_complexity = [max(objc - groupc, 0) for groupc, objc in zip(groupsc, objsc)]
        subtracted_complexity.append(subtracted_frame_complexity)
    return subtracted_complexity


def _calc_attribute_group_complexity(g, factor):
    group_length = len(g)
    group_complexity = group_length * factor
    return group_complexity


def _calc_fc_groupings(pg_f,sg_f,dg_f):
    p_c = 0.0
    s_c = 0.0
    d_c = 0.0

    # Position.
    for pos_state in pg_f:
        p_state_len = len(pos_state)
        for p_group in pos_state:
            p_c += _calc_attribute_group_complexity(p_group,POS_FACTORS['center'])
    # Speed
    for speed_state in sg_f:
        s_state_len = len(speed_state)
        for s_group in speed_state:
            if not isinstance(s_group, list):
                s_group = [s_group]
            #print(s_group)
            if "Speed" in s_group[0]['attributes'].keys():
                s_c += _calc_attribute_group_complexity(s_group,SPEED_FACTORS[s_group[0]['attributes']['Speed']])
    # Dir.
    for dir_state in dg_f:
        d_state_len = len(dir_state)
        for d_group in dir_state:
            if not isinstance(d_group, list):
                d_group = [d_group]
            if "Speed" in s_group[0]['attributes'].keys():
                d_c += _calc_attribute_group_complexity(d_group,DIR_FACTORS[d_group[0]['attributes']['Direction']])

    return p_c, s_c, d_c


def calc_framesc_groupings(pos_groups,spd_groups,dir_groups):

    frames_pc = {"frames":[]}
    frames_sc = {"frames":[]}
    frames_dc = {"frames":[]}

    num_frames = len(pos_groups['vehicle']['pos']['frames'])

    for i in range(num_frames):

        # Vehicle Groupings
        pgv_f = pos_groups['vehicle']['pos']['frames'][i]
        sgv_f = []
        for s in spd_groups['vehicle'].values():
            sgv_f.append(s['frames'][i])
        dgv_f = []
        for d in dir_groups['vehicle'].values():
            sgv_f.append(d['frames'][i])

        # Pedestrian Groupings
        pgp_f = pos_groups['pedestrian']['pos']['frames'][i]
        sgp_f = []
        for s in dir_groups['pedestrian'].values():
            sgp_f.append(s['frames'][i])
        dgp_f = []
        for d in dir_groups['pedestrian'].values():
            dgp_f.append(d['frames'][i])

        # Calculate complexities
        v_p_c, v_s_c, v_d_c = _calc_fc_groupings(pgv_f,sgv_f,dgv_f)
        p_p_c, p_s_c, p_d_c = _calc_fc_groupings(pgp_f,sgp_f,dgp_f)

        # Append Complexities
        frames_pc['frames'].append(v_p_c + p_p_c)
        frames_sc['frames'].append(v_s_c + p_s_c)
        frames_dc['frames'].append(v_d_c + p_d_c)

    return frames_pc, frames_sc, frames_dc

def calc_framesc(pos_boxes,spd_boxes,dir_boxes):

    frames_pc = {"frames":[]}
    frames_sc = {"frames":[]}
    frames_dc = {"frames":[]}

    num_frames = len(pos_boxes['vehicle']['pos']['frames'])

    for i in range(num_frames):

        # Vehicle Boxes
        pgv_f = pos_boxes['vehicle']['pos']['frames'][i]
        sgv_f = []
        for s in spd_boxes['vehicle'].values():
            sgv_f.append(s['frames'][i])
        dgv_f = []
        for d in dir_boxes['vehicle'].values():
            sgv_f.append(d['frames'][i])

        # Pedestrian boxes
        pgp_f = pos_boxes['pedestrian']['pos']['frames'][i]
        sgp_f = []
        for s in dir_boxes['pedestrian'].values():
            sgp_f.append(s['frames'][i])
        dgp_f = []
        for d in dir_boxes['pedestrian'].values():
            dgp_f.append(d['frames'][i])

        # Calculate complexities
        v_p_c, v_s_c, v_d_c = _calc_fc_groupings(pgv_f,sgv_f,dgv_f)
        p_p_c, p_s_c, p_d_c = _calc_fc_groupings(pgp_f,sgp_f,dgp_f)

        # Append Complexities
        frames_pc['frames'].append(v_p_c + p_p_c)
        frames_sc['frames'].append(v_s_c + p_s_c)
        frames_dc['frames'].append(v_d_c + p_d_c)

    return frames_pc, frames_sc, frames_dc