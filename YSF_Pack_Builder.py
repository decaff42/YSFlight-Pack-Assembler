#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 22:35:04 2024

@author: Decaff42


This code provides a GUI program to build LST files for aircraft, ground objects and sceneries.


It assumes the following:
    (1) The pack file structure is already created and all the files are properly located.
    (2) TBD

"""


__title__ = "YSFlight Pack Builder"
__version__ = "0.1.0"
__author__ = "Decaff42"
__copyright__ = "2024 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""


# Import standard Python Modules
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import os



def main():
    root = Tk()
    root.withdraw()

    LSTBuilderGUI(root, __title__, __version__, __author__, __copyright__)

    root.deiconify()
    root.mainloop()


class LSTBuilderGUI(Frame):
    def __init__(self, parent, title, version, author, copyright_notice):
        super().__init__(parent)
        self.title = title
        self.parent = parent
        self.version = version
        self.author = author
        self.copyright_notice = copyright_notice

        # Define filepaths that the user selects for the lst contents - These are Absolute Paths
        self.aircraft_paths = ['', '', '', '', '']
        self.ground_paths = ['', '', '', '', '']
        self.scenery_paths = ['', '', '']

        # Aircraft paths
        self.air_dat_fpath = StringVar()
        self.air_visual_fpath = StringVar()
        self.air_collision_fpath = StringVar()
        self.air_cockpit_fpath = StringVar()
        self.air_coarse_fpath = StringVar()

        # Ground Object paths
        self.gnd_dat_fpath = StringVar()
        self.gnd_visual_fpath = StringVar()
        self.gnd_collision_fpath = StringVar()
        self.gnd_cockpit_fpath = StringVar()
        self.gnd_coarse_fpath = StringVar()

        # Scenery paths
        self.sce_fld_path = StringVar()
        self.sce_stp_path = StringVar()
        self.sce_mission_path = StringVar()
        self.scenery_airrace = IntVar(value=0)

        # Define lists that hold aircraft, ground and scenery names for the listboxes
        self.air_listbox_names = list()
        self.gnd_listbox_names = list()
        self.sce_listbox_names = list()

        # Define the output pack directory
        self.PackDirectory = StringVar(value = os.getcwd())  # Default to where this code is run from.

        # Define where the models are located
        self.WorkingDirectory = StringVar(value = os.getcwd())  # default to where this code is run from.
        
        # Define names that the user will input at various points
        self.SceneryName = StringVar()
        self.UserName = StringVar()
        self.PackName = StringVar()

        # Define storage of the different LST file contents
        self.AircraftContents = list()
        self.GroundContents = list()
        self.SceneryConntents = list()
                
        # Define the LST Mode and options.
        self.LstMode = StringVar(value="Aircraft")  # other options are Scenery and Ground
        self.lst_mode_options = ['Aircraft', 'Ground', 'Scenery']              
        
        # Define the filetype options for the file selection gui, based on the allowable filetype.
        filetypes = dict()
        filetypes['srf'] = [("SRF File", "*.srf")]
        filetypes['dat'] = [("DAT File", "*.dat")]
        filetypes['dnm'] = [("DynaModel File", "*.dnm")]
        filetypes['stp'] = [("Start Position File", "*.stp")]
        filetypes['fld'] = [("Scenery File", "*.fld")]
        filetypes['yfs'] = [("Mission File", "*.yfs")]
        self.filetypes = filetypes

        # Define prompts for the file selection dialogs
        prompts = dict()
        prompts['Aircraft'] = ["Select The Aircraft's DAT File",
                               "Select The Aircraft's Visual Model FIle",
                               "Select The Aircraft's Collision Model File",
                               "Select the Aircraft's Cockpit Model File",
                               "Select The Aircraft's Coarse Model File"]
        prompts['Ground'] = ["Select The Ground Object's DAT File",
                             "Select The Ground Object's Visual Model FIle",
                             "Select The Ground Object's Collision Model File",
                             "Select The Ground Object's Cockpit Model File",
                             "Select The Ground Object's Coarse Model File"]
        prompts['Scenery'] = ["Select The Scenery's FLD File",
                              "Select The Scenery's Start Position File",
                              "Select The Scenery's Mission File"]
        self.prompts = prompts        
        
        # Define which files are required for a valid LST entry. Use None to fill in gaps so that all
        # definitions have the same length to avoid potential issues in the future.
        required_files = dict()
        required_files['Aircraft'] = [True, True, True, False, False]
        required_files['Scenery'] = [True, True, False, None, None]
        required_files['Ground'] = [True, True, True, False, False]
        self.required_files = required_files
        
        # Define Labels that should appear in the GUI for the various 
        labels = dict()
        labels['Aircraft'] = ['DAT', 'Visual Model', 'Collision', 'Cockpit', 'Coarse']
        labels['Ground'] = ['DAT', 'Visual Model', 'Collision', 'Cockpit', 'Coarse']
        labels['Scenery'] = ['Map', 'Start Position', 'Mission', '', '']
        self.labels = labels

        # Define the allowable file types for the different positions.
        # Make sure every element is a list so that they can all be parsed the same
        # way in the "select file" function.
        lst_filetypes = dict()
        lst_filetypes['Aircraft'] = [['dat'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf']]
        lst_filetypes['Ground'] = [['dat'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf']]
        lst_filetypes['Scenery'] = [['fld'], ['stp'], ['yfs'], [], []]
        self.lst_filetypes = lst_filetypes
        
        
        
        # Setup the GUI
        self.gui_setup()
        
        
    def gui_setup(self):
        """Create the User Interface"""
        # Window Title
        self.parent.wm_title(__title__ + " v" + __version__)
        
        # Window Geometry Controls
        self.parent.wm_resizable(width=True, height=True)
        self.parent.minsize(self.parent.winfo_width() + 150, self.parent.winfo_height() + 150)
        
        # Window Order
        self.parent.wm_attributes('-topmost', 1)
        
        # Setup the Frames
        MainFrame = Frame()        
        #
        # Setup the Pack Frame
        #

        # Define the place for the user to input:
        #  - The Pack's name
        #  - Where the files are located
        #  - Where the Pack should be assembled on their computer
        #  - What the name of their folder in the User folder should bev
        PackFrame = LabelFrame(MainFrame, text="Pack Details")
        row_num = 0
        Label(PackFrame, text="Pack Name:").grid(row=row_num, column=0, sticky="W")
        Entry(PackFrame, textvariable=self.PackName, width=40).grid(row=row_num, column=1, sticky="WE")
        # TODO impliment gui element <leave> to validate the pack name could be part of the valid filestructure [aA-zZ][0-9][_-]

        row_num += 1
        Label(PackFrame, text="User Name:").grid(row=row_num, column=0, sticky="W")
        Entry(PackFrame, textvariable=self.UserName, width=40).grid(row=row_num, column=1, sticky="WE")
        # TODO impliment gui element <leave> to validate the username could be part of the valid filestructure [aA-zZ][0-9][_-]
        
        row_num += 1
        Label(PackFrame, text="Modding Directory:").grid(row=row_num, column=0, sticky="W")
        Entry(PackFrame, textvariable=self.WorkingDirectory, width=40).grid(row=row_num, column=1)
        Button(PackFrame, text="Select").grid(row=row_num, column=2)

        row_num += 1
        Label(PackFrame, text="Output Directory:").grid(row=row_num, column=0, sticky="W")
        Entry(PackFrame, textvariable=self.PackDirectory, width=40).grid(row=row_num, column=1)
        Button(PackFrame, text="Select").grid(row=row_num, column=2)

        # Start a notebook to hold aircraft, ground object and scenery inputs
        Notebook = ttk.Notebook(MainFrame)

        # Build the aircraft Tab
        AircraftFrame = Frame(Notebook)

        # Aircraft Preview Section
        AircraftPreviewFrame = Frame(AircraftFrame)
        AircraftListFrame = Frame(AircraftPreviewFrame)
        air_listbox = Listbox(AircraftListFrame, width=20, height=15, font=("Helvetica",12), selectmode='SINGLE')
        air_listbox.pack(side="left")
        air_scrollbar = ttk.Scrollbar(AircraftListFrame, orient='vertical')
        air_scrollbar.configure(command=air_listbox.yview)
        air_scrollbar.pack(side='right', fill='y')
        AircraftListFrame.pack(side="top")
        
        AircraftPreviewButtonFrame = Frame(AircraftPreviewFrame)
        Button(AircraftPreviewButtonFrame, text="Edit").grid(row=0, column=0, sticky="NSWE")  #TODO Add Command
        Button(AircraftPreviewButtonFrame, text="Delete").grid(row=0, column=1, sticky="NSWE")  #TODO Add Command
        AircraftPreviewButtonFrame.pack(side='bottom')
        AircraftPreviewFrame.pack(side="left")
        
        # Aircraft Edit Section         
        AircraftEditFrame = Frame(AircraftFrame)
        AircraftEditButtonFrame = Frame(AircraftEditFrame)

        
        AircraftFrame.pack()
        

        # Build the Ground Object Tab
        GroundFrame = Frame(Notebook)
        GroundPreviewFrame = Frame(GroundFrame)
        GroundPreviewButtonFrame = Frame(GroundPreviewFrame)
        GroundEditFrame = Frame(GroundFrame)
        GroundEditButtonFrame = Frame(GroundEditFrame)
        

        # Build the Scenery Tab
        SceneryFrame = Frame(Notebook)
        SceneryPreviewFrame = Frame(SceneryFrame)
        SceneryPreviewButtonFrame = Frame(SceneryPreviewFrame)  
        SceneryEditFrame = Frame(SceneryFrame)
        SceneryEditButtonFrame = Frame(SceneryEditFrame)
              
        
        # Add the Aircraft, Ground Object and Scenery Frames to the Note Book
        Notebook.add(AircraftFrame, text='Aircraft')
        Notebook.add(GroundFrame, text='Ground Objects')
        Notebook.add(SceneryFrame, text='Scenery')

        # Pack up the frames
        MainFrame.pack()
        PackFrame.pack()
        Notebook.pack(expand=True, fill='both')
        
        
        

    def update_lst_type(self):
        pass

        # Assign Appropriate labels for the filepath inputs, add * if required

        # Determine which fields can be disabled based on the lst filetype selection

        # Disable Buttons that should not be used
        
        
        
    
    def select_pack_directory(self):
        """Have the user select the pack directory, with the standard sub folders for aircraft, user, etc"""
        prompt = "Please select the folder where you have built your addon package."



    def select_file(self, file_position):
        """Select the file for the indicated position."""
        # Get the prompt
        prompt = self.prompts[self.LstMode.get()][file_position]

        # Get the filetypes that are allowed for this position.
        gui_filetype = list() 
        ftype = self.lst_filetypes[self.LstMode.get()][file_position] # returns list of 0 - n elements
        for filetype in ftype:
            if filetype.lower() in self.filetypes.keys():
                gui_filetype.append(self.filetypes[filetype.lower()])

        gui_filetypes.append([("All Files", "*.*")])  # Always give the user an option to select all files.

        # Get the filepath using GUI
        path = filedialog.askdirectory(parent=parent, title=prompt, initialdir=starting_directory, filetypes=gui_filetype)

        # Set the filepath if a valid filepath is returned.
        # TODO:  figure out if there is a better way to handle this.
        if isinstance(path, str) and path != "":
            if file_position == 0:
                self.filepath1.set(path)
            elif file_position == 1:
                self.filepath2.set(path)
            elif file_position == 2:
                self.filepath3.set(path)
            elif file_position == 3:
                self.filepath4.set(path)
            elif file_position == 4:
                self.filepath5.set(path)

    
       
    
class AircraftElement:
    def __init__(self):
        # Define filepaths to the various files.
        self.dat = ""  
        self.visual = ""
        self.collision = ""
        self.coarse = ""
        self.cockpit = ""

    def load_lst(self, line):
        """Parse an lst file line into an aircraft element"""


    def assign(self, dat, visual, collision, cockpit, coarse):
        self.dat = dat
        self.visual = visual
        self.collision = collision
        self.cockpit = cockpit
        self.coarse = coarse

    
    
        
        
        
        
if __name__ == "__main__":
    main()
    
