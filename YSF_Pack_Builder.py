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

__title__ = "YSFlight LST File Builder"
__version__ = "0.1.0"
__author__ = "Decaff42"
__copyright__ = "2024 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""

import csv
from dataclasses import dataclass
from enum import Enum
# Import standard Python Modules
from tkinter import filedialog, messagebox
from tkinter import *
import os
from typing import Union, List

"""
================ Classes ===================
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
    """
    dat: os.PathLike
    dnm: os.PathLike
    collision_srf: os.PathLike
    cockpit_srf: os.PathLike = None
    coarse_dnm: os.PathLike = None

    def get_csv_line(self):
        return [self.a if self.a is not None else "" for a in self.__dict__.keys()]


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

    def get_csv_line(self):
        return [self.a if self.a is not None else "" for a in self.__dict__.keys()]


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
    is_airrace: bool = False

    def get_csv_line(self):
        return ([self.a if self.a is not None else "" for a in self.__dict__.keys() if not a == 'is_airrace'] +
                ['airrace' if self.is_airrace else ''])


class LSTType(Enum):
    AIRCRAFT = 'Aircraft'
    GROUND = 'Ground'
    SCENERY = 'Scenery'

class LSTFile:
    def __init__(self, lines: Union[List[AirLSTLine], List[GroundLSTLine], List[SceneryLSTLine]], lst_type: LSTType = None) -> None:
        if len(lines) == 0 and lst_type is None:
            raise ValueError("Must set LST file type if no lines are provided.")
        if isinstance(lines[0], AirLSTLine) and lst_type is not None and lst_type != LSTType.AIRCRAFT:
            raise ValueError("Aircraft lines were provided but declared as type: {}".format(lst_type))
        if isinstance(lines[0], GroundLSTLine) and lst_type is not None and lst_type != LSTType.GROUND:
            raise ValueError("Ground lines were provided but declared as type: {}".format(lst_type))
        if isinstance(lines[0], SceneryLSTLine) and lst_type is not None and lst_type != LSTType.SCENERY:
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

        # Define other class parameters
        self.filepath1 = StringVar()
        self.filepath2 = StringVar()
        self.filepath3 = StringVar()
        self.filepath4 = StringVar()
        self.filepath5 = StringVar()
        self.filelabel1 = StringVar()
        self.filelabel2 = StringVar()
        self.filelabel3 = StringVar()
        self.filelabel4 = StringVar()
        self.filelabel5 = StringVar()
        self.SceneryName = StringVar()

        self.lst_mode = StringVar(value="Aircraft")  # other options are Scenery and Ground
        self.lst_mode_options = ['Aircraft', 'Ground', 'Scenery']
        self.folderpath = StringVar()
        self.filepaths = list()

        # Define filetypes for GUIs
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

        # Define required files
        required_files = dict()
        required_files['Aircraft'] = [True, True, True, False, False]
        required_files['Scenery'] = [True, True, False, None, None]
        required_files['Ground'] = [True, True, True, False, False]
        self.required_files = required_files

        # Define Labels
        labels = dict()
        labels['Aircraft'] = ['DAT', 'Visual Model', 'Collision', 'Cockpit', 'Coarse']
        labels['Ground'] = ['DAT', 'Visual Model', 'Collision', 'Cockpit', 'Coarse']
        labels['Scenery'] = ['Map', 'Start Position', 'Mission', '', '']
        self.labels = labels

        lst_filetypes = dict()
        lst_filetypes['Aircraft'] = ['dat', ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf']]
        lst_filetypes['Ground'] = ['dat', ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf'], ['dnm', 'srf']]
        lst_filetypes['Scenery'] = ['fld', 'stp', 'yfs', '', '']
        self.lst_filetypes = lst_filetypes

        # Setup the GUI
        self.gui_setup()

    def gui_setup(self):
        """Create the User Interface"""
        # Window Title
        self.parent.wm_title(__title__ + " v" + __version__)

        # Window Geometry Controls
        self.parent.wm_resizable(width=True, height=True)
        self.parent.minsize(self.parent.winfo_width() + 100, self.parent.winfo_height() + 150)

        # Window Order
        self.parent.wm_attributes('-topmost', 1)

        # Setup the Frames
        MainFrame = Frame()
        PackFrame = LabelFrame(MainFrame, text="Pack Details")
        EditFrame = Frame(MainFrame)
        PreviewFrame = Frame(EditFrame)
        SelectFrame = Frame(EditFrame)
        ButtonFrame = Frame(MainFrame)

        # Setup the Pack Frame
        pack_label = Label(PackFrame, text="Pack Folder: ")
        pack_label.grid(row=0, column=0, sticky="W")
        pack_filepath_display = Entry(PackFrame, textvariable=self.folderpath, width=40).grid(row=0, column=1,
                                                                                              sticky="WE")
        pack_button = Button(PackFrame, text="Select Pack Folder", command=self.select_pack_directory).grid(row=0,
                                                                                                            column=2)

        lst_type = Label(PackFrame, text="LST Type:").grid(row=1, column=0)
        lst_type_selection = OptionMenu(PackFrame, self.lst_mode, *self.lst_mode_options).grid(row=1, column=1,
                                                                                               columnspan=2)

        # Setup the File Selection Frame
        row_num = 0
        self.scenery_name_label = Label(EditFrame, text="Scenery Name")
        self.scenery_name_label.grid(row=row_num, column=0, sticky="W")
        self.scenery_name_entry = Entry(EditFrame, textvariable=self.SceneryName, width=30)
        self.scenery_name_entry.grid(row=row_num, column=1, sticky="WE")

        row_num += 1
        self.file1_label = Label(EditFrame, text=self.labels[self.lst_mode.get()][0])
        self.file1_label.grid(row=row_num, column=0, sticky="W")
        self.file1_entry = Entry(EditFrame, textvariable=self.filepath1, width=30)
        self.file1_entry.grid(row=row_num, column=1, sticky="WE")
        self.button1 = Button(EditFrame, text="Select File", command=lambda: self.select_file(0))
        self.button1.grid(row=row_num, column=2, stick="WE")

        row_num += 1
        self.file2_label = Label(EditFrame, text=self.labels[self.lst_mode.get()][1])
        self.file2_label.grid(row=row_num, column=0, sticky="W")
        self.file2_entry = Entry(EditFrame, textvariable=self.filepath2, width=30)
        self.file2_entry.grid(row=row_num, column=1, sticky="WE")
        self.button2 = Button(EditFrame, text="Select File", command=lambda: self.select_file(1))
        self.button2.grid(row=row_num, column=2, stick="WE")

        row_num += 1
        self.file3_label = Label(EditFrame, text=self.labels[self.lst_mode.get()][2])
        self.file3_label.grid(row=row_num, column=0, sticky="W")
        self.file3_entry = Entry(EditFrame, textvariable=self.filepath3, width=30)
        self.file3_entry.grid(row=row_num, column=1, sticky="WE")
        self.button3 = Button(EditFrame, text="Select File", command=lambda: self.select_file(2))
        self.button3.grid(row=row_num, column=2, stick="WE")

        row_num += 1
        self.file4_label = Label(EditFrame, text=self.labels[self.lst_mode.get()][3])
        self.file4_label.grid(row=row_num, column=0, sticky="W")
        self.file4_entry = Entry(EditFrame, textvariable=self.filepath4, width=30)
        self.file4_entry.grid(row=row_num, column=1, sticky="WE")
        self.button4 = Button(EditFrame, text="Select File", command=lambda: self.select_file(3))
        self.button4.grid(row=row_num, column=2, stick="WE")

        row_num += 1
        self.file5_label = Label(EditFrame, text=self.labels[self.lst_mode.get()][4])
        self.file5_label.grid(row=row_num, column=0, sticky="W")
        self.file5_entry = Entry(EditFrame, textvariable=self.filepath5, width=30)
        self.file5_entry.grid(row=row_num, column=1, sticky="WE")
        self.button5 = Button(EditFrame, text="Select File", command=lambda: self.select_file(4))
        self.button5.grid(row=row_num, column=2, stick="WE")

        # Pack up the frames
        MainFrame.pack()
        PackFrame.pack()
        EditFrame.pack()
        PreviewFrame.grid(row=0, column=0)
        SelectFrame.grid(row=0, column=1)
        ButtonFrame.pack()

    def update_lst_type(self):
        pass

        # Assign Appropriate labels for the filepath inputs, add * if required

        # Determine which fields can be disabled based on the lst filetype selection

        # Disable Buttons that should not be used

    def select_pack_directory(self):
        """Have the user select the pack directory, with the standard sub folders for aircraft, user, etc"""
        prompt = "Please select the folder where you have built your addon package."

    def select_File(self, file_position):
        """Select the file for the indicated position."""
        # Get the prompt
        prompt = self.prompts[self.lst_mode.get()][file_position]

        # Get the filetypes 
        gui_filetype = [("All Files", "*.*")]

        ftype = self.lst_filetypes[self.lst_mode.get()][file_position]

        if isinstance(ftype, list):
            for filetype in ftype:
                if filetype.lower() in self.filetypes.keys():
                    gui_filetype.insert(0, self.filetypes[filetype.lower()])
        elif isinstance(ftype, str):
            if ftype.lower() in self.filetypes.keys():
                gui_filetype.insert(0, self.filetypes[ftype.lower()])

        # Get the filepath using GUI
        path = filedialog.askdirectory(parent=parent, title=prompt, initialdir=starting_directory,
                                       filetypes=gui_filetype)

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


if __name__ == "__main__":
    main()


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