from PIL import Image


def segment_frame(image: Image, num_segments: tuple = (1, 1)) -> dict:
    '''
    Creates a (row, col) sub-image grid from a given PIL.Image object and
    grid dimensions (row, col).

    Returns a dictionary where each item (sub-image + related data) has the
    following format: \n
    (row_i, col_j): {
        'image': Sub-image as PIL.Image object,\n
        'top': y-coordinate of the upper-left bounding box-corner,\n
        'left': x-coordinate of the upper-left bounding box-corner,\n
        'width': width of the sub-image, \n
        'height': height of the sub-image\n
    }, \n
    where they key (0, 0) is the first sub-image starting at the upper-left corner of the
    original image.
    '''
    size_row, size_col = _calculate_segment_size(image.size, num_segments)
    rows, cols = num_segments[0], num_segments[1]
    # Create and return the segment dictionary.
    return {(i, j): _calculate_segment_data(image=image, cell=(i, j), cell_size=(size_row, size_col))
            for i in range(rows) for j in range(cols)}


def grid_centers(window_size: tuple = (1920, 1080), grid_dimensions: tuple = (10, 20)) -> list:
    a, b = _calculate_segment_size(window_size, grid_dimensions)
    size_row, size_col = a // 2 , b // 2
    return [((b * i) + size_row, (a * j)  + size_col) for i in range(grid_dimensions[1]) for j in range(grid_dimensions[0])]

# [(x1, y1), (x2, y2), ... ]
def _points_within_radius(c, r, points):
    points_wr = []
    for p in points:
        if ((c[0] - p[0])**2 + (c[1] - p[1])**2) < r ** 2:
            points_wr.append(p)
    return points_wr


def points_within_radii(g_centers : dict, g_radii : dict, points: list) -> dict:
    centers = g_centers['frames']
    radii = g_radii['frames']
    return {'frames' : [[_points_within_radius(c,r,points) for c, r in zip(c_g, r_g)] for c_g, r_g in zip(centers,radii)]}


def _calculate_segment_size(img_size, num_segments) -> tuple:
    return img_size[1] // num_segments[0], img_size[0] // num_segments[1]


def _calculate_segment_data(image: Image, cell: tuple, cell_size: tuple) -> dict:
    top, left = cell[0] * cell_size[0], cell[1] * cell_size[1]
    bbox = (left, top, left + cell_size[1], top + cell_size[0])         # L T R B.
    subframe = image.crop(box=bbox)
    return {'image': subframe, 'top': top, 'left': left, 'width': cell_size[1], 'height': cell_size[1]}
