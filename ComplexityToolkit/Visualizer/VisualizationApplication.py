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
import PyvistaWrapper as pvw
import cmocean

class MainPlot():
    """
    The main plot, containing the points and scalars as 
    well as some defined parameters. This also contains the QFrame
    which will be the central widget in MyMainWindow.
    """
    def __init__(self):
        # Create the frame
        self.frame = QtWidgets.QFrame()
        
        #-----------
        self.dist_between_frames = 10
        self.point_size = 5
        self.scalar_threshold = 0

        #-----------
        self.wireframe = True
        self.gaussian_points = True
        self.emissive_points = True
        self.render_points_as_spheres = True
        
        #-----------
        self.json_filepath = 'H:/Kursmaterial/AdvancedHCI/Presentation/Final/Data/GroupingData/NewDelhi1_Annotated_p_complexities.json'
        self.scalar_type = "grouping_complexity"

        #-----------
        self.points, self.scalars, params = pvw.get_video_data(
            scalar_type=self.scalar_type,
            file_path=self.json_filepath, 
            scalar_threshold=self.scalar_threshold,
            dist_between_frames=self.dist_between_frames)
        
        #-----------
        if params != None:
            self.frame_dimensions = (params['image_width'],params['image_height'])
            self.num_frames = params['number_of_frames']
            #self.dimensions = params['dimensions']
            #self.folder_name = params['folder_name']
        else:
            self.frame_dimensions = (1,1)
            self.num_frames = 0
            #self.dimensions = (1,1)
            #self.folder_name = ""
        
        #----------- 
        if len(self.scalars) != 0:
            self.scalar_range = (min(list(self.scalars)),max(list(self.scalars)))
            #self.scalar_threshold = min(list(self.scalars))
        else:
            self.scalar_range = (0,1)
            
        
        #--------- TEST ---------
        # Test parameters
        self.num_points_per_frame = 1
        self.num_neighbors = 0

        # Test case
        #self.load_points()
        #self.load_scalars()
        #------------------------
        
    def set_scalar_type(self,stype:str):
        self.scalar_type = stype
    
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
        self.points = pvw.create_3d_points(  
            num_points_per_frame=self.num_points_per_frame,
            frame_dimensions=self.frame_dimensions,
            num_frames=self.num_frames,
            dist_between_frames=self.dist_between_frames)
        
    def load_scalars(self):    
        self.scalars = pvw.create_nn_scalars(
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
        param_vlayout.setAlignment((QtCore.Qt.AlignTop))
        
        #---------------
        # Sliders
        scalar_threshold_vbox_slider = self.create_vbox_slider(
            range=(math.floor(self.main_plot.scalar_range[0]),math.ceil(self.main_plot.scalar_range[1])),
            init_value=int(self.main_plot.scalar_threshold),
            tick_interval=1,
            label_text='Scalar Threshold: ',
            set_method=self.main_plot.set_scalar_threshold)
        
        num_frames_vbox_slider = self.create_vbox_slider(
            range=(1,self.main_plot.num_frames),
            init_value=self.main_plot.num_frames,
            label_text='Num Frames: ',
            set_method=self.main_plot.set_num_frames)
        
        dist_between_frames_vbox_slider = self.create_vbox_slider(
            range=(0,100),
            init_value=int(self.main_plot.dist_between_frames),
            tick_interval=5,
            label_text='Dist Frames: ',
            set_method=self.main_plot.set_dist_between_frames)
        
        point_size_vbox_slider = self.create_vbox_slider(
            range=(0,80),
            init_value=int(self.main_plot.point_size),
            tick_interval=2,
            label_text='Point Size: ',
            set_method=self.main_plot.set_point_size)
        
        #---------------
        # Checkboxes
        wireframe_cb = self.create_checkbox(
            title="Wireframe",
            status=self.main_plot.wireframe,
            change_method=self.checkbox_state)
        
        gaussian_points_cb = self.create_checkbox(
            title = "Gaussian",
            status=self.main_plot.gaussian_points,
            change_method=self.checkbox_state)
        
        emissive_points_cb = self.create_checkbox(
            title = "Emissive",
            status=self.main_plot.emissive_points,
            change_method=self.checkbox_state)
        
        sphere_points_cb = self.create_checkbox(
            title = "Spherical",
            status=self.main_plot.render_points_as_spheres,
            change_method=self.checkbox_state)
        
        # Add the checkboxes to their own layout    
        cb_vlayout = QtWidgets.QVBoxLayout()
        cb_vlayout.addWidget(wireframe_cb)
        cb_vlayout.addWidget(gaussian_points_cb)
        cb_vlayout.addWidget(emissive_points_cb)
        cb_vlayout.addWidget(sphere_points_cb)
        cb_vlayout.addWidget(self.create_line_separator())
        
        #---------------
        # Input field 
        inputfield_vbox_filepath = self.create_input_field(
            method = 'filepath',
            name='Filepath',
            max_size=(110,30),
            init_text=self.main_plot.json_filepath,
            btn_text='Load',
            btn_width=40)
        
        inputfield_vbox_scalar = self.create_input_field(
            method = 'scalar',
            name='Scalar Type',
            max_size=(110,30),
            init_text=self.main_plot.scalar_type,
            btn_text='Load',
            btn_width=40)

        
        #---------------
        # TODO: continue on this. Selection for color_map
        combobox1 = QtWidgets.QComboBox()
        combobox1.addItem('One')
        combobox1.addItem('Two')
        combobox1.addItem('Three')
        combobox1.addItem('Four')
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(combobox1)
        layout.addWidget(self.create_line_separator())

        #---------------
        # Add everything to the parameter layout
        param_vlayout.addLayout(inputfield_vbox_filepath)
        param_vlayout.addLayout(inputfield_vbox_scalar)
        param_vlayout.addLayout(scalar_threshold_vbox_slider)
        param_vlayout.addLayout(num_frames_vbox_slider)
        param_vlayout.addLayout(dist_between_frames_vbox_slider)
        param_vlayout.addLayout(point_size_vbox_slider)
        param_vlayout.addLayout(cb_vlayout)
        param_vlayout.addLayout(layout)
        
        
        # Add the parameter layout to the main layout
        hlayout.addLayout(param_vlayout,0)

        """self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setValue(self.main_plot.scalar_threshold)
        self.spinbox.valueChanged.connect(self.change_scalar_threshold_spin)
        self.spinbox.setFocusPolicy(QtCore.Qt.NoFocus)
        loadToolBar.addWidget(self.spinbox)"""

        #---------- Load our main plot and show the application ----------
        pvw.set_plotter_parameters(self.plotter,reset_cam_orientation=True)
        self.load_main_plot()

        # Show the application window
        if show:
            self.show()

    #==========================================================================
    #/////////////////////-- Essential Setup Methods --////////////////////////
    #==========================================================================
            
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

        self.statusbar.showMessage("Loading...", 3000) # Just for fun, not neccessary

    #=================================================================
    #/////////////////////-- Helper methods --////////////////////////
    #=================================================================

    def create_input_field(
            self,
            method,
            name='INPUT',
            max_size=None,
            init_text='',
            btn_text='BTN',
            btn_width=None,
            add_line_separator:bool=True):
        
        # Create the main layout for all widgets in the inputfield
        main_vbox = QtWidgets.QVBoxLayout()
        main_vbox.setAlignment((QtCore.Qt.AlignTop))

        # Create a label for the input field
        lbl = QtWidgets.QLabel()
        lbl.setText(name)
        
        # Create a horiszontal layout for the inputfield and its button
        hbox = QtWidgets.QHBoxLayout()

        # Create the inputfield
        inputfield = QtWidgets.QLineEdit()
        inputfield.setMaximumSize(max_size[0],max_size[1])
        inputfield.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                 QtWidgets.QSizePolicy.Fixed))
        inputfield.setText(init_text)

        # Create the button
        if method == 'filepath':
            btn = self.create_button(lambda: self.change_filepath(inputfield),btn_text)
        elif method == 'scalar':
            btn = self.create_button(lambda: self.change_scalar_type(inputfield),btn_text)
            
        btn.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                QtWidgets.QSizePolicy.Fixed))
        
        btn.setFixedWidth(btn_width)

        # Add the inputfield and button to the horizontal layout
        hbox.addWidget(inputfield)
        hbox.addWidget(btn)
        
        # Add the label and the howizontal layout to the main layout
        main_vbox.addWidget(lbl)
        main_vbox.addLayout(hbox)

        # Add a line_separator at the end
        if add_line_separator:
            sep_line = self.create_line_separator()
            main_vbox.addWidget(sep_line)

        return main_vbox

    def create_vbox_slider(
            self,
            range:tuple[int,int]=(0,10), 
            init_value:int=0, 
            tick_interval:int=1, 
            label_text:str='N: ',
            slider_size:tuple[int,int]=(150,30),
            set_method=None,
            add_line_separator:bool=True):
        """create a vbox layout with a slider and label"""
        
        # Create the vertical box layout
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setAlignment(QtCore.Qt.AlignTop)

        # Create the slide label
        slider_label = QtWidgets.QLabel()
        slider_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                 QtWidgets.QSizePolicy.Fixed))
        slider_label.setText(f'{label_text}{init_value}')
        
        # Create the slider and connect it to its method
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                 QtWidgets.QSizePolicy.Fixed))
        slider.setFixedSize(slider_size[0],slider_size[1])
        slider.setRange(range[0],math.ceil(range[1]/tick_interval))
        
        slider.setSingleStep(1)
        slider.setTickInterval(1)    # Not the same as the input tick_interval

        slider.setValue(math.ceil(init_value/tick_interval))
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow) 

        if set_method != None:   
            slider.valueChanged.connect(lambda: self.change_mainplot_param(set_method,tick_interval,slider_label,label_text))

        # Add the widgets created to the layout
        vlayout.addWidget(slider_label,0,alignment=QtCore.Qt.AlignTop)
        vlayout.addWidget(slider,0,alignment=QtCore.Qt.AlignTop)

        # Add a line_separator at the end
        if add_line_separator:
            sep_line = self.create_line_separator()
            vlayout.addWidget(sep_line)
        
        return vlayout

    def create_line_separator(self,line_width:int=1,color:tuple[int,int,int]=(200, 200, 200)):
        """create a line separator"""
        sep_line = QtWidgets.QFrame()
        sep_line.setFrameShape(QtWidgets.QFrame.HLine)
        sep_line.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                 QtWidgets.QSizePolicy.Fixed))
        sep_line.setLineWidth(line_width)

        pal = QtWidgets.QFrame().palette()
        pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(color[0], color[1], color[2]))
        sep_line.setPalette(pal)

        return sep_line

    def add_menu_item(self,menu,action):
        """add a menu item/add an action"""
        menu.addAction(action)
    
    def create_checkbox(self, title:str='TITLENAME',status:bool=False,change_method=None):
        """create a checkbox widget"""
        cb = QtWidgets.QCheckBox(title)
        cb.setChecked(status)
        cb.stateChanged.connect(lambda: change_method(self.sender()))
        return cb
    
    def create_button(self,method,name:str='BTN'):
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

        pvw.set_plotter_parameters(self.plotter)

        self.plotter.reset_camera()

    def load_cube(self, _=False): # Dont remove _=False. An action always return False
        """ add a cube to the pyqt frame """
        self.plotter.clear()

        cube = pv.Cube()
        self.plotter.add_mesh(cube, show_edges=True)

        pvw.set_plotter_parameters(self.plotter)

        self.plotter.reset_camera()
    
    def load_main_plot(self, _=False): # Dont remove _=False. An action always return False
        """load our main plot to the pyqt frame"""
        # Clear the screen
        self.plotter.clear()
        
        # Get the points and scalars from the json file
        self.main_plot.points, self.main_plot.scalars, params = pvw.get_video_data(
            scalar_type=self.main_plot.scalar_type,
            file_path=self.main_plot.json_filepath, 
            scalar_threshold=self.main_plot.scalar_threshold,
            dist_between_frames=self.main_plot.dist_between_frames)
        
        if params != None:
            self.main_plot.frame_dimensions = (params['image_width'],params['image_height'])
            self.main_plot.num_frames = params['number_of_frames']

        # Add the points to the plot
        pvw.add_plotter_points(
            plotter=self.plotter, 
            points=self.main_plot.points, 
            scalars=self.main_plot.scalars, 
            cmap=cmocean.cm.haline,
            emissive=self.main_plot.emissive_points, 
            style='points'+('_gaussian' if self.main_plot.gaussian_points else ''),
            render_points_as_spheres=self.main_plot.render_points_as_spheres,
            point_size=self.main_plot.point_size)
        
        if self.main_plot.wireframe:
            # Add a cube around the points to the plot
            pvw.add_plotter_cube(self.plotter,(self.main_plot.frame_dimensions[0],self.main_plot.frame_dimensions[1],(self.main_plot.num_frames - 1)*self.main_plot.dist_between_frames))
        
        # Set the plotter parameters (camera,background etc)
        pvw.set_plotter_parameters(self.plotter)

        # Reset the camera
        self.plotter.reset_camera()
        
    def change_mainplot_param(self, set_method=None, value_scalar=1, label_widget:QtWidgets.QLabel=None, label_text:str=None): # Dont remove _=False. An action always return False
        """change the some parameter in our main plot. Not filepath"""
        # Get the current value
        value = round(self.sender().value()*value_scalar,3)

        # Set the label if one is specified
        if label_widget != None and label_text != None:
            label_widget.setText(f'{label_text}{value}')

        # Use the set method to change the parameter
        set_method(value)

        # Reload the main plot
        self.load_main_plot()
    
    def change_filepath(self, inputfield:QtWidgets.QLineEdit):
        """change the filepath in our main plot"""
        # Set the filepath
        self.main_plot.set_filepath(copy.copy(inputfield.text()))

        # Reload the main plot
        self.load_main_plot()
        
    def change_scalar_type(self, inputfield:QtWidgets.QLineEdit):
        """change the scalar_type in our main plot"""
        # Set the filepath
        self.main_plot.set_scalar_type(copy.copy(inputfield.text()))

        # Reload the main plot
        self.load_main_plot()

    # TODO: fix this. Too hardcoded
    def checkbox_state(self, checkbox:QtWidgets.QCheckBox):
        """change some mainplot parameters with checkboxes"""
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
        

def run_application():
    """run our application"""
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    run_application()