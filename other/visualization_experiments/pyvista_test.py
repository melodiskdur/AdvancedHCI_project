import numpy as np
import pyvista as pv
from sklearn.neighbors import NearestNeighbors
import cmocean

#################################################
#////////////////--- Helpers ---/////////////////

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
    max_s = max(list(scalars))
    scalars = [s / max_s for s in scalars]

    # Set all the scalars that are below the threshold to 0
    scalars = [(0 if s < scalar_threshold else s) for s in scalars]

    return np.array(scalars)

def create_3d_points(
        num_points_per_frame:int=100, 
        frame_dimensions:tuple[int,int]=(10,8), 
        num_frames:int=10, 
        dist_between_frames:int=1,):
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

###################################################
#////////////////--- Rendering ---/////////////////

def add_plotter_cube(plotter:pv.Plotter,
                     cube_dims:tuple[int,int,int],
                     color:str='white',
                     style:str='wireframe',
                     line_width:int=2):
    """
    Basically just the plotter.add_mesh() method, but with
    an easier to use interface were only the needed 
    parameters are inclueded
    """
    actor = plotter.add_mesh(
        pv.Cube(
            center=(cube_dims[0]/2,cube_dims[1]/2,-cube_dims[2]/2),
            x_length=cube_dims[0],
            y_length=cube_dims[1],
            z_length=cube_dims[2]), 
        color=color, 
        style=style, 
        line_width=line_width)
    
    return actor

def add_plotter_points(plotter:pv.Plotter,
                       points,
                       scalars,
                       render_points_as_spheres:bool=True,
                       style:str='points_gaussian',
                       cmap=cmocean.cm.thermal,
                       emissive:bool=False,
                       rgba:bool=False,
                       point_size:int=10):
    """
    Basically just the plotter.add_points() method, but with
    an easier to use interface were only the needed 
    parameters are inclueded
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
        bg_color:str='k',
        cam_pos:str='xy',
        cam_zoom=1.0,
        cam_rotation:tuple[int,int,int]=(45,15,0),
        add_axes:bool=True,
        reset_cam_orientation:bool=False
        ): 
    """
    Sets some stuff. Need to be improved.
    """
    # Set a background color
    plotter.background_color = bg_color

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

    

    
    



