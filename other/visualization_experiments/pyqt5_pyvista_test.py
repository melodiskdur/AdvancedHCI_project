import sys

# Setting the Qt bindings for QtPy
import os
os.environ["QT_API"] = "pyqt5"

from qtpy import QtWidgets, QtCore, QtGui # pip install pyqt5-tools

import numpy as np

import pyvista as pv
from pyvistaqt import QtInteractor, MainWindow
import pyvista_test as pvt


class MainPlot():
    """
    The main plot, containing the points and scalars as 
    well as some defined parameters. This also contains the QFrame
    which will be the central widget in MyMainWindow.
    """
    def __init__(self):
        # Create the frame
        self.frame = QtWidgets.QFrame()
        self.points = None
        self.scalars = None

        self.num_points_per_frame = 20
        self.frame_dimensions = (1024,768)
        self.num_frames = 50
        self.dist_between_frames = 50
        self.num_neighbors = 4
        self.scalar_threshold = 0.5

        self.load_points()
        self.load_scalars()
    
    def set_num_points_per_frame(self,val):
        if val < 0: val = 0
        self.num_points_per_frame = val

    def set_frame_dimensions(self,dims:tuple[int,int]):
        if dims[0] < 0 or dims[1] < 0: dims = (0,0)
        self.frame_dimensions = dims

    def set_num_frames(self,val):
        if val < 0: val = 0
        self.num_frames = val
    
    def set_dist_between_frames(self,val):
        if val <= 0: val = 1
        self.dist_between_frames = val

    def set_num_neighbors(self,val:int):
        if val <= 0: val = 1
        self.num_neighbors = val
    
    def set_scalar_threshold(self,val:float):
        if val < 0: val = 0
        elif val > 1: val = 1
        self.scalar_threshold = val

    def load_points(self):
        self.points = pvt.create_3d_points(  
            num_points_per_frame=self.num_points_per_frame,
            frame_dimensions=self.frame_dimensions,
            num_frames=self.num_frames,
            dist_between_frames=self.dist_between_frames)
        
    def load_scalars(self):    
        self.scalars = pvt.create_nn_scalars(
            self.points, 
            self.num_neighbors,
            self.scalar_threshold)


