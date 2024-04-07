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

import csv
import json
import sys
from pathlib import PosixPath
# Import standard Python Modules
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from dataclasses import dataclass
from enum import Enum
from typing import Union, List
import os

FILE_TYPES = {
    "srf": [("SRF File", "*.srf")],
    "dat": [("DAT File", "*.dat")],
    "dnm": [("DynaModel File", "*.dnm")],
    "stp": [("Start Position File", "*.stp")],
    "fld": [("Scenery File", "*.fld")],
    "yfs": [("Mission File", "*.yfs")]
}

def load_config():
    try:
        return json.load(open("config.json"))
    except:
        print("config.json not found, or config.json has syntax errors.", file=sys.stderr)
        return dict()


CONFIG = load_config()

def main():
    root = Tk()
    root.withdraw()

    controller = LSTBuilderGUIController()

    view = LSTBuilderGUI(root, controller, __title__, __version__, __author__, __copyright__)

    controller.set_view(controller)

    root.deiconify()
    root.mainloop()


class LSTBuilderGUIController:
    def __init__(self):

        self.aircraft_lst: LSTFile = LSTFile(lines=[], lst_type=LSTType.AIRCRAFT)
        self.ground_lst: LSTFile = LSTFile(lines=[], lst_type=LSTType.GROUND)
        self.scenery_lst: LSTFile = LSTFile(lines=[], lst_type=LSTType.SCENERY)

    def set_view(self, view):
        self.view = view


