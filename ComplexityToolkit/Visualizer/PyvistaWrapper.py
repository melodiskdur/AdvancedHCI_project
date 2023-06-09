import numpy as np
import pyvista as pv
from sklearn.neighbors import NearestNeighbors
import cmocean
import copy
import json

#################################################
#////////////////--- Helpers ---/////////////////

def apply_threshold(mylist,threshold):
    return [(0 if x < threshold else x) for x in mylist]

def force_within_range(mylist):
    return [x / max(list(mylist)) for x in mylist]

def create_nn_scalars(points:np.ndarray, num_neighbors, scalar_threshold=0.5):
    """
    Calculate the nearest neighbor scalars for all points.
    A higher values are give to points that have neighbors that are close to it.
    Input:
        points: a np.ndarray of 3d points
        num_neighbors: the amount of neighbors that is considered for each point
        scalar_threshold: points assigned a scalar value below the threshold are given a scalar value of 0
    Output:
        scalars: a np.ndarray of float scalar values for each 3d point
    """
    if num_neighbors <= 0:
        num_neighbors = 1

    # Compute the nearest neighbors for each point
    neighbors = NearestNeighbors(n_neighbors=num_neighbors).fit(points)
    distances, _ = neighbors.kneighbors(points)

    # Calculate the scalars for the points based on the distances
    # Add a small value to prevent division by zero
    scalars = (1.0 / (distances.mean(axis=1) + 1e-10))

    # Scale the scalars to fit fully within [0,1]
    scalars = force_within_range(scalars)

    # Set all the scalars that are below the threshold to 0
    scalars = apply_threshold(scalars,scalar_threshold)

    return np.array(scalars)

def create_3d_points(
        num_points_per_frame:int=100, 
        frame_dimensions=(10,8), 
        num_frames:int=10, 
        dist_between_frames:int=1
        ):
    """
    Create all the points and their corresponding scalars
    Input:
        num_points_per_frame: the number of points in each frame
        frame_dimensions: a tuple with the width and height of the
        num_frames: the number of frames
        dist_between_frames: the distance between each frame in the plot
    Output:
        points: a np.array with 3d points
    """
    # Initialize the points list
    points = []

    # Create points for each frame
    for i in range(num_frames):

        # Calculate some random xy values withing the width and height of the frame
        x_values = np.random.uniform(low=0.0, high=frame_dimensions[0], size=num_points_per_frame)
        y_values = np.random.uniform(low=0.0, high=frame_dimensions[1], size=num_points_per_frame)

        # Create points and add a specific z-value for each frame
        frame_points = np.array([np.array([x,y,-i*dist_between_frames]) for x,y in zip(x_values,y_values)])

        # Append all the points created to points
        for p in frame_points:
            points.append(p)

    # Change points to a numpy array for ease of use
    points = np.array(points)

    return points

def get_video_data(
        file_path,
        scalar_type:str='feature_congestion',
        scalar_threshold:float=0.0,
        dist_between_frames=1
        ):
    """open and extract points,scalars etc from a data folder"""
    payload = None
    try:
        # open the file and load the data
        with open(file_path) as f:
            payload = json.load(f)
    except FileNotFoundError:
        print("ERROR: file not found. Try entering a different path in the input field")
        return np.array([]), np.array([]), payload
    
    # Initialize the points and scalars lists
    points = []
    scalars = []

    params = copy.deepcopy(payload)

    # Loop all values in the obtained data
    if isinstance(payload,dict):
        
        params.pop('data')

        for i, frame in enumerate(payload['data'].values()):    

            for val in frame['clutter_data'].values():

                # Append the point coordinates
                points.append(np.array([float(val['center_xy'][0]),-float(val['center_xy'][1]),-i*dist_between_frames]))

                # Add the wanted scalar
                try:
                    if scalar_type == 'feature_congestion':
                        scalars.append(val['feature_congestion'])

                    elif scalar_type == 'subband_entropy':
                        scalars.append(val['subband_entropy'])
                        
                    elif scalar_type == 'grouping_complexity':
                        scalars.append(val['grouping_complexity'])
                except KeyError:
                    scalars.append(0)
   
    # Scale the scalars to fit fully within [0,1]
    #scalars = force_within_range(scalars)
  
    # Set all the scalars that are below the threshold to 0
    scalars = apply_threshold(scalars, scalar_threshold)

    # Remove all points with scalars set to 0
    # TODO: fix this. Just a quick implementation
    indexes_to_remove = []
    for i, s in enumerate(scalars):
        if s == 0:
            indexes_to_remove.append(i)

    """if len(indexes_to_remove) != 0:
        indexes_to_remove.pop(0)"""
    
    for index in sorted(indexes_to_remove, reverse=True):
        del points[index]    
        del scalars[index]  

    return np.array(points), np.array(scalars), params 


