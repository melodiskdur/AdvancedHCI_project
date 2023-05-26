from ..Utils import label_parser


def group_category_by_position(parsed_data: dict, category: str) -> dict:
    #frames = label_parser.select_parsed_data_by_category(parsed_data=parsed_data, category=category)
    frames = parsed_data['frames']
    groupings = {'frames': [] }
    for frame in frames:
        frame_groupings = []
        for i, box in enumerate(frame['labels']):
            for j in range(len(frame['labels'])):
                if i >= j:
                    continue
                if _overlap(box['box2d'],frame['labels'][j]['box2d']):
                    frame_groupings.append((box,frame['labels'][j]))
        groupings['frames'].append(frame_groupings)
                    
    return groupings
    
def _overlap(box2d_A: dict, box2d_B: dict) -> bool:
    wA, hA = box2d_A['x2'] - box2d_A['x1'], box2d_A['y2'] - box2d_A['y1']
    wB, hB = box2d_B['x2'] - box2d_B['x1'], box2d_B['y2'] - box2d_B['y1']
    
    # Check if the two boxed do NOT overlap, and return the opposite bool.
    return not (box2d_A['x1'] > box2d_B['x2'] or box2d_B['x1'] > box2d_A['x2']) or \
                (box2d_A['y1'] > box2d_B['y2'] or box2d_B['y1'] > box2d_A['y2'])
    