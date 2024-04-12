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
from dataclasses import dataclass
from enum import Enum
from pathlib import PosixPath
import csv
import string



def main():
    root = Tk()
    root.withdraw()

    PackBuilderGUI(root, __title__, __version__, __author__, __copyright__)

    root.deiconify()
    root.mainloop()


class PackBuilderGUI(Frame):
    def __init__(self, parent, title, version, author, copyright_notice):
        super().__init__(parent)
        self.title = title
        self.parent = parent
        self.version = version
        self.author = author
        self.copyright_notice = copyright_notice

        # Define filepaths that the user selects for the lst contents - These are Absolute Paths
        self.current_paths = {'Aircraft':[StringVar()] * 5, 'Ground':[StringVar()] * 5, 'Scenery':[StringVar()] * 3}
        # self.current_paths['Aircraft'][0].set('/')

        # Define lists that hold aircraft, ground and scenery names for the listboxes
        self.air_listbox_names = list()
        self.gnd_listbox_names = list()
        self.sce_listbox_names = list()

        # Define the output pack directory
        self.PackDirectory = StringVar(value = os.path.abspath(os.sep))

        # Define where the models are located
        self.WorkingDirectory = StringVar(value = os.path.abspath(os.sep)) 
        
        # Define names that the user will input at various points
        self.SceneryName = StringVar()
        self.UserName = StringVar()
        self.PackName = StringVar()
        self.SceneryAirRace = IntVar(value=0)

        # Define the aircraft and ground object name based on the DAT file.
        self.AircraftName = StringVar(value='AIRCRAFT_NAME')
        self.GroundObjectName = StringVar(value='GROUND_OBJECT_NAME')

        # Define storage of the different LST file contents
        self.AircraftContents = list()
        self.GroundContents = list()
        self.SceneryConntents = list()
                
        # Define the the lst options
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
        self.PackNameEntry = Entry(PackFrame, textvariable=self.PackName, width=40)
        self.PackNameEntry.grid(row=row_num, column=1, sticky="WE")
        self.PackNameEntry.bind('<FocusOut>', lambda e: self.validate_pack_username(e, 'PackName'))
        # TODO impliment gui element <leave> to validate the pack name could be part of the valid filestructure [aA-zZ][0-9][_-]

        row_num += 1
        Label(PackFrame, text="User Name:").grid(row=row_num, column=0, sticky="W")
        self.UserNameEntry = Entry(PackFrame, textvariable=self.UserName, width=40)
        self.UserNameEntry.grid(row=row_num, column=1, sticky="WE")
        self.UserNameEntry.bind('<FocusOut>', lambda e: self.validate_pack_username(e, 'UserName'))
        # TODO impliment gui element <leave> to validate the username could be part of the valid filestructure [aA-zZ][0-9][_-]
        
        row_num += 1
        Label(PackFrame, text="Modding Directory:").grid(row=row_num, column=0, sticky="W")
        Entry(PackFrame, textvariable=self.WorkingDirectory, width=40).grid(row=row_num, column=1)
        Button(PackFrame, text="Select", command=self.select_working_directory).grid(row=row_num, column=2)

        row_num += 1
        Label(PackFrame, text="Output Directory:").grid(row=row_num, column=0, sticky="W")
        Entry(PackFrame, textvariable=self.PackDirectory, width=40).grid(row=row_num, column=1)
        Button(PackFrame, text="Select", command=self.select_pack_directory).grid(row=row_num, column=2)

        # Start a notebook to hold aircraft, ground object and scenery inputs
        Notebook = ttk.Notebook(MainFrame)

        #
        # Build the aircraft Tab
        #
        # This is where the user will select the dat, visual, collission, cockpit, and coarse models for
        # an aircraft lst line item.
        AircraftFrame = Frame(Notebook)

        # Aircraft Preview Section
        AircraftPreviewFrame = Frame(AircraftFrame)
        AircraftListFrame = Frame(AircraftPreviewFrame)
        air_listbox = Listbox(AircraftListFrame, width=30, height=10, font=("Helvetica",12), selectmode='SINGLE')
        air_listbox.pack(side="left")
        air_yscrollbar = ttk.Scrollbar(AircraftListFrame, orient='vertical')
        air_yscrollbar.configure(command=air_listbox.yview)
        air_yscrollbar.pack(side='right', fill='y')
        
        air_xscrollbar = ttk.Scrollbar(AircraftListFrame, orient='horizontal')
        air_xscrollbar.configure(command=air_listbox.xview)
        air_yscrollbar.pack(side='bottom', fill='x')
        
        AircraftListFrame.pack(side="top")
        
        AircraftPreviewButtonFrame = Frame(AircraftPreviewFrame)
        Button(AircraftPreviewButtonFrame, text="Edit").grid(row=0, column=0, sticky="NSWE")  #TODO Add Command
        Button(AircraftPreviewButtonFrame, text="Delete").grid(row=0, column=1, sticky="NSWE")  #TODO Add Command
        AircraftPreviewButtonFrame.pack(side='bottom')
        AircraftPreviewFrame.pack(side="left")
        
        # Aircraft Edit Section         
        AircraftEditFrame = Frame(AircraftFrame)
        AircraftEntryFrame = Frame(AircraftEditFrame)
        row_num = 0
        Label(AircraftEntryFrame, textvariable=self.AircraftName).grid(row=row_num, column=0, columnspan=3)

        row_num += 1
        Label(AircraftEntryFrame, text="DAT File:").grid(row=row_num, column=0, sticky="W")
        Entry(AircraftEntryFrame, textvariable=self.current_paths['Aircraft'][0], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(AircraftEntryFrame, text="Select", command=lambda: self.select_file(0, 'Aircraft')).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Label(AircraftEntryFrame, text="DNM File:").grid(row=row_num, column=0, sticky="W")
        Entry(AircraftEntryFrame, textvariable=self.current_paths['Aircraft'][1], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(AircraftEntryFrame, text="Select", command=lambda: self.select_file(1, 'Aircraft')).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Label(AircraftEntryFrame, text="Collision File:").grid(row=row_num, column=0, sticky="W")
        Entry(AircraftEntryFrame, textvariable=self.current_paths['Aircraft'][2], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(AircraftEntryFrame, text="Select", command=lambda: self.select_file(2, 'Aircraft')).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Label(AircraftEntryFrame, text="Cockpit File:").grid(row=row_num, column=0, sticky="W")
        Entry(AircraftEntryFrame, textvariable=self.current_paths['Aircraft'][3], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(AircraftEntryFrame, text="Select", command=lambda: self.select_file(3, 'Aircraft')).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Label(AircraftEntryFrame, text="Coarse File:").grid(row=row_num, column=0, sticky="W")
        Entry(AircraftEntryFrame, textvariable=self.current_paths['Aircraft'][4], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(AircraftEntryFrame, text="Select", command=lambda: self.select_file(4, 'Aircraft')).grid(row=row_num, column=2, sticky="NSWE")
        AircraftEntryFrame.pack()

        
        AircraftEditButtonFrame = Frame(AircraftEditFrame)
        Button(AircraftEditButtonFrame, text="Save").grid(row=0,column=0, sticky="NSWE")  # TODO Add Command
        Button(AircraftEditButtonFrame, text="Clear All Inputs", command=lambda: self.clear_paths('Scenery')).grid(row=0,column=1, sticky="NSWE")
        AircraftEditButtonFrame.pack()
        
        AircraftEditFrame.pack(side='right')
        AircraftFrame.pack()
        

        #
        # Build the Ground Object Tab
        #
        # This is where the user will select the dat, visual, collission, cockpit, and coarse models for
        # a ground object lst line item.
        GroundFrame = Frame(Notebook)
        
        # Ground Object Preview Section
        GroundPreviewFrame = Frame(GroundFrame)
        GroundPreviewButtonFrame = Frame(GroundPreviewFrame)

        # Ground Object Edit Section
        GroundEditFrame = Frame(GroundFrame)
        GroundEntryFrame = Frame(GroundEditFrame)
        GroundEditButtonFrame = Frame(GroundEditFrame)
        

        #
        # Build the Scenery Tab
        #
        # This is where the user will input a scenery name and select an fld, stp, and optional yfs file.
        SceneryFrame = Frame(Notebook)

        # Scenery Preview Selection
        SceneryPreviewFrame = Frame(SceneryFrame)
        SceneryPreviewButtonFrame = Frame(SceneryPreviewFrame)


        # Scenery Edit Selection
        SceneryEditFrame = Frame(SceneryFrame)
        SceneryEntryFrame = Frame(SceneryEditFrame)

        row_num = 0
        Label(SceneryEntryFrame, text="Scenery Name:").grid(row=row_num, column=0, sticky='W')
        Entry(SceneryEntryFrame, textvariable=self.SceneryName).grid(row=row_num, column=1, columnspan=2, sticky='WE')

        row_num += 1
        Label(SceneryEntryFrame, text="FLD File:").grid(row=row_num, column=0, sticky="W")
        Entry(SceneryEntryFrame, textvariable=self.current_paths['Scenery'][0], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(SceneryEntryFrame, text="Select", command=lambda: self.select_file(0, 'Scenery')).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Label(SceneryEntryFrame, text="Start Position File:").grid(row=row_num, column=0, sticky="W")
        Entry(SceneryEntryFrame, textvariable=self.current_paths['Scenery'][1], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(SceneryEntryFrame, text="Select", command=lambda: self.select_file(1, 'Scenery')).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Label(SceneryEntryFrame, text="Mission File:").grid(row=row_num, column=0, sticky="W")
        Entry(SceneryEntryFrame, textvariable=self.current_paths['Scenery'][2], width=30).grid(row=row_num, column=1, sticky="WE")
        Button(SceneryEntryFrame, text="Select", command=lambda: self.select_file(2, 'Scenery')).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Checkbutton(SceneryEntryFrame, text="YSFlight 2018+ Air Race Map?", variable=self.SceneryAirRace, onvalue=1, offvalue=0).grid(row=row_num, column=1, sticky='w')

        SceneryEntryFrame.pack()
        

        
        SceneryEditButtonFrame = Frame(SceneryEditFrame)
        Button(SceneryEditButtonFrame, text="Save").grid(row=0,column=0, sticky="NSWE")  # TODO Add Command
        Button(SceneryEditButtonFrame, text="Clear All Inputs", command=lambda: self.clear_paths('Scenery')).grid(row=0,column=1, sticky="NSWE")
        SceneryEditButtonFrame.pack()
        
        SceneryEditFrame.pack(side='right')
        SceneryFrame.pack()
              
        
        # Add the Aircraft, Ground Object and Scenery Frames to the Note Book
        Notebook.add(AircraftFrame, text='Aircraft')
        Notebook.add(GroundFrame, text='Ground Objects')
        Notebook.add(SceneryFrame, text='Scenery')

        # Pack up the frames
        MainFrame.pack()
        PackFrame.pack(expand=True, fill='y')
        Notebook.pack(expand=True, fill='both')
        
        

    def update_air_gnd_label(self, zone, datfilepath):
        """This function will be called to update the aircraft or ground object title
        label at the top of the Aircraft and Ground Object Edit Frames.

        Assumptions:
        - The datfilepath has already been validated as a datfile

        inputs
        zone (str): 'Aircraft' or 'Ground'
        datfilepath (str): os.path-like to where the dat file for the aircraft or ground object is located.

        outputs
        None - This function executes and will set the appropriate variables in the class
        """

        # Import DAT File
        dat = list()
        with open(datfilepath, mode='r') as dat_file:
            dat = dat_file.readlines()

        # Find aircraft/ground object name
        identify_idx = 0
        for line in dat:
            if line.startswith("IDENTIFY"):
                break
            identify_idx += 1

        # Remove unnecessary parts
        name = dat[identify_idx][8:]
        if '#' in name:
            name = name.split('#')[0]
        if '"' in name:
            name = name.split('"')[1]

        # Set the variable names
        if zone == 'Aircraft':
            self.AircraftName.set(name)
        elif zone == 'Ground':
            self.GroundObjectName.set(name)
                
    def validate_pack_username(self, event, mode):
        """Validate the packname and username to ensure they are compatible with windows/mac/linux systems

        Inputs
        event (event): Tkinter event needed to run this function. NOT USED IN FUNCTION.
        mode (str): "UserName" or "PackName"

        Outputs
        None - This function executes and will set the appropriate variables in the class
        """
        valid_chars = string.ascii_letters + string.digits + " _-.[]()+"

        # Identify the name
        name = None
        if mode == 'UserName':
            name = self.UserName.get()
        elif mode == 'PackName':
            name = self.PackName.get()

        if isinstance(name, str):
            # Determine if bad characters are present
            okay_name = True
            bad_chars = list()
            if len(name) > 0:
                for character in name:
                    if character not in valid_chars:
                        okay_name = False
                        bad_chars.append(character)
                    
            if okay_name is False:
                # Clean up the name:
                for character in bad_chars:
                    name = name.replace(character, "")
                    
                # Assign the name
                if mode == "UserName":
                    self.UserName.set(name)
                elif mode == "PackName":
                    self.PackName.set(name)

                # Alert the user of the issue.
                title = "Invalid characters detected in {}".format(mode)
                info = "Tthe following invalid characters were removed from the {}:\n{}".format(mode, "".join(bad_chars))
                messagebox.showinfo(parent=self.parent, title=title, message=info)

    def edit_aircraft_lst_entry(self):
        """Allow the user to edit the selected aircraft entry in the aircraft listbox."""

        # Check to make sure that the user has selected something in the aircraft listbox.

        # If the user has entries in the aircraft filepaths in the GUI, then we need to verify that the
        # user wants to clear the inputs and load the selected aircraft LST entry.

        # Clear the aircraft entries - Use the same function as the clear input function

        # Assign the different filepaths for the aircraft to the GUi variables.


    def clear_paths(self, mode, ask=True):
        """Clear the aircraft, ground object, or scenery filepath entries.

        inputs
        mode (str): 'Aircraft', 'Ground', or 'Scenery'
        ask (boolean): a boolean to force the user to confirm they want to clear filepath entries.

        outputs
        None - This function executes and will set the appropriate variables in the class
        """

        # Validate inputs. These should never trigger unless we have not 
        # properly set up the command calls for the select file buttons.
        if isinstance(mode, str) is True:
            if mode in self.lst_mode_options is False:
                raise ValueError("{} Found that input [mode] was not 'Aircraft', 'Ground', or 'Scenery'".format(__name__))
        else:
            raise TypeError("{} Expects input [mode] to be a string".format(__name__))

        if isinstance(ask, bool) is False:
            raise TypeError("{} Expects input [ask] to be a Boolean".format(__name__))

        # Determine if there are any currently loaded paths that we should ask the user if
        # they want to delete them.
        paths = self.current_paths[mode]
        if any([True for path in paths if len(path.get()) > 0]) or ask is True:
            # Ask the user if they reeaaaaaallly want to delete all the paths.
            prompt = "Are you sure you want to delete all of the {} filepaths you have entered?".format(mode)
            title = "Delete all {} Filepaths?".format(mode)

            answer = mesagebox.askquestion(parent=self.parent, title=title, message=prompt)

            if answer is False or answer is None:
                return   

        # Clear filepath inputs
        self.current_paths[mode] = [StringVar()] * len(self.current_paths[mode])  # Account for the 5 vs 3 length difference

    def select_pack_directory(self):
        """Have the user select where they want their addon package to be assembled.
        
        Inputs
        - None - The function is only called from one location

        Outputs
        - None - This function will set the appropriate class variable.
        """
        prompt = "Select the Directory where you want to assemble your addon package."
        path = Filedialog.askdirectory(parent=self.parent, title=prompt, mustexist=True, initialdir = self.os.getcwd())

        # Validate the path
        if isinstance(path, str) is False:
            return
        else:
            if path == "":
                return

        # Set the appropriate variable
        self.PackDirectory.set(path)

    def select_working_directory(self):
        """Have the user select where they want their their WIP files are
        
        Inputs
        - None - The function is only called from one location

        Outputs
        - None - This function will set the appropriate class variable.
        """
        prompt = "Select the Directory where you have your modding files."
        path = Filedialog.askdirectory(parent=self.parent, title=prompt, mustexist=True, initialdir = self.os.getcwd())

        # Validate the path
        if isinstance(path, str) is False:
            return
        else:
            if path == "":
                return

        # Set the appropriate variable
        self.WorkingDirectory.set(path)

    def select_file(self, file_position, mode):
        """Select the file for the indicated position.

        Inputs
        file_position (int): an integer of range 0 to 4 that indicates what position in the LST File the file being selected is for
        mode (str): 'Aircraft', 'Ground', or 'Scenery'

        Outputs
        None - This function will set the appropriate variables in the class.
        
        """

        # Validate inputs. These should never trigger unless we have not 
        # properly set up the command calls for the select file buttons.
        if isinstance(file_position, int) is True:
            if file_position < 0 or file_position > 4:
                raise ValueError("{} Found that input [file_position] was not 0-4".format(__name__))
        else:
            raise TypeError("{} Expects input [file_position] to be an integer".format(__name__))

        if isinstance(mode, str) is True:
            if mode in self.lst_mode_options is False:
                raise ValueError("{} Found that input [mode] was not 'Aircraft', 'Ground', or 'Scenery'".format(__name__))
        else:
            raise TypeError("{} Expects input [mode] to be a string".format(__name__))

        if mode == 'Scenery' and file_position > 2:
            # Scenery lst lines only have 3 filepaths.
            raise ValueError("{} Was expecting input [file_position] to be 0-2 for [mode]='Scenery'".format(__name__))
        
        # Get the prompt
        prompt = self.prompts[mode][file_position]

        # Get the filetypes that are allowed for this position.
        gui_filetypes = list() 
        ftype = self.lst_filetypes[mode][file_position] # returns list of 0 - n elements
        for filetype in ftype:
            if filetype.lower() in self.filetypes.keys():
                gui_filetypes.append(self.filetypes[filetype.lower()][0])

        gui_filetypes.append(("All Files", "*.*"))  # Always give the user an option to select all files.

        print(gui_filetypes)

        # Get the filepath using GUI
        path = filedialog.askopenfilename(parent=self.parent, title=prompt, initialdir=self.WorkingDirectory.get(), filetypes=gui_filetypes)

        # Validate the path
        if isinstance(path, str) is False:
            return
        else:
            if path == "":
                return

        # Set the appropriate variable
        self.current_paths[mode][file_position].set(path)

        # Update the aircraft and ground object names
        if mode in ['Aircraft', 'Ground'] and path.endswith(".dat") and file_position == 0:
            self.update_air_gnd_label(mode, path)


    

        
if __name__ == "__main__":
    main()
    