###################################################
#////////////////--- Rendering ---/////////////////

def add_plotter_cube(
        plotter:pv.Plotter,
        cube_dims,
        color:str='white',
        style:str='wireframe',
        line_width:int=2
        ):
    """
    Basically just the plotter.add_mesh() method, but with
    an easier to use interface were only the needed
    parameters are inclueded
    """
    actor = plotter.add_mesh(
        pv.Cube(
            center=(cube_dims[0]/2,-cube_dims[1]/2,-cube_dims[2]/2),
            x_length=cube_dims[0],
            y_length=cube_dims[1],
            z_length=cube_dims[2]),
        color=color,
        style=style,
        line_width=line_width)

    return actor

def add_plotter_points(
        plotter:pv.Plotter,
        points,
        scalars,
        render_points_as_spheres:bool=True,
        style:str='points_gaussian',
        cmap=cmocean.cm.thermal,
        emissive:bool=False,
        rgba:bool=False,
        point_size:int=10
        ):
    """
    Basically just the plotter.add_points() method, but with
    an easier to use interface were only the needed
    parameters are inclueded
    """
    if len(points) == 0:
        return
    """
    cloud = pv.PolyData(points)
    surf = cloud.delaunay_2d()
    actor = plotter.add_mesh(surf, color=True, show_edges=True)
    """

    actor = plotter.add_points(
        points,
        render_points_as_spheres=render_points_as_spheres,
        style=style,
        cmap=cmap,
        emissive=emissive,
        scalars=scalars,
        rgba=rgba,
        point_size=point_size,
        show_scalar_bar=True,
        scalar_bar_args= {'label_font_size':10,'outline':False})

    return actor


def set_plotter_parameters(
        plotter:pv.Plotter,
        bg_color:str='#000000',
        cam_pos:str='xy',
        cam_zoom=1.0,
        cam_rotation=(45,15,0),
        add_axes:bool=True,
        reset_cam_orientation:bool=False
        ):
    """
    Sets some stuff. Need to be improved.
    """
    # Set a background color
    plotter.set_background(bg_color, top='#2c2438')

    # Add some text to the plot
    plotter.add_text('AdvancedHCI_project',font_size=6, color='w')

    if reset_cam_orientation:

        # Set the default camera view position and orientation
        plotter.camera_position = cam_pos

        # Set a default initial camera rotation
        plotter.camera.azimuth = cam_rotation[0]
        plotter.camera.elevation = cam_rotation[1]
        plotter.camera.roll = cam_rotation[2]

    # Set an intial camera zoom
    plotter.camera.zoom(cam_zoom)

    # Add the xyz-axes visible in the lower left
    if add_axes:
        plotter.add_axes()


##############################################
#////////////////--- Main ---/////////////////

def test_main():

    #-------------------
    # Plotting parameters
    num_points_per_frame = 20
    frame_dimensions = (1024,768)
    num_frames = 50
    dist_between_frames = 50
    num_neighbors = 4
    scalar_threshold = 0.5
    #-------------------

    #-------------------
    # Create all the points
    points = create_3d_points(
        num_points_per_frame=num_points_per_frame,
        frame_dimensions=frame_dimensions,
        num_frames=num_frames,
        dist_between_frames=dist_between_frames)

    # Create all the scalars for each point
    scalars = create_nn_scalars(
        points,
        num_neighbors=num_neighbors,
        scalar_threshold=scalar_threshold)

    #-------------------
    # Create a pyvista plotting object
    plotter = pv.Plotter(shape=(1, 1))
    plotter.subplot(0, 0)

    # Add the points to the plot
    add_plotter_points(plotter,points,scalars)

    # Add a cube around the points to the plot
    add_plotter_cube(plotter,(frame_dimensions[0],frame_dimensions[1],num_frames*dist_between_frames))

    # NOTE: set parameters after adding everything to the plotter
    set_plotter_parameters(plotter,reset_cam_orientation=True)

    # Display everything added to the plot
    plotter.show()

if __name__ == "__main__":
    test_main()








