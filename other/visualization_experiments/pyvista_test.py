import numpy as np
import pyvista as pv
from sklearn.neighbors import NearestNeighbors
import threading
from pynput import keyboard


################################################
#////////////////--- Globals ---/////////////////

# TODO: remove globals if possible
default_view = 'xy'
reset_view = False


#####################################################################
#////////////////--- Hotkeys and their functions ---/////////////////

# Define all the hotkeys
HOTKEYS = {'<ctrl>+r': lambda : reset_camera_view('<ctrl>+r'),
            '<ctrl>+z': lambda : function_1('<ctrl>+z'),
            '<ctrl>+x': lambda : function_2('<ctrl>+x')}

def reset_camera_view(hotkey):
    global default_view
    global reset_view
    #print('Executed reset_camera_view:',hotkey)
    default_view = 'xy'
    reset_view = True

def function_1(hotkey):
    #print('Executed function_1:',hotkey)
    pass

def function_2(hotkey):
    #print('Executed function_2:',hotkey)
    pass


#################################################
#////////////////--- Helpers ---/////////////////

def normalize_point(p):
    return p / np.sqrt(np.sum(p**2))

def normalize_points(points):
    return np.array([normalize_point(p) for p in points])

def set_z_value(p,val):
    return np.array([p[0],p[1],val])

def set_z_values(points,val):
    return np.array([set_z_value(p,val) for p in points])

def calculate_scalars(points, num_neighbors):
    # Compute the nearest neighbors for each point
    neighbors = NearestNeighbors(n_neighbors=num_neighbors).fit(points)
    distances, _ = neighbors.kneighbors(points)

    # Calculate the scalars for the points based on the distances
    # Add a small value to prevent division by zero
    scalars = 1.0 / (distances.mean(axis=1) + 1e-6)

    return scalars

def create_points_and_scalars(num_points_per_frame:int=100,
                              frame_width:int=10,
                              frame_height:int=8,
                              num_frames:int=10,
                              dist_between_frames:int=1,
                              num_neighbors:int=6):
    """
    Create all the points and their corresponding scalars
    Input:
        num_points_per_frame: the number of points in each frame
        frame_width: the width of the frame
        frame_height: the height of the frame
        num_frames: the number of frames
        dist_between_frames: the distance between each frame in the plot
    Output:
        points: a np.array with 3d points
        scalars: a np.array with float scalars for each 3d point in points
    """

    # Initialize the points list
    points = []

    # Create points for each frame
    for i in range(num_frames):

        # Calculate some random xy values withing the width and height of the frame
        x_values = np.random.uniform(low=0.0, high=frame_width, size=num_points_per_frame)
        y_values = np.random.uniform(low=0.0, high=frame_height, size=num_points_per_frame)

        # Create points and add a specific z-value for each frame
        frame_points = np.array([np.array([x,y,-i*dist_between_frames]) for x,y in zip(x_values,y_values)])

        # Append all the points created to points
        for p in frame_points:
            points.append(p)

    # Change points to a numpy array for ease of use
    points = np.array(points)

    # Create all the scalars for each point
    scalars = np.array(calculate_scalars(points, num_neighbors=num_neighbors))

    return points, scalars


############################################
#////////////////--- IO ---/////////////////

def change_plotter_parameters(pl:pv.Plotter):
    global default_view
    global reset_view

    # If we want to reset the view ot the default
    if reset_view:
        pl.camera_position = default_view
        reset_view = False


###################################################
#////////////////--- Threading ---/////////////////

def activate_thread(target:object, args:tuple):
    # Create a thread
    thread = threading.Thread(target=target, args=args)

    # Start the thread
    thread.start()

    return thread

def deactivate_thread(thread):
    # Kill the thread
    thread.join()


###################################################
#////////////////--- Rendering ---/////////////////

def plot_data(plotter:pv.Plotter, points:list, scalars:list, width:int=10, height:int=8, num_frames:int=10, dist_between_frames:int=1):

    # NOTE: this cubemesh can be removed. Primarily for debugging
    # Add the cube mesh to encapsulate all the data/frames
    plotter.add_mesh(
        pv.Cube(
            center=(width/2,height/2,-(num_frames*dist_between_frames)/2),
            x_length=width,
            y_length=height,
            z_length=num_frames*dist_between_frames),
        color='white',
        style='wireframe',
        line_width=2)

    # Add all the points with their scalars to the plot
    plotter.add_points(
        points,
        render_points_as_spheres=True,
        style='points_gaussian',
        emissive=True,
        scalars=scalars,
        rgba=False,
        point_size=10,
        show_scalar_bar=True,
        scalar_bar_args= {'label_font_size':10,'outline':False})

    # Add some text at the top
    plotter.add_text('pyvista_test.py',font_size=6, color='w')

    # Set a background color
    plotter.background_color = 'k'

    # Set the default camera view position and orientation
    plotter.camera_position = default_view

    # Add the xyz-axes visible in the lower left
    plotter.add_axes()

    # Set an intial camera zoom
    plotter.camera.zoom(1.2)

    # Show the plot i.e. everything we have added to the plotter
    # NOTE: interactive_update is set to tru to allow plotter.update() to run
    # This way we enable handling of input fro the user when plotting
    plotter.show(interactive_update=True)

    # Continously update the window
    while True:

        # Change plot parameters depending on the users input
        change_plotter_parameters(plotter)

        # Update the window
        plotter.update()


##############################################
#////////////////--- Main ---/////////////////

if __name__ == "__main__":

    #-------------------
    # Plotting parameters
    num_points_per_frame = 20
    frame_width = 10
    frame_height = 8
    num_frames = 30
    dist_between_frames = 0.5

    #-------------------
    # Create all the points and their corresponding scalars
    points, scalars = create_points_and_scalars(num_points_per_frame,frame_width,frame_height,num_frames,dist_between_frames)

    #-------------------
    # Create a pyvista plotting object
    num_rows, num_columns = 1, 1
    plotter = pv.Plotter(shape=(num_rows, num_columns))

    # Set current subplot
    plotter.subplot(0, 0)

    #-------------------
    # Create and start a thread for plotting
    plot_thread = activate_thread(target=plot_data, args=(plotter,points,scalars,frame_width,frame_height,num_frames,dist_between_frames))

    #-------------------
    # Create and start a thread for handling input
    with keyboard.GlobalHotKeys(HOTKEYS) as input_thread:

        # NOTE: this line below can substitute the creation of plot_thread
        #plot_data(plotter,100,10,8,10)

        # Kill the input thread
        deactivate_thread(input_thread)

    #-------------------
    #Kill the plotting thread
    deactivate_thread(plot_thread)





