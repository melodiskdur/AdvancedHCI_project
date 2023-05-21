import sys

# Setting the Qt bindings for QtPy
import os
os.environ["QT_API"] = "pyqt5"

from qtpy import QtWidgets, QtCore, QtGui

# pip install pyqt5-tools
# python -m pip install PyQt5

import numpy as np
import math
import copy

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
        
        # Essential parameters
        self.frame_dimensions = (1280,720)
        self.num_frames = 1
        self.dist_between_frames = 0
        self.scalar_threshold = 8
        self.wireframe = True
        self.gaussian_points = True
        self.emissive_points = False
        self.render_points_as_spheres = True
        self.point_size = 10

        # Intialize the data points and scalars
        self.points = None
        self.scalars = None
        # TODO: specify folder instead of a single file (or add both options)
        self.json_filepath = 'F:/Kursmaterial/AdvancedHCI/test_frame_10x20.json'
        self.points, self.scalars = pvt.get_frame_ps_json(file_path=self.json_filepath, scalar_threshold=self.scalar_threshold)
        self.scalar_range = (min(list(self.scalars)),max(list(self.scalars)))
        
        #--------- TEST ---------
        # Test parameters
        self.num_points_per_frame = 1
        self.num_neighbors = 0

        # Test case
        #self.load_points()
        #self.load_scalars()
        #------------------------
    
    def set_filepath(self,path:str):
        self.json_filepath = path
    
    def set_render_points_as_spheres(self,s:bool):
        self.render_points_as_spheres = s
    
    def set_wireframe(self, s:bool):
        self.wireframe = s
    
    def set_gaussian_points(self, s:bool):
        self.gaussian_points = s
        
    def set_emissive_points(self, s:bool):
        self.emissive_points = s
    
    def set_point_size(self,size:int):
        self.point_size = size
    
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
        if val < 0: val = 0
        self.dist_between_frames = val

    def set_num_neighbors(self,val:int):
        if val <= 0: val = 1
        self.num_neighbors = val
    
    def set_scalar_threshold(self,sc):
        if sc < math.floor(self.scalar_range[0]): sc = 0
        elif sc > math.ceil(self.scalar_range[1]): sc = 1
        self.scalar_threshold = sc

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
        hlayout = QtWidgets.QHBoxLayout()

        #Add the pyvista interactor object
        self.plotter = QtInteractor(self.main_plot.frame)
        hlayout.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)
        
        #Set the frames layout of the main plot
        self.main_plot.frame.setLayout(hlayout)
        

        #Add the main plots frame as the central widget
        self.setCentralWidget(self.main_plot.frame)

        #---------- Create all the widgets etc ----------

        self._create_actions()      # Actions used by widgets (not buttons)

        self._create_menus()        # Menubar atop of the application

        self._create_buttons()      # Buttons with actions

        self._create_toolbars()     # Movable objects containing widgets

        self._create_statusbar()    # Displays helpful messages
        
        #---------- Create the parameter field and add some sliders/spinboxes/checkboxes ----------
        
        # Parameter layout
        param_vlayout = QtWidgets.QVBoxLayout()
        
        # Sliders
        scalar_threshold_slider = self.create_vbox_slider(
            range=(math.floor(self.main_plot.scalar_range[0]),math.ceil(self.main_plot.scalar_range[1])),
            init_value=int(self.main_plot.scalar_threshold),
            label_text='Scalar Threshold: ',
            set_method=self.main_plot.set_scalar_threshold)
        
        num_frames_slider = self.create_vbox_slider(
            range=(1,10),
            init_value=int(self.main_plot.num_frames),
            label_text='Num Frames: ',
            set_method=self.main_plot.set_num_frames)
        
        dist_between_frames_slider = self.create_vbox_slider(
            range=(0,100),
            init_value=int(self.main_plot.dist_between_frames),
            tick_interval=10,
            label_text='Dist Frames: ',
            set_method=self.main_plot.set_dist_between_frames)
        
        point_size_slider = self.create_vbox_slider(
            range=(0,80),
            init_value=int(self.main_plot.point_size),
            tick_interval=5,
            label_text='Point Size: ',
            set_method=self.main_plot.set_point_size)
        
        
        # Checkboxes
        wireframe_cb = self.create_checkbox(
            title="Wireframe",
            status=True,
            change_method=self.checkbox_state)
        
        gaussian_points_cb = self.create_checkbox(
            title = "Gaussian",
            status=True,
            change_method=self.checkbox_state)
        
        emissive_points_cb = self.create_checkbox(
            title = "Emissive",
            status=False,
            change_method=self.checkbox_state)
        
        sphere_points_cb = self.create_checkbox(
            title = "Spherical",
            status=True,
            change_method=self.checkbox_state)
        
        # Add the checkboxes to theier own layout    
        cb_vlayout = QtWidgets.QVBoxLayout()
        cb_vlayout.setContentsMargins(20,0,0,0)
        cb_vlayout.addWidget(wireframe_cb)
        cb_vlayout.addWidget(gaussian_points_cb)
        cb_vlayout.addWidget(emissive_points_cb)
        cb_vlayout.addWidget(sphere_points_cb)
        
        # TODO: fix a proper inputfield
        # Input field 
        inputfield_vlayout = QtWidgets.QVBoxLayout()
        nameLabel = QtWidgets.QLabel()
        nameLabel.setText('Filepath')
        
        if_hlayout = QtWidgets.QHBoxLayout()
        inputfield = QtWidgets.QLineEdit()
        inputfield.setText(self.main_plot.json_filepath)
        if_button = self.create_button(lambda: self.change_filepath(inputfield),'Load File')
        if_hlayout.addWidget(inputfield)
        if_hlayout.addWidget(if_button)
        
        inputfield_vlayout.addWidget(nameLabel)
        inputfield_vlayout.addLayout(if_hlayout)
        
        
        # Add everything to the parameter layout
        param_vlayout.addLayout(inputfield_vlayout)
        param_vlayout.addLayout(scalar_threshold_slider)
        param_vlayout.addLayout(num_frames_slider)
        param_vlayout.addLayout(dist_between_frames_slider)
        param_vlayout.addLayout(point_size_slider)
        param_vlayout.addLayout(cb_vlayout)
        

        # Add the parameter layout to the main layout
        hlayout.addLayout(param_vlayout,0)

        """self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setValue(self.main_plot.scalar_threshold)
        self.spinbox.valueChanged.connect(self.change_scalar_threshold_spin)
        self.spinbox.setFocusPolicy(QtCore.Qt.NoFocus)
        loadToolBar.addWidget(self.spinbox)"""

        #---------- Load our main plot and show the application ----------
        pvt.set_plotter_parameters(self.plotter,reset_cam_orientation=True)
        self.load_main_plot()

        # Show the application window
        if show:
            self.show()

    #==========================================================================
    #/////////////////////-- Essential Setup Methods --////////////////////////
    #==========================================================================
    
    # TODO: move this
    def change_filepath(self, inputfield:QtWidgets.QLineEdit):
        self.main_plot.set_filepath(copy.copy(inputfield.text()))
        self.load_main_plot()
        
    # TODO: move this. Reactor. No hardcoding
    def checkbox_state(self, checkbox:QtWidgets.QCheckBox):
        
        status = checkbox.isChecked()
        
        if checkbox.text() == "Wireframe":
            self.main_plot.set_wireframe(status)
	
        elif checkbox.text() == "Gaussian":
            self.main_plot.set_gaussian_points(status)
        
        elif checkbox.text() == "Emissive":
            self.main_plot.set_emissive_points(status)
        
        elif checkbox.text() == "Spherical":
            self.main_plot.set_render_points_as_spheres(status)
        
        self.load_main_plot()
            

    def _create_menus(self):
        """create all the menus and submenus"""
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

    def create_vbox_slider(self,range:tuple[int,int]=(0,10),init_value:int=0,tick_interval:int=1,label_text:str='N: ', set_method=None):
        """create a vbox layout with a slider and label"""
        
        # Create the vertical box layout
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setAlignment(QtCore.Qt.AlignTop)

        # Create the slide label
        slider_label = QtWidgets.QLabel()
        slider_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                 QtWidgets.QSizePolicy.Fixed))
        slider_label.setContentsMargins(3,0,3,0)
        slider_label.setFixedHeight(20)
        slider_label.setText(f'{label_text}{init_value}')
        
        # Create the slider and connect it to its method
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                 QtWidgets.QSizePolicy.Fixed))
        slider.setContentsMargins(3,0,3,5)
        slider.setFixedSize(150,30)
        slider.setRange(range[0],math.ceil(range[1]/tick_interval))
        
        #slider.setSingleStep(1)
        slider.setTickInterval(tick_interval)
        slider.setValue(math.ceil(init_value/tick_interval))
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow) 

        if set_method != None:   
            slider.valueChanged.connect(lambda: self.change_mainplot_param(set_method,tick_interval,slider_label,label_text))

        # Add the widgets created to the layout
        vlayout.addWidget(slider_label,0,alignment=QtCore.Qt.AlignTop)
        vlayout.addWidget(slider,0,alignment=QtCore.Qt.AlignTop)
        
        return vlayout

    def add_menu_item(self,menu,action):
        """add a menu item/add an action"""
        menu.addAction(action)
    
    def create_checkbox(self, title:str='TITLENAME',status:bool=False,change_method=None):
        """create a checkbox widget"""
        cb = QtWidgets.QCheckBox(title)
        cb.setChecked(status)
        cb.stateChanged.connect(lambda: change_method(self.sender()))
        return cb
    
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
    
    def load_main_plot(self, _=False): # Dont remove _=False. An action always return False
        """load our main plot to the pyqt frame"""
        # Clear the screen
        self.plotter.clear()
        
        # Get the points and scalars from the json file
        self.main_plot.points, self.main_plot.scalars = pvt.get_frame_ps_json(file_path=self.main_plot.json_filepath, scalar_threshold=self.main_plot.scalar_threshold)

        # Add the points to the plot
        pvt.add_plotter_points(
            self.plotter, 
            self.main_plot.points, 
            self.main_plot.scalars, 
            emissive=self.main_plot.emissive_points, 
            style='points'+('_gaussian' if self.main_plot.gaussian_points else ''),
            render_points_as_spheres=self.main_plot.render_points_as_spheres,
            point_size=self.main_plot.point_size)
        
        if self.main_plot.wireframe:
            # Add a cube around the points to the plot
            pvt.add_plotter_cube(self.plotter,(self.main_plot.frame_dimensions[0],self.main_plot.frame_dimensions[1],(self.main_plot.num_frames - 1)*self.main_plot.dist_between_frames))
        
        # Set the plotter parameters (camera,background etc)
        pvt.set_plotter_parameters(self.plotter)

        # Reset the camera
        self.plotter.reset_camera()
        
    def change_mainplot_param(self, set_method=None, value_scalar=1, label_widget:QtWidgets.QLabel=None, label_text:str=None): # Dont remove _=False. An action always return False
        """change the some parameter in our main plot"""
        # getting current value
        value = round(self.sender().value()*value_scalar,3)
  
        if label_widget != None and label_text != None:
            label_widget.setText(f'{label_text}{value}')
 
        set_method(value)
        
        # setting value of spin box to the label
        self.load_main_plot()
        
    


def run_application():
    """run our application"""
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    run_application()