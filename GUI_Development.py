#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 22:35:04 2024

@author: Decaff42


This code provides a GUI program to assemble a pack that includes aircraft, ground objects and scenery addons based
on the user's selection of files. Will create LST files for the various addons defined.
"""


__title__ = "YSFlight Pack Builder"
__version__ = "0.1.0"
__author__ = "Decaff42 & MartinDutchie"
__copyright__ = "2024 by Decaff_42 & MartinDutchie"
__license__ = """Only non-commercial use is allowed without prior written permission."""


# Import standard Python Modules
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import os
import string
import shutil



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
        self.settings_directory = os.getcwd()

        # Define filepaths that the user selects for the lst contents - These are Absolute Paths. The
        # user will have the filenames displayed so that they can actually determine if they have the
        # correct file in selected after the fact.
        self.current_paths = {'Aircraft':[StringVar() for _ in range(0,5)], 'Ground':[StringVar() for _ in range(0,5)], 'Scenery':[StringVar() for _ in range(0,3)]}
        self.current_filenames = {'Aircraft':[StringVar() for _ in range(0,5)], 'Ground':[StringVar() for _ in range(0,5)], 'Scenery':[StringVar() for _ in range(0,3)]}

        # Define the output pack directory where the user will export an assembled pack to. Note: The tool will create
        # the pack folder so we just need a place to put it. This could default to where the tool is located as a
        # fixed default, or be placed as a setting for the user in the future.
        self.PackDirectory = StringVar(value = os.path.abspath(os.sep))

        # Store where a user last selected a file from as this is likely close to where their next file is and will
        # therefore help them save a lot of time in folder navigation by simply storing that information.
        self.WorkingDirectory = StringVar(value = os.path.abspath(os.sep))
        
        # Define names that the user will input at various points
        # The UserName and PackName be used to create folder/filenames in the pack file structure:
        # [PackName].zip\user\[UserName]\[PackName]\[air/gnd/sce]\[files]
        self.SceneryName = StringVar()  # Need a custom name for each map added to the LST
        self.UserName = StringVar()
        self.PackName = StringVar()
        self.SceneryAirRace = IntVar(value=0)  # Used to indicate if a map should have the AIR RACE flag added to it in the LST File.

        # Define the aircraft and ground object name based on the DAT file. This will be displayed at the top of the
        # Aircraft and Ground Object Edit frame so that the user can see what they are working on.
        self.default_aircraft_name = 'AIRCRAFT_NAME'  # Could be a setting
        self.default_ground_object_name = 'GROUND_OBJECT_NAME'  # Could be a setting
        self.AircraftName = StringVar(value=self.default_aircraft_name)
        self.GroundObjectName = StringVar(value=self.default_ground_object_name)

        # Define storage of the different LST file contents
        self.lst_entries = {'Aircraft': {}, 'Ground': {}, 'Scenery': {}}
        self.current_lst_edit_name = {'Aircraft': None, 'Ground': None, 'Scenery': None}

        # Define the the lst options
        self.lst_types = ['Aircraft', 'Ground', 'Scenery']  # validate mode inputs into functions
        self.lst_file_prefixes = ['air', 'gnd', 'sce']  # Validate which lst file we are importing or exporting.
        self.current_mode = 'Aircraft'  # A variable to hold the shortened name of the tab currently displayed
        
        # Define the filetype options for the file selection gui, based on the allowable filetype.
        filetypes = dict()
        filetypes['srf'] = [("SRF File", "*.srf")]
        filetypes['dat'] = [("DAT File", "*.dat")]
        filetypes['dnm'] = [("DynaModel File", "*.dnm")]
        filetypes['stp'] = [("Start Position File", "*.stp")]
        filetypes['fld'] = [("Scenery File", "*.fld")]
        filetypes['yfs'] = [("Mission File", "*.yfs")]
        filetypes['dnm srf'] = [("DynaModel or Surf File", "*.dnm *.srf")]
        self.filetypes = filetypes

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

        # Define prompts for the file selection dialogs. Matches order of the labels and GUI.
        prompts = dict()
        for name, key in zip(['Aircraft', 'Ground Object', 'Scenery'], list(self.labels.keys())):
            prompts[key] = list()
            for label_name in self.labels[key]:
                if label_name:
                    prompts[key].append("Select the {}'s {} File".format(name, label_name))
                else:  # Handle the empty parts of the Scenery label list or any future blank entries.
                    prompts[key].append('')
        self.prompts = prompts

        # Define the allowable file types for the different positions.
        # Make sure every element is a list so that they can all be parsed the same
        # way in the "select file" function.
        lst_filetypes = dict()
        lst_filetypes['Aircraft'] = [['dat'], ['dnm srf', 'dnm', 'srf'], ['dnm srf', 'dnm', 'srf'], ['dnm srf', 'dnm', 'srf'], ['dnm srf', 'dnm', 'srf']]
        lst_filetypes['Ground'] = [['dat'], ['dnm srf', 'dnm', 'srf'], ['dnm srf', 'dnm', 'srf'], ['dnm srf', 'dnm', 'srf'], ['dnm srf', 'dnm', 'srf']]
        lst_filetypes['Scenery'] = [['fld'], ['stp'], ['yfs'], [], []]
        self.lst_filetypes = lst_filetypes

        # Define settings class variables
        self.settings = dict()
        self.setting_types = dict()
        self.build_default_settings()

        # Define variables that should move to a settings file.
        self.ask_before_delete_lst = IntVar(value=1)

        # Define Configuration File Delimiters:
        self.pack_save_config_delimiter = ":="
        self.testing_config_filepath = os.path.join(os.getcwd(), 'testing_pack_config_file.cfg')
        self.use_testing_config_filepath = True

        # Put all frames inside a main Frame widget.
        self.MainFrame = Frame()

        # Setup the GUI
        self.air_listbox = None
        self.gnd_listbox = None
        self.sce_listbox = None
        self.read_settings()  # Will create default settings dict if settings file not found.
        # self.load_pack_configuration()
        self.gui_setup()

    def clear_loaded_data(self, aircraft=True, ground=True, scenery=True):
        """Provide a way to clear all data in some or all of the tabs"""
        if aircraft is True:
            self.lst_entries['Aircraft'] = {}
            self.air_listbox.delete(0, END)
            self.current_lst_edit_name['Aircraft'] = None
        if ground is True:
            self.lst_entries['Ground'] = {}
            self.gnd_listbox.delete(0, END)
            self.current_lst_edit_name['Ground'] = None
        if scenery is True:
            self.lst_entries['Scenery'] = {}
            self.sce_listbox.delete(0, END)
            self.current_lst_edit_name['Scenery'] = None

    def clear_entry_fields(self, aircraft=True, ground=True, scenery=True, ask=False):
        """Provide a way to clear all fields in some or all of the tabs"""

        if ask is True:
            paths = self.current_paths[self.current_mode]
            if any([True for path in paths if len(path.get()) > 0]):
                # Ask the user if they really want to delete all the paths.
                prompt = "Are you sure you want to delete all of the {} filepaths you have entered?".format(self.current_mode)
                title = "Delete all {} Filepaths?".format(self.current_mode)

                answer = messagebox.askquestion(parent=self, title=title, message=prompt)
                if answer is False or answer is None:
                    return

        if aircraft is True:
            self.AircraftName.set(value=self.default_aircraft_name)
            for idx in range(len(self.current_paths['Aircraft'])):
                self.current_paths['Aircraft'][idx].set("")
                self.current_filenames['Aircraft'][idx].set("")
            self.current_lst_edit_name['Aircraft'] = None
        if ground is True:
            self.GroundObjectName.set(self.default_ground_object_name)
            for idx in range(len(self.current_paths['Ground'])):
                self.current_paths['Ground'][idx].set("")
                self.current_filenames['Ground'][idx].set("")
            self.current_lst_edit_name['Ground'] = None
        if scenery is True:
            self.SceneryName.set(value="")
            self.SceneryAirRace.set(0)
            for idx in range(len(self.current_paths['Scenery'])):
                self.current_paths['Scenery'][idx].set("")
                self.current_filenames['Scenery'][idx].set("")
            self.current_lst_edit_name['Scenery'] = None

    def open_settings_dialog(self):
        """Let the user open a settings GUI to make selections"""
        # Store the current settings so that we have something to compare to
        old_settings = self.settings

        # Let the user make changes to the settings
        self.wait_window(Settings(self))
        self.focus_set()

        # store the settings
        self.write_settings()

        # Test to see if any settings have changed.
        update = False
        for key in old_settings.keys():
            if old_settings[key] != self.settings[key]:
                update = True

        # Reload the GUI to update any changes.
        if update is True:
            for widget in self.MainFrame.winfo_children():
                widget.destroy()
            self.gui_setup()

            messagebox.showinfo(parent=self.parent,
                                title="Settings Updated",
                                message="You may need to restart to the program for all settings to be displayed.")

        # Assign class variables based on updated settings.
        self.WorkingDirectory.set(self.settings['working_directory'])
        self.UserName.set(self.settings['user_name'])

    def build_default_settings(self):
        """Have a function to define all of the default settings"""
        self.setting_types = {'preview_num_rows':  int,
                              'preview_char_width': int,
                              'working_directory': os.PathLike,
                              'user_name': str,
                              'ask_before_entry_removal': int}

        self.settings = {'preview_num_rows':15,
                         'preview_char_width':30,
                         'working_directory':os.path.normpath(os.sep),
                         'user_name':'UserName',
                         'ask_before_entry_removal':  1}

    def write_settings(self):
        """assemble the lines for a settings file and write to the settings location."""
        output = [self.title+"\n", "v"+self.version+"\n"]
        for key, value in self.settings.items():
            output.append("{}{}{}\n".format(key,self.pack_save_config_delimiter, value))

        with open(os.path.join(self.settings_directory, "settings.cfg"), mode='w') as settings_file:
            settings_file.writelines(output)

    def read_settings(self):
        """Read an existing settings file"""
        if os.path.isfile(os.path.join(self.settings_directory, "settings.cfg")) is False:
            self.build_default_settings()
            return

        with open(os.path.join(self.settings_directory, "settings.cfg"), mode='r') as settings_file:
            lines = settings_file.readlines()

        # Skip the header and the version number
        self.settings = dict()
        lines = lines[2:]
        for line in lines:
            key, value = line[:-1].split(self.pack_save_config_delimiter)
            if value:
                if key in self.setting_types.keys():
                    output_type = self.setting_types[key]
                    if output_type is bool:
                        self.settings[key] = bool(value)
                    elif output_type is int:
                        self.settings[key] = int(value)
                    elif output_type is os.PathLike:
                        self.settings[key] = os.path.normpath(value)
                    elif output_type is str:
                        self.settings[key] = value

    def gui_setup(self):
        """Create the User Interface for the LST Builder."""
        # Window Title
        self.parent.wm_title(self.title + " v" + self.version)
        
        # Window Geometry Controls
        self.parent.wm_resizable(width=True, height=True)
        self.parent.minsize(self.parent.winfo_width() + 150, self.parent.winfo_height() + 150)
        
        # Window Order
        self.parent.wm_attributes('-topmost', 1)

        #
        # Set up the file menus
        #
        MenuBar = Menu(self.parent)

        # Setup the file menu
        FileMenu = Menu(MenuBar, tearoff=0)
        FileMenu.add_command(label="New Project", command=self.new_pack_configuration)
        FileMenu.add_command(label="Open Project", command=self.load_pack_configuration)
        FileMenu.add_command(label="Save Project", command=self.save_pack_configuration)
        FileMenu.add_separator()
        FileMenu.add_command(label="Quit {}".format(self.title), command=self.quit_program)
        MenuBar.add_cascade(label="File", menu=FileMenu)

        # Set up the Edit Menu
        EditMenu = Menu(MenuBar, tearoff=0)
        EditMenu.add_command(label="Export Pack", command=self.assemble_pack)
        EditMenu.add_command(label="Validate Pack", command=self.validate_pack_structure)
        EditMenu.add_separator()
        EditMenu.add_command(label="Edit LST Entry", command=self.edit_lst_entry)
        EditMenu.add_command(label="Copy LST Entry", command=self.copy_lst_entry)
        EditMenu.add_separator()
        EditMenu.add_command(label="Move Selected LST Entry Up", command=lambda: self.move_selected_lst_entry('up'))
        EditMenu.add_command(label="Move Selected LST Entry Down", command=lambda: self.move_selected_lst_entry('down'))
        MenuBar.add_cascade(label="Edit", menu=EditMenu)

        # Set up the Settings Menu
        SettingsMenu = Menu(MenuBar, tearoff=0)
        SettingsMenu.add_command(label="Settings", command=self.open_settings_dialog)
        # SettingsMenu.add_command(label="Set Default Working Directory", command=self.ask_default_working_directory)
        # SettingsMenu.add_command(label="Set Default Username", command=self.ask_username)
        MenuBar.add_cascade(label="Settings", menu=SettingsMenu)

        # Set up the Help Menu
        HelpMenu = Menu(MenuBar, tearoff=0)
        HelpMenu.add_command(label="Help", command=self.get_user_help)
        HelpMenu.add_command(label="About", command=self.show_about)
        MenuBar.add_cascade(label="Help", menu=HelpMenu)

        # Add the Menu to the GUI
        self.parent.config(menu=MenuBar)

        # Start a notebook to hold aircraft, ground object and scenery inputs
        LstNotebook = ttk.Notebook(self.MainFrame)

        #
        # Build the aircraft Tab
        #
        # This is where the user will select the dat, visual, collision, cockpit, and coarse models for
        # an aircraft lst line item.
        AircraftFrame = Frame(LstNotebook)

        # Aircraft Preview Section
        AircraftPreviewFrame = Frame(AircraftFrame)

        # Start with a listbox to show the different aircraft that have been loaded in the program. This will display
        # the identify line of the aircraft's DAT file or in a future update: a user-selected IDENTIFY line to overwrite
        # the identify line of an existing DAT FILE that will be copied and used for the LST entry.
        AircraftListFrame = Frame(AircraftPreviewFrame)
        AircraftMoveLSTButtonFrame = Frame(AircraftListFrame, width=10)
        pixel = PhotoImage(width=1, height=1)
        Button(AircraftMoveLSTButtonFrame,
               image=pixel,
               width=1,
               text=u'\u2191',
               command=lambda: self.move_selected_lst_entry('up')
               ).grid(row=0,column=0)
        Button(AircraftMoveLSTButtonFrame,
               image=pixel,
               width=1,
               text=u'\u2193',
               command=lambda: self.move_selected_lst_entry('down')
               ).grid(row=1, column=0)
        AircraftMoveLSTButtonFrame.grid(row=0, column=0)

        self.air_listbox = Listbox(AircraftListFrame,
                                   width=self.settings['preview_char_width'],
                                   height=self.settings['preview_num_rows'],
                                   font=("Helvetica",12),
                                   selectmode='SINGLE')
        self.air_listbox.grid(row=0, column=1, sticky="NSWE")
        air_y_axis_scroll_bar = ttk.Scrollbar(AircraftListFrame, orient='vertical')
        air_y_axis_scroll_bar.configure(command=self.air_listbox.yview)
        air_y_axis_scroll_bar.grid(row=0, column=2, sticky="NSWE")

        # To account for long IDENTIFY names beyond the 30 character width of the listbox we will have a x scrollbar.
        air_x_axis_scroll_bar = ttk.Scrollbar(AircraftListFrame, orient='horizontal')
        air_x_axis_scroll_bar.configure(command=self.air_listbox.xview)
        air_x_axis_scroll_bar.grid(row=1, column=1, sticky="NSWE")
        
        AircraftListFrame.pack(side="top", padx=5, pady=5)

        # At the bottom of the listbox we want buttons to control some user functionality to either edit or delete
        # an LST entry.
        AircraftPreviewButtonFrame = Frame(AircraftPreviewFrame)
        Button(AircraftPreviewButtonFrame,
               text="Edit",
               command=self.edit_lst_entry
               ).grid(row=0, column=0, sticky="NSWE")
        Button(AircraftPreviewButtonFrame,
               text="Delete",
               command=self.delete_lst_entry
               ).grid(row=0, column=1, sticky="NSWE")
        AircraftPreviewButtonFrame.pack(side='bottom')
        AircraftPreviewFrame.pack(side="left")
        
        # Aircraft Edit Section         
        AircraftEditFrame = Frame(AircraftFrame)
        AircraftEntryFrame = Frame(AircraftEditFrame)
        row_num = 0
        Label(AircraftEntryFrame, textvariable=self.AircraftName).grid(row=row_num, column=0, columnspan=3)

        # Build the Aircraft GUI Entry widgets iteratively
        for file_position in range(0,5):
            row_num += 1
            txt = self.labels['Aircraft'][file_position] + ":"
            if self.required_files['Aircraft'][file_position] is True:
                txt += " *"

            Label(AircraftEntryFrame, text=txt).grid(row=row_num, column=0, sticky="W")
            Entry(AircraftEntryFrame,
                  textvariable=self.current_filenames['Aircraft'][file_position],
                  width=30).grid(row=row_num, column=1, sticky="NSWE")

            # Need the lambda x=file_position in order to have the current value of file_position at time of the Button
            # creation to stay stored in this button.
            Button(AircraftEntryFrame,
                   text="Select",
                   command=lambda x=file_position: self.select_file(x)).grid(row=row_num, column=2, sticky="NSWE")
        AircraftEntryFrame.pack()

        AircraftEditButtonFrame = Frame(AircraftEditFrame)
        Button(AircraftEditButtonFrame, text="Store", command=self.save_lst_entry).grid(row=0,column=0, sticky="NSWE")
        Button(AircraftEditButtonFrame,
               text="Clear All Inputs",
               command=lambda: self.clear_entry_fields(aircraft=True, ground=False, scenery=False, ask=True)
               ).grid(row=0,column=1, sticky="NSWE")
        AircraftEditButtonFrame.pack()
        
        AircraftEditFrame.pack(side='right', padx=15)
        AircraftFrame.pack()

        #
        # Build the Ground Object Tab
        #
        # TODO: This section to be completed once the Aircraft and Scenery LST sections are ironed out as the Ground LST
        # will function largely the same as the Aircraft.
        # This is where the user will select the dat, visual, collision, cockpit, and coarse models for
        # a ground object lst line item.
        GroundFrame = Frame(LstNotebook)
        
        # Ground Object Preview Section
        GroundPreviewFrame = Frame(GroundFrame)
        GroundPreviewButtonFrame = Frame(GroundPreviewFrame)
        self.gnd_listbox = Listbox(GroundPreviewFrame,
                                   width=self.settings['preview_char_width'],
                                   height=self.settings['preview_num_rows'],
                                   font=("Helvetica",12), selectmode='SINGLE')

        # Ground Object Edit Section
        GroundEditFrame = Frame(GroundFrame)
        GroundEntryFrame = Frame(GroundEditFrame)
        row_num = 0
        GroundEditButtonFrame = Frame(GroundEditFrame)

        #
        # Build the Scenery Tab
        #
        # This is where the user will input a scenery name and select an fld, stp, and optional yfs file.
        SceneryFrame = Frame(LstNotebook)

        # Scenery Preview Selection
        SceneryPreviewFrame = Frame(SceneryFrame)
        SceneryPreviewButtonFrame = Frame(SceneryPreviewFrame)
        self.sce_listbox = Listbox(SceneryPreviewFrame,
                                   width=self.settings['preview_char_width'],
                                   height=self.settings['preview_num_rows'],
                                   font=("Helvetica", 12), selectmode='SINGLE')

        # Scenery Edit Selection
        SceneryEditFrame = Frame(SceneryFrame)
        SceneryEntryFrame = Frame(SceneryEditFrame)

        row_num = 0
        Label(SceneryEntryFrame, text="Scenery Name: *").grid(row=row_num, column=0, sticky='W')
        Entry(SceneryEntryFrame, textvariable=self.SceneryName).grid(row=row_num, column=1, columnspan=2, sticky='WE')

        # Build the scenery GUI Elements iteratively.
        for file_position in range(0,3):
            row_num += 1
            txt = self.labels['Scenery'][file_position] + ":"
            if self.required_files['Scenery'][file_position] is True:
                txt += " *"
            Label(SceneryEntryFrame, text=txt).grid(row=row_num, column=0, sticky="W")
            Entry(SceneryEntryFrame,
                  textvariable=self.current_filenames['Scenery'][file_position],
                  width=30).grid(row=row_num, column=1, sticky="WE")

            # Need the lambda x=file_position in order to have the current value of file_position at time of the Button
            # creation to stay stored in this button.
            Button(SceneryEntryFrame,
                   text="Select",
                   command=lambda x=file_position: self.select_file(x)).grid(row=row_num, column=2, sticky="NSWE")

        row_num += 1
        Checkbutton(SceneryEntryFrame,
                    text="YSFlight 2018+ Air Race Map?",
                    variable=self.SceneryAirRace, onvalue=1, offvalue=0).grid(row=row_num, column=1, sticky='w')
        SceneryEntryFrame.pack()

        SceneryEditButtonFrame = Frame(SceneryEditFrame)
        Button(SceneryEditButtonFrame, text="Store", command=self.save_lst_entry).grid(row=0,column=0, sticky="NSWE")
        Button(SceneryEditButtonFrame,
               text="Clear All Inputs",
               command=self.clear_entry_fields(scenery=True, ask=True)).grid(row=0,column=1, sticky="NSWE")
        SceneryEditButtonFrame.pack()
        
        SceneryEditFrame.pack(side='right')
        SceneryFrame.pack()

        # Add the Aircraft, Ground Object, and Scenery Frames to the NoteBook Widget
        LstNotebook.add(AircraftFrame, text='Aircraft')
        LstNotebook.add(GroundFrame, text='Ground Objects')
        LstNotebook.add(SceneryFrame, text='Scenery')

        # Pack up the frames
        self.MainFrame.pack()
        # PackFrame.pack(expand=True, fill='y')
        LstNotebook.pack(expand=True, fill='both')
        LstNotebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def functionality_not_available_popup(self, function_name):
        messagebox.showinfo(parent=self,
                            title="Functionality Not Yet Implemented",
                            message="{} has not yet been implemented.".format(function_name))
    
    def get_user_help(self):
        """Provide a URL or some other way to provide a tutorial to the user.

        This function will be used in the future and for now is undeveloped
        """
        self.functionality_not_available_popup("get_user_help")

    def show_about(self):
        """Display basic information about the program for the user"""
        key_total_width = 15
        msg = self.title + "\n\n"
        msg += "{}{}\n".format("Version:".ljust(key_total_width), self.version)
        msg += "{}{}\n\n".format("Authors:".ljust(key_total_width), self.author)
        msg += "Copyright {}".format(self.copyright_notice)
        messagebox.showinfo(title="About", message=msg)

    def ask_default_working_directory(self):
        """Have the user select a folder where they keep their modding WIP files

        This function will be used in the future and for now is undeveloped
        """
        self.functionality_not_available_popup("ask_default_working_directory")

    def move_selected_lst_entry(self, mode):
        """Will take a selected LST entry and move it up or down the listbox."""

        # Depending on the current mode, we will need data from different sources
        selected_idx = list()   # initialize to catch current_mode issues.
        listbox_order = list()  # initialize to catch current_mode issues.
        if self.current_mode == 'Aircraft':
            listbox_order = self.air_listbox.get(0,END)
            selected_idx = list(self.air_listbox.curselection())
        elif self.current_mode == 'Ground':
            listbox_order = self.gnd_listbox.get(0, END)
            selected_idx = list(self.gnd_listbox.curselection())
        elif self.current_mode == 'Scenery':
            listbox_order = self.sce_listbox.get(0, END)
            selected_idx = list(self.sce_listbox.curselection())

        # Exit early if:
        # (1) There was nothing selected
        # (2) There was nothing to select in the first place (empty listbox)
        # (3) The current_mode was not an expected value.
        if len(selected_idx) == 0 or len(listbox_order) == 0:
            return

        # Make a new order based on the index(es) of the selected items. All of the elements selected should be
        # Grouped together, starting at the highest index.
        new_selected_idx = list()
        if mode.lower() == 'up':
            starting_idx = max(0, min(selected_idx) - 1)
            for idx, old_idx in enumerate(selected_idx):
                element = listbox_order.pop(old_idx)
                listbox_order.insert(starting_idx + idx, element)
                new_selected_idx.append(starting_idx + idx)
        else:
            starting_idx = max(len(listbox_order), max(selected_idx) + 1)
            extracted = [listbox_order[idx] for idx in selected_idx]
            new_order = list()
            for idx, element in enumerate(listbox_order):
                if element not in extracted and idx < starting_idx:
                    new_order.append(element)
                else:
                    break
            new_order.extend(extracted)
            new_selected_idx = [new_order.index(i) for i in extracted]
            for element in listbox_order:
                if element not in new_order:
                    new_order.append(element)

            listbox_order = new_order

        # Clear the old listbox entries and insert the new ones and set the selection
        if self.current_mode == 'Aircraft':
            self.air_listbox.delete(0,END)
            self.air_listbox.insert(END, *listbox_order)
            self.air_listbox.selection_clear(0, END)
            for idx in new_selected_idx:  # Cannot select elements in listbox at once, need to do singly.
                self.air_listbox.selection_set(idx)
        elif self.current_mode == 'Ground':
            self.gnd_listbox.delete(0,END)
            self.gnd_listbox.insert(END, *listbox_order)
            self.gnd_listbox.selection_clear(0, END)
            for idx in new_selected_idx:  # Cannot select elements in listbox at once, need to do singly.
                self.gnd_listbox.selection_set(idx)
        elif self.current_mode == 'Scenery':
            self.sce_listbox.delete(0,END)
            self.sce_listbox.insert(END, *listbox_order)
            self.sce_listbox.selection_clear(0, END)
            for idx in new_selected_idx:  # Cannot select elements in listbox at once, need to do singly.
                self.sce_listbox.selection_set(idx)

    def copy_lst_entry(self):
        """Will take a selected LST entry and load the contents into the GUI for the purpose of creating a new LST Entry
        based on the selected one.

        This function will be used in the future and for now is undeveloped
        """
        self.functionality_not_available_popup("copy_lst_entry")

    def edit_lst_entry(self):
        """Will take a selected LST entry and load the contents into the GUI for editing purposes

        This function will be used in the future and for now is undeveloped
        """
        self.functionality_not_available_popup("edit_lst_entry")

    def delete_lst_entry(self):
        """Will take a selected LST entry and delete it.

        This function will be used in the future and for now is undeveloped
        """
        self.functionality_not_available_popup("edit_lst_entry")

        # Ensure that there is an option selected in the current Tab's Listbox

        # If the user wants a warning before deleting an LST entry, ask them self.settings['ask_before_entry_removal']

        # Delete LST entry from appropriate list of LST Entries

        # Re-set the listbox entries.

    def validate_pack_structure(self):
        """Validate that filepaths still exist and that IDENTIFY and SCENERY NAMEs are unique

        This function will be used in the future and for now is undeveloped
        """
        self.functionality_not_available_popup("new_pack_configuration")

    def new_pack_configuration(self):
        """This function is used to unload any and all saved and unsaved work to prepare for a new project

        This function will be used in the future and for now is undeveloped
        """
        self.functionality_not_available_popup("new_pack_configuration")

    def save_pack_configuration(self):
        """This function is used to save un-completed pack progress into a file that can be loaded by this program to
        initialize class instances.

        This function will be used in the future and for now is undeveloped
        """

        if self.use_testing_config_filepath is True:
            output_file = open(self.testing_config_filepath, mode='w')
        else:
            # Ask the user to select a filename & location, default to the Working Directory (where their mod files are)
            output_file = filedialog.asksaveasfile(parent=self.parent,
                                                   initialdir=self.WorkingDirectory.get(),
                                                   defaultextension=".cfg",
                                                   filetypes=(("Config File", "*.cfg"), ("All Files", "*.*")))
        if not output_file:
            messagebox.showinfo(parent=self.parent, title="Not Saved", message="Your pack configuration was not saved.")
            return

        if os.access(os.path.abspath(output_file.name), os.W_OK) is False:
            title = "Unable to Save"
            msg = "Unable to save to the selected file. Check to see if it is open and close it."
            messagebox.showerror(parent=self.parent,
                                 title=title,
                                 message=msg)
            return

        # Initialize the output with some information about the tool so that we can hold onto that for cases of backwards
        # compatibility
        output = ['PACK_BUILDER_TOOL_VERSION: {}'.format(self.version),
                  "DELIMITER:{}".format(self.pack_save_config_delimiter),  # Record so that future tools can learn it.
                  "AIRCRAFT_BLOCK"]

        # Assemble LST info from the classes. We need to preserve order, so use the order defined in the Previews.
        # This can only be done because we will have previously ensured that the IDENTIFY or MAP Names are unique prior
        # to storing them and displaying them in the preview list boxes.
        # We will wrap each section with a string so we can split the list up later on import more easily
        for air_identify in self.air_listbox.get(0, END):
            save_data = self.lst_entries['Aircraft'][air_identify].write_save_config_data()
            output.append("AIRCRAFT")
            for key, value in save_data.items():
                output.append("{}{}{}".format(key, self.pack_save_config_delimiter, value))
            output.append("END_AIRCRAFT")
        output.append("AIRCRAFT_BLOCK")

        output.append("GROUND_BLOCK")
        for gnd_identify in self.gnd_listbox.get(0, END):
            save_data = self.lst_entries['Ground'][gnd_identify].write_save_config_data()
            output.append("GROUND")
            for key, value in save_data.items():
                output.append("{}{}{}".format(key, self.pack_save_config_delimiter, value))
            output.append("END_GROUND")
        output.append("GROUND_BLOCK")

        output.append("SCENERY_BLOCK")
        for map_name in self.sce_listbox.get(0, END):
            save_data = self.lst_entries['Scenery'][map_name].write_save_config_data()
            output.append("SCENERY")
            for key, value in save_data.items():
                output.append("{}{}{}".format(key, self.pack_save_config_delimiter,  value))
            output.append("END_SCENERY")
        output.append("SCENERY_BLOCK")

        # Write the data to file
        for line in output:
            output_file.write(line +"\n")

        # May need to close the file for memory savings.
        try:
            output_file.close()
        except:
            pass

        # self.functionality_not_available_popup("save_pack_configuration")

    def load_pack_configuration(self):
        """This function is used to load an un-completed pack progress into the program from a file written by
        function save_pack_configuration and initializes class instances

        This function will be used in the future and for now is undeveloped
        """
        # Get the input filepath
        if self.use_testing_config_filepath is True:
            input_filepath = self.testing_config_filepath
        else:
            # Ask the user to select a pack configuration file
            input_filepath = filedialog.askopenfile(parent=self.parent, initialdir=self.WorkingDirectory.get())
            if not input_filepath:
                messagebox.showinfo(parent=self.parent,
                                    title="No File Selected",
                                    message="No pack configuration selected.")
                return

        # Import the raw data
        with open(input_filepath, mode='r') as config_file:
            input_data = config_file.readlines()
            for idx, line in enumerate(input_data):
                if line.endswith("\n"):
                    input_data[idx] = line[:-1]

        # Determine what the delimiter is. This should be in the second row. If it isn't then we should just default
        # to the default delimiter in the tool.
        if input_data[1].startswith("DELIMITER:"):
            delimiter = input_data[1][10:]
        else:
            delimiter = self.pack_save_config_delimiter

        # Clear all previously loaded data and clear the listbox preview windows.
        self.clear_loaded_data(aircraft=True, ground=True, scenery=True)

        # Load Aircraft
        if 'END_AIRCRAFT' in input_data:
            # We found at least one aircraft to process.
            aircraft_blocks = split_list(input_data, ['AIRCRAFT', 'END_AIRCRAFT'])[1:-1]
            for block in aircraft_blocks:
                temp_dict = dict()
                for line in block:
                    key, value = line.split(delimiter)
                    temp_dict[key] = value
                class_instance = AirGndLSTEntry()
                class_instance.assign_values(temp_dict)
                self.lst_entries['Aircraft'][class_instance.IDENTIFY] = class_instance
                self.air_listbox.insert(END, class_instance.IDENTIFY)  # Insert into the preview listbox
                print("Loaded Aircraft: " + class_instance.IDENTIFY)

        # Load Ground Objects
        if 'END_GROUND' in input_data:
            # We found at least one ground object to process.
            ground_blocks = split_list(input_data, ['GROUND', 'END_GROUND'])[1:-1]
            for block in ground_blocks:
                temp_dict = dict()
                for line in block:
                    key, value = line.split(delimiter)
                    temp_dict[key] = value
                class_instance = AirGndLSTEntry()
                class_instance.assign_values(temp_dict)
                self.lst_entries['Ground'][class_instance.IDENTIFY] = class_instance
                self.gnd_listbox.insert(END, class_instance.IDENTIFY)  # Insert into the preview listbox
                print("Loaded Ground Object: " + class_instance.IDENTIFY)

        # Load Sceneries
        if 'END_SCENERY' in input_data:
            # We found at least one scenery to process.
            scenery_blocks = split_list(input_data, ['SCENERY', 'END_SCENERY'])[1:-1]
            for block in scenery_blocks:
                temp_dict = dict()
                for line in block:
                    key, value = line.split(delimiter)
                    temp_dict[key] = value
                class_instance = SceLSTEntry()
                class_instance.assign_values(temp_dict)
                self.lst_entries['Scenery'][class_instance.map_name] = class_instance
                self.sce_listbox.insert(END, class_instance.map_name)  # Insert into the preview listbox
                print("Loaded Scenery: " + class_instance.map_name)

        # Clear all entry fields.
        self.clear_entry_fields(aircraft=True, ground=True, scenery=True)

        # self.functionality_not_available_popup("load_pack_configuration")

    def save_lst_entry(self):
        """Save the LST Entry from the active tab and insert it's LST Entry class instance into the appropriate list"""

        # Identify any missing required files. Use the labels in the GUI.
        required_files_missing = list()
        for idx, (path, required) in enumerate(zip(self.current_paths[self.current_mode], self.required_files[self.current_mode])):
            # This method will verify that we don't have a "", or a non-set StringVar
            if os.path.isfile(path.get()) is False and required is True:
                required_files_missing.append("\n- {}".format(self.labels[self.current_mode][idx]))

        # Alert the user that a file is missing.
        if len(required_files_missing) > 0:
            # Determine which files are missing based on the index
            title = "Missing Required Files for {} LST Entries".format(self.current_mode)
            msg = "The following files were either not defined or are no longer in their identified position:\n"
            for line in required_files_missing:
                msg += line

            # Inform the user of the issue and then do not proceed with the execution of this function.
            messagebox.showerror(parent=self, title=title, message=msg)
            return

        # Check to see if the IDENTIFY or SceneryName that we are adding is a duplicate
        if ((self.current_mode == 'Scenery' and self.SceneryName.get() in list(self.lst_entries[self.current_mode].keys())) or
            (self.current_mode == 'Aircraft' and self.AircraftName.get() in list(self.lst_entries[self.current_mode].keys())) or
            (self.current_mode == 'Ground' and self.GroundObjectName.get() in list(self.lst_entries[self.current_mode].keys()))):
            temp = ['Aircraft', 'Ground Object', 'Scenery']
            temp2 = ['IDENTIFY', 'IDENTIFY', 'Scenery Name']
            title = "Duplicate {} {} Detected".format(temp[self.lst_types.index(self.current_mode)], temp2[self.lst_types.index(self.current_mode)])
            msg = "All {}s must be unique in a pack".format(temp2[self.lst_types.index(self.current_mode)])
            messagebox.showerror(parent=self, title=title, message=msg)

            # TODO: Give user option to define new IDENTIFY Name and continue after checking it.
            return

        # Initialize an LST class instance for the type of LST we are working on and then add the appropriate values
        if self.current_mode == 'Scenery':
            lst_entry = SceLSTEntry()
        else:
            lst_entry = AirGndLSTEntry()

        # Assemble the necessary information into a dictionary and set values in the class instance. Use a loop to
        # automatically handle the routine information.
        transfer = dict()
        for label, value in zip(self.labels[self.current_mode], self.current_paths[self.current_mode]):
            if label:
                transfer[label.replace(" ","_")] = value.get()  # The replace is here as well as in the classes for redundancy

        # Handle the unique information that isn't common between the different types of LST Entries.
        if self.current_mode == "Scenery":
            transfer['map_name'] = self.SceneryName.get()
            transfer['air_race'] = bool(self.SceneryAirRace.get())
        elif self.current_mode == "Aircraft":
            transfer['IDENTIFY'] = self.AircraftName.get()
        elif self.current_mode == "Ground":
            transfer['IDENTIFY'] = self.GroundObjectName.get()

        # Assign values extracted from the GUI into the LST Entry class instance.
        lst_entry.assign_values(transfer)

        # Determine if we are replacing an existing lst entry in the storage lists
        if self.current_lst_edit_name[self.current_mode] in self.lst_entries[self.current_mode].keys():
            # Currently editing an lst entry
            self.lst_entries[self.current_mode][self.current_lst_edit_name[self.current_mode]] = lst_entry

            # Reset the editing notation as the user has saved the information.
            self.current_lst_edit_name[self.current_mode] = None
        else:
            if self.current_mode == 'Aircraft':
                self.lst_entries[self.current_mode][lst_entry.IDENTIFY] = lst_entry
                self.air_listbox.insert(END, lst_entry.IDENTIFY)
                self.clear_entry_fields(aircraft=True, ground=False, scenery=False)
            elif self.current_mode == 'Ground':
                self.lst_entries[self.current_mode][lst_entry.IDENTIFY] = lst_entry
                self.gnd_listbox.insert(END, lst_entry.IDENTIFY)
                self.clear_entry_fields(aircraft=False, ground=True, scenery=False)
            elif self.current_mode == 'Scenery':
                self.lst_entries[self.current_mode][lst_entry.IDENTIFY] = lst_entry
                self.sce_listbox.insert(END, lst_entry.map_name)
                self.clear_entry_fields(aircraft=False, ground=False, scenery=True)

        # self.functionality_not_available_popup("save_lst_entry")

    def update_air_gnd_label(self, dat_file_path):
        """This function will be called to update the aircraft or ground object title
        label at the top of the Aircraft and Ground Object Edit Frames.

        Assumptions:
        - The dat_file_path has already been validated as a dat file

        inputs
        dat_file_path (str): os.path-like to where the dat file for the aircraft or ground object is located.

        outputs
        None - This function executes and will set the appropriate variables in the class
        """
        # Get the identify line form the dat file
        name = extract_identify_from_dat(dat_file_path)

        # Set the variable names
        if self.current_mode == 'Aircraft':
            self.AircraftName.set(name)
        elif self.current_mode == 'Ground':
            self.GroundObjectName.set(name)
                
    def validate_pack_username(self, _, mode):
        """Validate the pack name and username to ensure they are compatible with windows/mac/linux systems

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
                info = "The following invalid characters were removed from the {}:\n{}".format(mode, "".join(bad_chars))
                messagebox.showinfo(parent=self, title=title, message=info)

    def edit_aircraft_lst_entry(self):
        """Allow the user to edit the selected aircraft entry in the aircraft listbox."""

        self.functionality_not_available_popup("edit_aircraft_lst_entry")

        # Check to make sure that the user has selected something in the aircraft listbox.

        # If the user has entries in the aircraft filepaths in the GUI, then we need to verify that the
        # user wants to clear the inputs and load the selected aircraft LST entry.

        # Clear the aircraft entries - Use the same function as the clear input function

        # Assign the different filepaths for the aircraft to the GUi variables.

    def select_pack_directory(self):
        """Have the user select where they want their addon package to be assembled.
        
        Inputs
        - None - The function is only called from one location

        Outputs
        - None - This function will set the appropriate class variable.
        """
        prompt = "Select the Directory where you want to assemble your addon package."
        path = filedialog.askdirectory(parent=self, title=prompt, mustexist=True, initialdir=os.getcwd())

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
        path = filedialog.askdirectory(parent=self, title=prompt, mustexist=True, initialdir=self.WorkingDirectory.get())

        # Validate the path
        if path:
            # Set the appropriate variable
            self.WorkingDirectory.set(path)

    def select_file(self, file_position):
        """Select the file for the indicated position.

        Inputs
        file_position (int): an integer of range 0 to 4 that indicates what position in the LST File the file being
                             selected is for and also corresponds to the vertical order of the GUI elements for selecting
                             these files.
        Outputs
        None - This function will set the appropriate variables in the class.
        """
        print(file_position, self.current_mode)  # Testing

        # Validate inputs. These should never trigger unless we have not 
        # properly set up the command calls for the select file buttons.
        if isinstance(file_position, int) is True:
            if file_position < 0 or file_position > 4:
                raise ValueError("{} Found that input [file_position] was not 0-4".format(__name__))
        else:
            raise TypeError("{} Expects input [file_position] to be an integer".format(__name__))

        if isinstance(self.current_mode, str) is True:
            if self.current_mode in self.lst_types is False:
                raise ValueError("{} Found that input [mode] was not 'Aircraft', 'Ground', or 'Scenery'".format(__name__))
        else:
            raise TypeError("{} Expects input [mode] to be a string".format(__name__))

        if self.current_mode == 'Scenery' and file_position > 2:
            # Scenery lst lines only have 3 filepaths.
            raise ValueError("{} Was expecting input [file_position] to be 0-2 for [mode]='Scenery'".format(__name__))
        
        # Get the prompt
        prompt = self.prompts[self.current_mode][file_position]

        # Get the filetypes that are allowed for this position.
        gui_filetypes = list() 
        file_type = self.lst_filetypes[self.current_mode][file_position] # returns list of 0 - n elements
        for filetype in file_type:
            if filetype.lower() in self.filetypes.keys():
                gui_filetypes.append(self.filetypes[filetype.lower()][0])

        gui_filetypes.append(("All Files", "*.*"))  # Always give the user an option to select all files.

        # Get the filepath using GUI
        path = filedialog.askopenfilename(parent=self,
                                          title=prompt,
                                          initialdir=self.WorkingDirectory.get(),
                                          filetypes=gui_filetypes)

        # Validate the path and process valid paths
        if path:  # Filters None and '' path values
            print(path)
            # Set the appropriate variables
            self.current_paths[self.current_mode][file_position].set(path)
            self.current_filenames[self.current_mode][file_position].set(os.path.basename(path))

            # Store the directory that the user last selected
            self.WorkingDirectory.set(os.path.dirname(path))

            # Update the aircraft and ground object names
            if self.current_mode in ['Aircraft', 'Ground'] and path.endswith(".dat") and file_position == 0:
                self.update_air_gnd_label(path)

    def on_tab_change(self, event):
        """Run a function when the air/gnd/sce tab changes"""
        # Set the current tab being displayed
        self.current_mode = event.widget.tab('current')['text'].split()[0]

    def quit_program(self, force_close=False):
        """Provide a graceful way to close the program. If  we implement a way to check to see what has been saved,
        then we can provide a more meaningful way to check what has been saved or not."""

        if force_close is False:
            unsaved_changes = False
            # Check to see if there are unsaved changes.

            # Check to see if there are any elements in the various input fields (i.e. files selected and not stored)
            entries = list()
            for group in self.lst_types:
                for var in self.current_paths[group]:
                    entries.append(var.get())
                for var in self.current_filenames[group]:
                    entries.append(var.get())

            if len(list(filter(None, entries))) > 0:
                # There are unsaved changes
                unsaved_changes = True

            # Regardless of detection method, raise alert to show user that there are unsaved changes that will be lost.
            if unsaved_changes is True:
                title = "Do you want to close?"
                msg = "You will lose unsaved work."
                result = messagebox.askyesno(parent=self.parent, title=title, message=msg)

                if result == 'no':
                    return

        self.parent.destroy()

    def assemble_pack(self):
        """This function will take the filepaths, naming and organization."""

        self.functionality_not_available_popup("assemble_pack")

        # Ask the user where to export the pack to.


        # Perform filepath validation


        # Perform dat file identify line validation and compare to stored data.


        # Force Scenery names to replace spaces with underscores


class AirGndLSTEntry:
    bad_identify_characters = [" ", '"']
    replacement_characters = ["_", ""]
    def __init__(self):
        # All Files use the same nomenclature as the labels for simpler automatic transfer of information between
        # the class instance and the GUI.
        self.DAT = ""
        self.Visual_Model = ""
        self.Collision = ""
        self.Cockpit = ""
        self.Coarse = ""
        self.IDENTIFY = ""
        self.dat_rename = False
        self.dat_new_name = ""

    def assign_values(self, dict_of_values):
        for key, value in dict_of_values.items():
            if key in self.__dict__.keys():
                setattr(self, key.replace(" ", "_"), value)

    def make_lst_entry(self, pack_name, user_name):
        """Make a single string for a line in the LST File."""
        parts = [make_pack_filepath(self.DAT, pack_name, user_name, self.dat_new_name),
                 make_pack_filepath(self.Visual_Model, pack_name, user_name),
                 make_pack_filepath(self.Collision, pack_name, user_name),
                 make_pack_filepath(self.Cockpit, pack_name, user_name),
                 make_pack_filepath(self.Coarse, pack_name, user_name)]
        return " ".join(parts)

    def write_save_config_data(self):
        """Generate the data needed to completely write the data stored in this class instance to a save file."""
        return self.__dict__

    def assign_new_identify(self, new_identify):
        for bad_char, replacement in zip(self.bad_identify_characters, self.replacement_characters):
            new_identify.replace(bad_char, replacement)
        self.IDENTIFY = new_identify

    def generate_pack(self, output_directory):
        """Copy the files from their source to the new directory. If the dat file needs to be renamed, do so and
        ensure that the IDENTIFY line is set to whatever is in the class instance."""

        # Generate output paths for all files.
        original_paths = [self.DAT, self.Visual_Model, self.Collision, self.Cockpit, self.Coarse]
        output_paths = [os.path.join(output_directory, os.path.basename(i)) for i in original_paths]
        if self.dat_rename:
            output_paths[0] = os.path.join(output_directory, self.dat_new_name)

        # Move the files to the new locations
        for source, destination in zip(original_paths, output_paths):
            if os.path.isfile(source):
                shutil.copyfile(source, destination)
            else:
                raise FileNotFoundError("Could not find file {} for {}.".format(source, self.IDENTIFY))

        # Overwrite the IDENTIFY line to force it to match what has been defined in the tool.
        # Need to see if there is a better alternate method
        new_identify_line = 'IDENTIFY "{}"\n'.format(self.IDENTIFY)

        with open(output_paths[0], mode='r') as old_dat_file:
            old_dat = [line.rstrip() for line in old_dat_file.readlines()]
        for idx, line in enumerate(old_dat):
            if line.startswith("IDENTIFY "):
                old_dat[idx] = new_identify_line
                break
        with open(output_paths[0], mode='w') as new_dat_file:
            for line in old_dat:
                new_dat_file.write(line)


class SceLSTEntry:
    bad_map_name_characters = [" ", '"']
    replacement_characters = ["_", ""]
    def __init__(self):
        # All Files use the same nomenclature as the labels for simpler automatic transfer of information between
        # the class instance and the GUI.
        self.Map = ""
        self.Start_Position = ""
        self.Mission = ""
        self.air_race = False
        self.map_name = ""

    def make_lst_entry(self, pack_name, user_name):
        parts = [self.map_name.replace(" ", "_"),
                 make_pack_filepath(self.Map, pack_name, user_name),
                 make_pack_filepath(self.Start_Position, pack_name, user_name),
                 make_pack_filepath(self.Mission, pack_name, user_name)]

        if self.air_race is True:
            parts.append("AIRRACE")

        return " ".join(parts)

    def assign_values(self, dict_of_values):
        for key, value in dict_of_values.items():
            if key in self.__dict__.keys():
                setattr(self, key.replace(" ","_"), value)

    def write_save_config_data(self):
        return self.__dict__


def extract_identify_from_dat(dat_file_path):
    """Find the IDENTIFY line in a DAT file and return the name

    inputs
    dat_file_path (str): path to where the dat file is

    outputs
    name (str): IDENTIFY of the aircraft or ground object
    """

    # Validate the dat file exists and is a dat file
    if dat_file_path.endswith(".dat") is False or os.path.isfile(dat_file_path) is False:
        return ""

    # Import DAT File
    with open(dat_file_path, mode='r', errors='ignore') as dat_file:
        dat = dat_file.readlines()
        for idx, line in enumerate(dat):
            if line.endswith("\n"):
                dat[idx] = line[:-1]

    # Find aircraft/ground object name
    identify_idx = 0
    for line in dat:
        if line.startswith("IDENTIFY"):
            break
        identify_idx += 1

    # Remove unnecessary parts of the raw dat file line.
    name = dat[identify_idx][8:]  # Trim the dat variable form the beginning.
    if '#' in name:
        name = name.split('#')[0]  # Trim elements after in-line comment
    if '"' in name:
        name = name.split('"')[1]  # Remove the quotation marks and extract contents within them.
        # NOTE: Most Ground Object Identify Lines do not have quotation marks

    return name



def make_pack_filepath(raw_filepath, pack_name, user_name, new_filename=""):
    if new_filename:
        return '"users/{}/{}/{}"'.format(user_name,pack_name,new_filename)
    else:
        return '"users/{}/{}/{}"'.format(user_name, pack_name, os.path.basename(raw_filepath))



class Dialog(Frame):
    """A helper class to support custom pop-up windows that appear above the main GUI class.
    This is primarily planned for the Settings Menu"""
    def __init__(self,parent,title=""):
        self.applet = Toplevel(parent)
        self.applet.transient(parent)
        self.applet.title(title)
        self.applet.resizable(False,False)
        self.applet.grab_set()
        self.applet.geometry("+{}+{}".format(parent.winfo_rootx()+50,
                                             parent.winfo_rooty()+50))
        super().__init__(self.applet)
        self.pack(fill='both',expand=True)


class Settings(Dialog):
    """Provide a convenient way to set the program's settings in a custom GUI."""
    def __init__(self, parent, title="Settings"):
        super().__init__(parent, title)
        self.parent = parent
        self.applet.title = title

        # Define local GUI variables for the Settings GUI Entries and initialize with their current values in from the
        # main program GUI.
        self.Working_Directory = StringVar(value=self.parent.settings['working_directory'])
        self.UserName = StringVar(value=self.parent.settings['user_name'])
        self.ListBoxWidth = StringVar(value=str(self.parent.settings['preview_char_width']))
        self.ListBoxHeight = StringVar(value=str(self.parent.settings['preview_num_rows']))
        self.AskBeforeDeletingLstEntry = IntVar(value=int(self.parent.settings['ask_before_entry_removal']))

        # OptionMenu lists need to be strings.
        self.preview_num_row_options = [str(i) for i in [5, 10 ,15 ,20, 25]]
        self.preview_line_character_width_options = [str(i) for i in [20, 35, 30, 35, 40]]
        self.selected_num_rows = StringVar(value=str(self.parent.settings['preview_num_rows']))
        self.selected_char_width = StringVar(value=str(self.parent.settings['preview_char_width']))
        self.ask_before_delete_entry = IntVar(value=self.parent.settings['ask_before_entry_removal'])

        self.build_settings_gui()

    def build_settings_gui(self):
        """Build the custom GUI for the settings"""

        Main = Frame(self.applet)
        row_num = 0
        Label(Main, text="User Name:").grid(row=row_num, column=0, sticky="W")
        Entry(Main, textvariable=self.UserName, width=30).grid(row=row_num, column=1, sticky="WE", columnspan=2)

        row_num += 1
        Label(Main, text="Working Directory").grid(row=row_num, column=0, sticky="W")
        Entry(Main, textvariable=self.Working_Directory, width=30).grid(row=row_num, column=1, sticky="WE")
        Button(Main, text="Select Folder", command=self.select_working_folder).grid(row=row_num, column=2, sticky="NSEW")

        row_num += 1
        Label(Main, text="Preview Rows:").grid(row=row_num, column=0, sticky="W")
        OptionMenu(Main,
                   self.selected_num_rows,
                   self.selected_num_rows.get(),
                   *self.preview_num_row_options
                   ).grid(row=row_num, column=1, sticky="EW")

        row_num += 1
        Label(Main, text="Preview Width:").grid(row=row_num, column=0, sticky="W")
        OptionMenu(Main,
                   self.selected_char_width,
                   self.selected_char_width.get(),
                   *self.preview_line_character_width_options
                   ).grid(row=row_num, column=1, sticky="EW")

        row_num += 1
        Checkbutton(Main,
                    text="Ask before deleting LST entries?",
                    variable=self.ask_before_delete_entry
                    ).grid(row=row_num, column=0, columnspan=3, sticky="EW")

        row_num += 1
        Separator(Main).grid(row=row_num, column=1, columnspan=2, sticky="EW", pady=5)

        row_num += 1
        Button(Main, text="Cancel", command=self.close_settings).grid(row=row_num, column=0, columnspan=1, sticky="NSEW")
        Button(Main, text="Save", command=self.save_settings).grid(row=row_num, column=1, columnspan=2, sticky="NSEW")

        Main.pack()

    def save_settings(self):
        """Update the parent's settings dict and then close, use the parent class to write the settings to file."""
        # Update the parent's settings based on the user's selections.
        self.parent.settings['preview_char_width'] = int(self.selected_char_width.get())
        self.parent.settings['preview_num_rows'] = int(self.selected_num_rows.get())
        self.parent.settings['working_directory'] = self.Working_Directory.get()
        self.parent.settings['user_name'] = self.UserName.get()
        self.parent.settings['ask_before_entry_removal'] = int(self.ask_before_delete_entry.get())

        # Close the window
        self.applet.destroy()

    def close_settings(self):
        """Close the settings without saving."""
        self.applet.destroy()

    def select_working_folder(self):
        """Select a default working folder"""
        prompt = "Select the Directory where you have your modding files."
        path = filedialog.askdirectory(parent=self, title=prompt, mustexist=True, initialdir=self.Working_Directory.get())

        # Validate the path
        if path:
            # Set the appropriate variable
            self.Working_Directory.set(path)


def split_list(input_list, delimiter_element):
    """Split a list into a list of lists based on a delimiter element or elements, deleting empty lists along the way

    inputs:
    input_list (list): a list that needs to be split
    delimiter_element (list, any): A list of elements or a single element that we can delimit on.
    """
    # Convert to list
    if isinstance(delimiter_element, list) is False:
        delimiter_element = [delimiter_element]

    # Verify that a delimiter is in the input_list
    missing_delimiter = True
    if any(x in input_list for x in delimiter_element):
        missing_delimiter = False

    # Exit early if there is nothing to split over.
    if missing_delimiter is True:
        return [input_list]

    output = list()
    temp = list()
    for element in input_list:
        if element in delimiter_element and len(temp) > 0:
            output.append(temp)
            temp = list()
        else:
            temp.append(element)
    output.append(temp)

    return output



# Run the program. This must be at the end of the file.
if __name__ == "__main__":
    main()
    
