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
    for i in range(len(grid_complexities['frames'])):
        for state_type in pos_groups[category].keys():
            pg_centers, pg_radii = gd.group_centers_n_radii(pos_groups[category][state_type])
            pg_within_radii = FrameSegmenter.points_within_radii(pg_centers, pg_radii, grid_centers)
            # For each grid center, apply the complexity of each group that contains the grid center.
            # Each frame(f) and pos_state.
            for f, pos_state in zip(pg_within_radii['frames'], pos_groups[category][state_type]['frames']):
                # Each group(cwr:center within radius).
                for cwr, p_group in zip(f, pos_state):
                    p_c = _calc_attribute_group_complexity(p_group,POS_FACTORS['center'])
                    # Each grid center(c) located within the group radius.
                    for c in cwr:
                        grid_complexities['frames'][i][c]['pos'].append(p_c)

    #----Spd----
    for i in range(len(grid_complexities['frames'])):
        for state_type in spd_groups[category].keys():
            sg_centers, sg_radii = gd.group_centers_n_radii(spd_groups[category][state_type])
            sg_within_radii = FrameSegmenter.points_within_radii(sg_centers, sg_radii, grid_centers)
            for f, spd_state in zip(sg_within_radii['frames'], spd_groups[category][state_type]['frames']):
                # Each group(cwr:center within radius).
                for cwr, s_group in zip(f, spd_state):
                    s_c = _calc_attribute_group_complexity(s_group,SPEED_FACTORS[s_group[0]['attributes']['Speed']])
                    # Each grid center(c) located within the group radius.
                    for c in cwr:
                        grid_complexities['frames'][i][c]['spd'].append(s_c)

    for i in range(len(grid_complexities['frames'])):
        #----Dir----
        for state_type in dir_groups[category].keys():
            dg_centers, dg_radii = gd.group_centers_n_radii(dir_groups[category][state_type])
            dg_within_radii = FrameSegmenter.points_within_radii(dg_centers, dg_radii, grid_centers)
            for f, dir_state in zip(dg_within_radii['frames'], dir_groups[category][state_type]['frames']):
                # Each group(cwr:center within radius).
                for cwr, d_group in zip(f, dir_state):
                    d_c = _calc_attribute_group_complexity(d_group,DIR_FACTORS[d_group[0]['attributes']['Direction']])
                    # Each grid center(c) located within the group radius.
                    for c in cwr:
                        grid_complexities['frames'][i][c]['dir'].append(d_c)

    return grid_complexities


def _calc_attribute_group_complexity(g,factor):
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
            s_c += _calc_attribute_group_complexity(s_group,SPEED_FACTORS[s_group[0]['attributes']['Speed']])
    # Dir.
    for dir_state in dg_f:
        d_state_len = len(dir_state)
        for d_group in dir_state:
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