class MyMainWindow(MainWindow):
    """
    The main window, basically the whole application
    """
    def __init__(self, parent=None, show=True):
        QtWidgets.QMainWindow.__init__(self, parent)

        #---------- Setup the main frame ----------
        #Create the main plot
        self.main_plot = MainPlot()
        vlayout = QtWidgets.QVBoxLayout()

        #Add the pyvista interactor object
        self.plotter = QtInteractor(self.main_plot.frame)
        vlayout.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)

        #Set the frames layout of the main plot
        self.main_plot.frame.setLayout(vlayout)
        

        #Add the main plots frame as the central widget
        self.setCentralWidget(self.main_plot.frame)

        #---------- Create the actions, toolbars and statusbars ----------
        self._create_actions()

        self._create_buttons()

        self._create_toolbars()

        self._create_statusbar()

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMaximumSize(100,20)
        self.slider.setRange(0,20)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(5)
        self.slider.setValue(self.main_plot.num_neighbors)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)        
        self.slider.valueChanged.connect(self.change_num_neighbors_slider)
  
        self.main_plot.frame.layout().addWidget(self.slider)

        self.result_label = QtWidgets.QLabel(f'N: {self.slider.value()}', self)
        self.main_plot.frame.layout().addWidget(self.result_label)

        """self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setValue(self.main_plot.num_neighbors)
        self.spinbox.valueChanged.connect(self.change_num_neighbors_spin)
        self.spinbox.setFocusPolicy(QtCore.Qt.NoFocus)
        loadToolBar.addWidget(self.spinbox)"""

        #---------- Set up the applications menu ----------
        # Add a main menubar
        mainMenu = self.menuBar()

        #---------------- 
        # Add a menu to the menubar called File
        fileMenu = mainMenu.addMenu('&File')

        # Add the exitbutton the the file menu
        fileMenu.addAction(self.exit_program_action)

        #---------------- 
        # Add a menu to the menubar called File
        viewMenu = mainMenu.addMenu('&View')

        self.add_menu_item(viewMenu,self.full_screen_action)

        self.add_menu_item(viewMenu,self.max_screen_action)

        self.add_menu_item(viewMenu,self.normal_screen_action)

        self.add_menu_item(viewMenu,self.min_screen_action)

        #----------------
        # Add a load menu
        loadMenu = mainMenu.addMenu('&Load')

        # Allow adding our plot
        self.add_menu_item(loadMenu, self.load_main_plot_action)

        #------
        # Add an example-meshes menu
        examplemeshesMenu = loadMenu.addMenu("Example Meshes")

        # Allow adding a sphere
        self.add_menu_item(examplemeshesMenu, self.load_sphere_action)

        # Allow adding a cube
        self.add_menu_item(examplemeshesMenu, self.load_cube_action)

        #----------------
        # Add a help menu
        helpMenu = mainMenu.addMenu('&Help')

        # Allow adding our plot
        self.add_menu_item(helpMenu, self.help_commands_action)

        #---------- Load our main plot and show the application ----------
        pvt.set_plotter_parameters(self.plotter,reset_cam_orientation=True)
        self.load_main_plot()

        # Show the application window
        if show:
            self.show()

    #==========================================================================
    #/////////////////////-- Essential Setup Methods --////////////////////////
    #==========================================================================

    def _create_actions(self):
        """create all the actions we will use"""
        # File Actions
        self.exit_program_action = self.create_action('Exit',self.close,shortcut='Ctrl+Q',tip='Exit the application and close the window')

        # View Actions
        self.full_screen_action = self.create_action('Full',self.showFullScreen,shortcut='Ctrl+F',tip='Set the application-window to full screen')
        self.max_screen_action = self.create_action('Maximize',self.showMaximized,shortcut='Ctrl+B',tip='Maximize the application-window')
        self.normal_screen_action = self.create_action('Normal',self.showNormal,shortcut='Ctrl+N',tip='Set the application-window to its normal size')
        self.min_screen_action = self.create_action('Minimize',self.showMinimized,shortcut='Ctrl+M',tip='Minimize the application-window')
        
        # Load Actions
        self.load_sphere_action = self.create_action('Load Sphere',self.load_sphere,tip='Cleans the frame and loads a sphere')
        self.load_cube_action = self.create_action('Load Cube',self.load_cube,tip='Cleans the frame and loads a cube')
        self.load_main_plot_action = self.create_action('Load Main Plot',self.load_main_plot,shortcut='Ctrl+R',tip='Cleans the frame and loads our plot')

        # Help Actions
        self.help_commands_action = self.create_action('Pyvista Commands',self.show_popup,tip='Show some useful keyboard commands for moving the meshes')

    def _create_buttons(self):
        """create all the buttons we will use"""
        self.load_main_plot_btn = self.create_button(self.load_main_plot,'Load Main Plot')
        self.load_sphere_btn = self.create_button(self.load_cube,'Load Cube')
        self.load_cube_btn = self.create_button(self.load_sphere,'Load Sphere')

    def _create_toolbars(self):
        """create all the toolbars and their widgets"""
        loadToolBar = QtWidgets.QToolBar("&Load", self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,loadToolBar)

        loadToolBar.addWidget(self.load_sphere_btn)
        loadToolBar.addWidget(self.load_cube_btn)
        loadToolBar.addWidget(self.load_main_plot_btn)
    
    def _create_statusbar(self):
        """create the statusbar"""
        self.statusbar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Hello there", 3000)

    #=================================================================
    #/////////////////////-- Helper methods --////////////////////////
    #=================================================================

    def add_menu_item(self,menu,action):
        """add a menu item/add an action"""
        menu.addAction(action)
    
    def create_button(self,method,name:str='button'):
        """create a button with a name and associated method"""
        btn = QtWidgets.QPushButton()
        btn.setText(name)
        btn.clicked.connect(method)
        return btn
        
    def create_action(self,name,method,shortcut=None,tip=None):
        """create an action"""
        # Create a new action
        action = QtWidgets.QAction(name, self)

        # Add a tip for the action
        if tip:
            action.setStatusTip(tip)
            action.setToolTip(tip)

        # Add a shortcut for the action
        if shortcut:
            action.setShortcut(shortcut)

        # Add what method is used for the action
        action.triggered.connect(method)

        return action

    #=================================================================
    #/////////////////////-- Action Methods --////////////////////////
    #=================================================================

    def show_popup(self, _=False):
        """method used to show a popup info displaying command information"""
        self.help_command_message = QtWidgets.QMessageBox()
        self.help_command_message.setWindowTitle("Pyvista Commands")
    
        self.help_command_message.setText("Ctrl -> Rotate the camera around the view direction\nShift -> Translate active mesh/object\nCtrl + Shift -> Translate the camera along the view direction")

        self.help_command_message.setDetailedText("42")

        self.help_command_message.buttonClicked.connect(self.popup_button)

        self.help_command_message.exec_()

    def popup_button(self, i):
        """when a button in show_popup is pressed"""
        #print(i.text())
        pass
            
    def load_sphere(self, _=False): # Dont remove _=False. An action always return False
        """ add a sphere to the pyqt frame """
        self.plotter.clear()
        sphere = pv.Sphere()
        self.plotter.add_mesh(sphere, show_edges=True)

        pvt.set_plotter_parameters(self.plotter)

        self.plotter.reset_camera()

    def load_cube(self, _=False): # Dont remove _=False. An action always return False
        """ add a cube to the pyqt frame """
        self.plotter.clear()

        cube = pv.Cube()
        self.plotter.add_mesh(cube, show_edges=True)

        pvt.set_plotter_parameters(self.plotter)

        self.plotter.reset_camera()
    
    def load_main_plot(self, _=False, new_scalars = True): # Dont remove _=False. An action always return False
        """load our main plot to the pyqt frame"""
        # Clear the screen
        self.plotter.clear()

        if new_scalars:
            self.main_plot.load_points()
            
        self.main_plot.load_scalars()

        # Add the points to the plot
        pvt.add_plotter_points(self.plotter,self.main_plot.points,self.main_plot.scalars)

        # Add a cube around the points to the plot
        pvt.add_plotter_cube(self.plotter,(self.main_plot.frame_dimensions[0],self.main_plot.frame_dimensions[1],self.main_plot.num_frames*self.main_plot.dist_between_frames))
        
        # Set the plotter parameters (camera,background etc)
        pvt.set_plotter_parameters(self.plotter)

        # Reset the camera
        self.plotter.reset_camera()
        

    def change_num_neighbors_spin(self, _=False): # Dont remove _=False. An action always return False
        """change the number of neighbors in our main plot with the spinbox"""
        # getting current value
        value = self.spinbox.value()

        self.result_label.setText(f'N: {value}')

        self.main_plot.set_num_neighbors(value)
        # setting value of spin box to the label
        self.load_main_plot(new_scalars=False)

    def change_num_neighbors_slider(self, _=False): # Dont remove _=False. An action always return False
        """change the number of neighbors in our main plot with the slider"""
        # getting current value
        value = self.slider.value()

        self.result_label.setText(f'N: {value}')

        self.main_plot.set_num_neighbors(value)
        # setting value of spin box to the label
        self.load_main_plot(new_scalars=False)




def run_application():
    """run our application"""
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    run_application()