class LSTBuilderGUI(Frame):
    def __init__(self, parent, controller, title, version, author, copyright_notice):
        super().__init__(parent)
        self.title = title
        self.parent = parent
        self.version = version
        self.author = author
        self.copyright_notice = copyright_notice

        self.controller = controller

        # Define lists that hold aircraft, ground and scenery names for the listboxes
        self.air_listbox_names = list()
        self.gnd_listbox_names = list()
        self.sce_listbox_names = list()

        # Define the output pack directory
        self.PackDirectory = StringVar(value=os.path.join(os.getcwd(), "out"))  # Default to where this code is run from.

        # Define where the models are located
        self.WorkingDirectory = StringVar()  # default to where this code is run from.

        # Define names that the user will input at various points
        self.SceneryName = StringVar()
        self.UserName = StringVar()
        self.PackName = StringVar()

        # Define the aircraft and ground object name based on the DAT file.
        self.AircraftName = StringVar(value='AIRCRAFT_NAME')
        self.GroundObjectName = StringVar(value='GROUND_OBJECT_NAME')

        # Define lists of the different LST file contents
        self.air_lst_pane_lines = Variable()
        self.ground_lst_pane_lines = Variable()
        self.scenery_lst_pane_lines = Variable()

        # Define the LST Mode and options.
        self.LstMode = StringVar(value="Aircraft")  # other options are Scenery and Ground
        self.lst_mode_options = ['Aircraft', 'Ground', 'Scenery']

        self.aircraft_edit_panel = {
            'fpaths': [StringVar() for _ in range(5)],
            'prompts': [
                "Select The Aircraft's DAT File",
                "Select The Aircraft's Visual Model FIle",
                "Select The Aircraft's Collision Model File",
                "Select the Aircraft's Cockpit Model File",
                "Select The Aircraft's Coarse Model File"
            ],
            'labels': [
                'DAT', 'Visual Model', 'Collision', 'Cockpit', 'Coarse'
            ],
            'allowed_filetypes': [
                ['dat'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf']
            ],
            "required_fields": [True, True, True, False, False]
        }
        self.ground_edit_panel = {
            'fpaths': [StringVar() for _ in range(5)],
            'prompts': [
                "Select The Ground Object's DAT File",
                "Select The Ground Object's Visual Model FIle",
                "Select The Ground Object's Collision Model File",
                "Select The Ground Object's Cockpit Model File",
                "Select The Ground Object's Coarse Model File"
            ],
            'labels': [
                'DAT', 'Visual Model', 'Collision', 'Cockpit', 'Coarse'
            ],
            'allowed_filetypes': [
                ['dat'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf']
            ],
            "required_fields": [True, True, True, False, False]
        }

        self.scenery_edit_panel = {
            'fpaths': [StringVar() for _ in range(3)],
            'prompts': [
                "Select The Scenery's FLD File",
                "Select The Scenery's Start Position File",
                "Select The Scenery's Mission File"
            ],
            "prompts": [
                'Map', 'Start Position', 'Mission'
            ],
            'labels': [
                'Map', 'Start Position', 'Mission'
            ],
            'allowed_filetypes': [
                ['fld'], ['stp'], ['yfs']
            ],
            "required_fields": [True, True, False]
        }

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

        def set_modding_directory():
            dir = self.choose_dir(prompt="Set Modding directory", start_dir=self.WorkingDirectory.get() or '.')
            if dir:
                self.WorkingDirectory.set(dir)

        Button(PackFrame, text="Select", command=set_modding_directory).grid(row=row_num, column=2)

        row_num += 1
        Label(PackFrame, text="Output Directory:").grid(row=row_num, column=0, sticky="W")
        Entry(PackFrame, textvariable=self.PackDirectory, width=40).grid(row=row_num, column=1)

        def set_output_directory():
            dir = self.choose_dir(prompt="Set output directory for pack", start_dir='.')
            if dir:
                self.PackDirectory.set(dir)

        Button(PackFrame, text="Select", command=set_output_directory).grid(row=row_num, column=2)

        # Start a notebook to hold aircraft, ground object and scenery inputs
        Notebook = ttk.Notebook(MainFrame)

        # Build the aircraft Tab
        AircraftFrame = Frame(Notebook)

        # Aircraft Preview Section
        AircraftPreviewFrame = Frame(AircraftFrame)
        AircraftListFrame = Frame(AircraftPreviewFrame)

        air_listbox = Listbox(AircraftListFrame, listvariable=self.air_lst_pane_lines, width=20, height=15, font=("Helvetica", 12), selectmode='SINGLE')
        air_listbox.pack(side="left")
        air_scrollbar = ttk.Scrollbar(AircraftListFrame, orient='vertical')
        air_scrollbar.configure(command=air_listbox.yview)
        air_scrollbar.pack(side='right', fill='y')
        AircraftListFrame.pack(side="top")

        AircraftPreviewButtonFrame = Frame(AircraftPreviewFrame)
        Button(AircraftPreviewButtonFrame, text="Edit").grid(row=0, column=0, sticky="NSWE")  # TODO Add Command
        Button(AircraftPreviewButtonFrame, text="Delete").grid(row=0, column=1, sticky="NSWE")  # TODO Add Command
        AircraftPreviewButtonFrame.pack(side='bottom')
        AircraftPreviewFrame.pack(side="left")

        # Aircraft Edit Section         
        AircraftEditFrame = Frame(AircraftFrame)
        AircraftEntryFrame = Frame(AircraftEditFrame)

        air_panel = self.aircraft_edit_panel

        row_num = 0
        Label(AircraftEntryFrame, textvariable=self.AircraftName).grid(row=row_num, column=0, columnspan=3)

        for row_num in range(5):
            Label(AircraftEntryFrame, text=air_panel['labels'][row_num]).grid(row=row_num + 1, column=0, sticky="W")
            Entry(AircraftEntryFrame, textvariable=air_panel['fpaths'][row_num], width=30).grid(row=row_num + 1,
                                                                                                column=1, sticky="WE")

            def choose_file(i):
                allowed_file_types = []
                for allowed_file_type in air_panel['allowed_filetypes'][i]:
                    allowed_file_types.extend(FILE_TYPES[allowed_file_type])

                fname = self.choose_file(prompt=air_panel['prompts'][i],
                                         allowed_filetypes=allowed_file_types,
                                         start_dir=self.WorkingDirectory.get())
                if fname:
                    air_panel['fpaths'][i].set(fname)

            Button(AircraftEntryFrame, text="Select",
                   command=lambda i=row_num: choose_file(i)).grid(row=row_num + 1, column=2, sticky="NSWE")

        AircraftEntryFrame.pack()

        AircraftEditButtonFrame = Frame(AircraftEditFrame)


        Button(AircraftEditButtonFrame, text="Save", command=lambda: self.save_item("aircraft")).grid(row=0, column=0, sticky="NSWE")
        Button(AircraftEditButtonFrame, text="Clear All Inputs").grid(row=0, column=1, sticky="NSWE")
        AircraftEditButtonFrame.pack()

        AircraftEditFrame.pack(side='right')
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


    def choose_dir(self, prompt, start_dir):
        """
        Prompts the user for a directory.
        :param prompt: Window title
        :param start_dir: Initial working directory.
        :return: Selected directory path, or None if no file was selected.
        """
        fpath = filedialog.askdirectory(parent=self, title=prompt, initialdir=start_dir)
        if not fpath:
            return
        return fpath

    def choose_file(self, prompt, allowed_filetypes, start_dir):
        """
        Prompts the user for a file.
        :param prompt: Window title
        :param allowed_filetypes: List of tuples with the allowed file types. example: [("JPEG Files", "*.jpeg")]
        :param start_dir: Initial working directory.
        :return: Selected file path, or None if no file was selected.
        """
        fpath = filedialog.askopenfilename(parent=self, title=prompt, initialdir=start_dir,
                                           filetypes=allowed_filetypes)
        if not fpath:
            return
        return fpath

    def save_item(self, frame_id):
        if frame_id == 'aircraft':
            self.controller.aircraft_lst.lines.append(
                AirLSTLine({k:self.aircraft_edit_panel['fpaths'][i] for i, k in enumerate(AirLSTLine.__dict__.keys())})
            )
            self.update_lst_pane('aircraft')


    def update_lst_pane(self, frame_id):
        if frame_id == 'aircraft':
            self.air_lst_pane_lines.set([aircraft.aircraft_name() for aircraft in self.controller.aircraft_lst.lines])
        if frame_id == 'ground':
            self.ground_lst_pane_lines.set([ground.ground_object_name() for ground in self.controller.ground_lst.lines])
        if frame_id == 'scenery':
            self.scenery_lst_pane_lines.set([scenery.name for scenery in self.controller.scenery_lst.lines])

    def set_controller(self, controller):
        self.controller = controller

    # def update_lst_type(self):
    #     pass
    #
    #     # Assign Appropriate labels for the filepath inputs, add * if required
    #
    #     # Determine which fields can be disabled based on the lst filetype selection
    #
    #     # Disable Buttons that should not be used

    # def select_pack_directory(self):
    #     """Have the user select the pack directory, with the standard sub folders for aircraft, user, etc"""
    #     prompt = "Please select the folder where you have built your addon package."

    # def select_file(self, file_position, mode):
    #     """Select the file for the indicated position.
    #
    #     Inputs
    #     file_position (int): an integer of range 0-4 that indicates what position in the LST File the file being selected is for
    #     mode (str): 'Aircraft', 'Ground', 'Scenery'
    #
    #     Outputs
    #     None - This function will set the appropriate variables in the class.
    #
    #     """
    #
    #     # Validate inputs:
    #     if isinstance(file_position, int) is True:
    #         if file_position < 0 or file_position > 4:
    #             raise ValueError("{} Found that input [file_position] was not 0-4".format(__name__))
    #     else:
    #         raise TypeError("{} Expects input [file_position] to be an integer".format(__name__))
    #
    #     if isinstance(mode, str) is True:
    #         if mode in self.lst_mode_options is False:
    #             raise ValueError(
    #                 "{} Found that input [mode] was not 'Aircraft', 'Ground', or 'Scenery'".format(__name__))
    #     else:
    #         raise TypeError("{} Expects input [mode] to be a string".format(__name__))
    #
    #     # Get the prompt
    #     prompt = self.prompts[mode][file_position]
    #
    #     # Get the filetypes that are allowed for this position.
    #     gui_filetype = list()
    #     ftype = self.lst_filetypes[self.LstMode.get()][file_position]  # returns list of 0 - n elements
    #     for filetype in ftype:
    #         if filetype.lower() in self.filetypes.keys():
    #             gui_filetype.append(self.filetypes[filetype.lower()])
    #
    #     gui_filetype.append([("All Files", "*.*")])  # Always give the user an option to select all files.
    #
    #     # Get the filepath using GUI
    #     path = filedialog.askdirectory(parent=self, title=prompt, initialdir=starting_directory,
    #                                    filetypes=gui_filetype)
    #
    #     # Validate the path
    #     if isinstance(path, str) is False:
    #         return
    #     else:
    #         if path == "":
    #             return
    #
    #     # Set the appropriate variables
    #
    #     # Set the filepath if a valid filepath is returned.
    #     # TODO:  figure out if there is a better way to handle this.
    #     if isinstance(path, str) and path != "":
    #         if file_position == 0:
    #             self.filepath1.set(path)
    #         elif file_position == 1:
    #             self.filepath2.set(path)
    #         elif file_position == 2:
    #             self.filepath3.set(path)
    #         elif file_position == 3:
    #             self.filepath4.set(path)
    #         elif file_position == 4:
    #             self.filepath5.set(path)


"""

============== Utilities ================

"""


def determine_lst_type_from_filename(path: os.PathLike):
    filename = os.path.split()[-1]

    fname, ext = os.path.splitext(filename)
    if ext.lower() != "lst":
        raise ValueError(f"File with location {path} must have the file extension '.lst'")

    if filename.lower().startswith("air"):
        return LSTType.AIRCRAFT
    if filename.lower().startswith("gro"):
        return LSTType.GROUND
    if filename.lower().startswith("sce"):
        return LSTType.SCENERY
    else:
        raise ValueError(f"Could not determine type of LST file with path {path}. "
                         f"LST file names MUST start with 'air', 'gro' or 'sce'.")


def lst_serialize(attribute):
    """
    Helper function for serializing entries of an LSTLine object.
    :param attribute: attribute to serialize.
    :return: serialized attribute.
    """
    if attribute is None or attribute == "":
        return ""
    elif isinstance(attribute, os.PathLike):
        return PosixPath(attribute)
    elif isinstance(attribute, str):
        return attribute
    else:
        raise ValueError(f"Could not perform lst file serialization for attribute {attribute}")


"""
================ LST Classes ===================
"""


@dataclass
class AirLSTLine:
    """
    Aircraft LST Line

    Models a single line of an Aircraft LST file.

    Parameters:
        dat:
          The aircraft dat file.
        dnm:
          The aircraft dnm file.
        collision_srf:
          The aircraft collision srf file.
        cockpit_srf:
          The aircraft cockpit srf file. Not required.
        coarse_dnm:
          The aircraft coarse dnm file. Not required.
        aircraft_name:
          The aircraft name. A tuple of datfile and aircraft name. Used as a caching object.
    """
    dat: os.PathLike
    dnm: os.PathLike
    collision_srf: os.PathLike
    cockpit_srf: os.PathLike = None
    coarse_dnm: os.PathLike = None
    _aircraft_name = None

    def get_csv_line(self):
        return [lst_serialize(a) for a in self.__dict__.keys()]

    def aircraft_name(self):
        self._aircraft_name = (None, None)
        if self._aircraft_name and self._aircraft_name[0] == self.dat:
            return self._aircraft_name[1]
        else:
            with open(self.dat, 'r') as f:
                for line in f:
                    if line.startswith("IDENTIFY"):
                        aircraft_name = line.removeprefix("IDENTIFY").strip().removeprefix("\"").removesuffix("\"")
                        self._aircraft_name = (self.dat, aircraft_name)
                        return aircraft_name
            raise ValueError(f"Could not determine aircraft name from datfile {self.dat}")


@dataclass
class GroundLSTLine:
    """
    Ground LST Line

    Models a single line of a Ground LST file.

    Parameters:
        dat:
          The ground object dat file.
        dnm:
          The ground object dnm file.
        collision_srf:
          The ground object collision srf file.
        cockpit_srf:
          The ground object cockpit srf file. Not required.
        coarse_dnm:
          The ground object coarse dnm file. Not required.

    """

    dat: os.PathLike
    dnm: os.PathLike
    collision_srf: os.PathLike
    cockpit_srf: os.PathLike = None
    coarse_dnm: os.PathLike = None
    _ground_object_name = None

    def get_csv_line(self):
        return [lst_serialize(a) for a in self.__dict__.keys()]



    def ground_object_name(self):
        self._ground_object_name = (None, None)
        if self._ground_object_name and self._ground_object_name[0] == self.dat:
            return self._ground_object_name[1]
        else:
            with open(self.dat, 'r') as f:
                for line in f:
                    if line.startswith("IDENTIFY"):
                        ground_object_name = line.removeprefix("IDENTIFY").strip().removeprefix("\"").removesuffix("\"")
                        self._ground_object_name = (self.dat, ground_object_name)
                        return ground_object_name
            raise ValueError(f"Could not determine ground object name from datfile {self.dat}")




@dataclass
class SceneryLSTLine:
    """
    Scenery LST Line

    Models a single line of a Scenery LST file.

    """
    name: str
    fld: os.PathLike
    stp: os.PathLike
    mission_file: os.PathLike = None
    game_mode: str = ''

    def get_csv_line(self):
        return [lst_serialize(a) for a in self.__dict__.keys()]


class LSTType(Enum):
    AIRCRAFT = 'Aircraft'
    GROUND = 'Ground'
    SCENERY = 'Scenery'


class LSTFile:
    def __init__(self, lines: Union[List[AirLSTLine], List[GroundLSTLine], List[SceneryLSTLine]],
                 lst_type: LSTType = None) -> None:
        if len(lines) == 0 and lst_type is None:
            raise ValueError("Must set LST file type if no lines are provided.")
        elif len(lines) > 0:
            if isinstance(lines[0], AirLSTLine) and lst_type is not None and lst_type != LSTType.AIRCRAFT:
                raise ValueError("Aircraft lines were provided but declared as type: {}".format(lst_type))
            elif isinstance(lines[0], GroundLSTLine) and lst_type is not None and lst_type != LSTType.GROUND:
                raise ValueError("Ground lines were provided but declared as type: {}".format(lst_type))
            elif isinstance(lines[0], SceneryLSTLine) and lst_type is not None and lst_type != LSTType.SCENERY:
                raise ValueError("Scenery lines were provided but declared as type: {}".format(lst_type))

        self.lines = lines

    @staticmethod
    def from_file(filepath: os.PathLike):

        lst_type = determine_lst_type_from_filename(filepath)

        with open(filepath, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file, delimiter=" ", quotechar="\"")

            lines = []

            for line_number, line in enumerate(csv_reader):
                try:
                    if len(line) == 0:
                        continue  # Empty line, skip
                    if lst_type == LSTType.AIRCRAFT:
                        lines.append(AirLSTLine(**line))
                    elif lst_type == LSTType.GROUND:
                        lines.append(GroundLSTLine(**line))
                    elif lst_type == LSTType.SCENERY:
                        lines.append(SceneryLSTLine(**line))
                    else:
                        raise ValueError(f"Unrecognized LST type: {lst_type}")
                except ValueError as e:
                    raise ValueError(f"Fatal error when reading file '{filepath}', line {line_number + 1}: {e.message}")
            return LSTFile(lines=lines, lst_type=lst_type)

    def write_file(self, filepath: os.PathLike):
        with open(filepath, "w", encoding="utf-8") as file:
            csv_writer = csv.writer(file, delimiter=" ", quotechar="\"", quoting=csv.QUOTE_ALL)

            csv_writer.writerows([line.get_csv_line() for line in self.lines])


if __name__ == "__main__":
    main()
