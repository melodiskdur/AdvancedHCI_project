import sys
import json
#/home/antjad/ACHI/AdvancedHCI_project/ComplexityToolkit
sys.path.append("../AdvancedHCI_project/")
#print(sys.path)
from ComplexityToolkit.ClutterAnalyzer import VCBatchAnalyzer
from ComplexityToolkit.Utils import LabelParser, ReformateJson
from ComplexityToolkit.GroupingsAnalyzer import GroupingsDefiner as gd
import copy
import math
import matplotlib.pyplot as plt


def _calc_fc_groupings(pg_f,sg_f,dg_f):
    c = 0

    num_pg = len(pg_f)
    num_sg = sum([len(s) for s in sg_f])
    num_dg = sum([len(d) for d in dg_f])
    Sp = 0.5
    Ss = 0.5
    Sd = 0.5
    
    if num_pg != 0 or num_sg != 0 or num_dg != 0:
        c = round((Sp*num_pg + Ss*num_sg + Sd*num_dg),5)

    return c

def calc_framesc_groupings(pos_groups,spd_groups,dir_groups):
    framesc = {"frames":[]}
    
    for i in range(len(pos_groups['vehicle']['pos']['frames'])):
        # Vehicle
        pgv_f = pos_groups['vehicle']['pos']['frames'][i]
        sgv_f = []
        for s in spd_groups['vehicle'].values():
            sgv_f.append(s['frames'][i])
        dgv_f = []
        for d in dir_groups['vehicle'].values():
            sgv_f.append(d['frames'][i])

        v_complexity = _calc_fc_groupings(pgv_f,sgv_f,dgv_f)

        # Pedestrian
        pgp_f = pos_groups['pedestrian']['pos']['frames'][i]
        sgp_f = []
        for s in dir_groups['pedestrian'].values():
            sgp_f.append(s['frames'][i])
        dgp_f = []
        for d in dir_groups['pedestrian'].values():
            dgp_f.append(d['frames'][i])

        p_complexity = _calc_fc_groupings(pgp_f,sgp_f,dgp_f)

        framesc['frames'].append(v_complexity + p_complexity)
    
    return framesc


if __name__ == "__main__":
    file_path = "data/Dublin1_Annotated.json"
    data = LabelParser.read_json(file_path)

    # Pos
    pos_groupings = {
        "vehicle" : {
        "pos" : gd.group_category_by_position(data,"vehicle"),},
        "pedestrian" : {
        "pos" : gd.group_category_by_position(data,"pedestrian"),}
    }

    # Spd
    spd_groupings = {
        "vehicle" : {
        "slow" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Speed",state="Slow"),
        "moderate" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Speed",state="Moderate"),
        "fast" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Speed",state="Fast"),
        "veryfast" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Speed",state="VeryFast"),},

        "pedestrian" : {
        "slow" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Speed",state="Slow"),
        "moderate" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Speed",state="Moderate"),
        "fast" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Speed",state="Fast"),
        "veryfast" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Speed",state="VeryFast"),}
    }

    # Dir
    dir_groupings = {
        "vehicle" : {
        "ul" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="UL"),
        "u" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="U"),
        "ur" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="UR"),
        "l" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="L"),
        "na" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="NA"),
        "r" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="R"),
        "dl" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="DL"),
        "d" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="D"),
        "dr" : gd.regroup_by_attribute_state(pos_groupings['vehicle']['pos'],attribute="Direction",state="DR"),},

        "pedestrian" : {
        "ul" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="UL"),
        "u" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="U"),
        "ur" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="UR"),
        "l" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="L"),
        "na" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="NA"),
        "r" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="R"),
        "dl" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="DL"),
        "d" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="D"),
        "dr" : gd.regroup_by_attribute_state(pos_groupings['pedestrian']['pos'],attribute="Direction",state="DR"),}
    }

    frame_complexities = calc_framesc_groupings(pos_groupings,spd_groupings,dir_groupings)

    print(frame_complexities)

    x = []
    for i, _ in enumerate(frame_complexities['frames']):
        x.append(i)
    
    plt.plot(x, frame_complexities['frames'])
    plt.show()

    """for i, frame in enumerate(pos_groupings['vehicle']['pos']):
        print("frame:",i,", num groups:",len(frame),"{",end='')
        for j, group in enumerate(frame):
            print("group",j,":",len(group),",",end='')
            for obj in group: 
                pass
        print("}")"""
                


