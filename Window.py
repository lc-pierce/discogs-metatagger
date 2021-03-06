#-----------------------------------------------------------------------------#
#   File: Window.py                                                           #
#   Author: Logan Pierceall                                                   #
#                                                                             #
#   This module contains all of the code pertaining to the program's GUI and  #
#       to the program's interaction with the Discogs API. Consequently, this #
#       module depends on the 'discogs_client' API found at                   #
#       https://pypi.org/project/python3-discogs-client/                      #
#                                                                             #
#   This module doesn't contain any of the code related to direct             #
#       manipulation of file metadata information. That code can be found     #
#       within 'FileData.py'.                                                 #
#-----------------------------------------------------------------------------#

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Tk
from tkinter import ttk
from urllib.parse import urlparse

import discogs_client

import FileData

class TagWindow(Tk):

    def __init__(self, *args, **kwargs):
    
        super().__init__(*args, **kwargs)
        
        # Account for screen boundaries and taskbar size
        WIN_H = self.winfo_screenheight() - 80
        WIN_W = self.winfo_screenwidth() - 10
        
        self.geometry(f'{WIN_W}x{WIN_H}+0+0')
        self.title('Discogs Metadata Tagger')
        self.resizable(False, False)
        
        # Widget option defaults
        self.bg = '#708090'
        self.fg = '#f5fffa'
        self.font = ('Microsoft Tai Le', 12)
        
        # Boolean to determine if the user has provided their Discogs API token
        self.token_flag = False
        
        # Boolean to determine if data from a Discogs page has been loaded
        self.data_loaded = False
        
        # Boolean to determine if music files have been added to the treeview
        self.files_loaded = False
        
        # List that holds the file paths for loaded music files
        self.added_files = []
        
        self.PopulateWindow()
    
    
    def AddFiles(self):
        """Add music files to the treeview for editing."""
        
        _types = (('FLAC', '*.flac'), ('MP3', '*.mp3'))
        files = list(filedialog.askopenfilenames(filetypes=_types))
        if not files:
            return
        
        self.files_loaded = True
        bad_files = []
        for i, file in enumerate(files, 0):
            
            # If the operation is unsuccessful, 'bad_file' will contain the
            #   filename of the inaccessible file
            result, bad_file = FileData.ParseFile(file, self.tree, i)
            if not result:
                tk.messagebox.showerror('Error',
                                        f'Unable to access {bad_file}')
                # Add file index to list of inaccessible files
                bad_files.append(i)
        
        if not bad_files:
            self.added_files = files
            return
        
        # Create a new copy of the 'files' list without inaccessible files
        self.added_files = []
        for i, file in enumerate(files, 0):
            if i in bad_files:
                continue
            self.added_files.append(file)
    
    
    def CopyTracklist(self):
        """Copy track titles from the listbox to the music files.
        
        This function is called by the 'Send Track Titles' button.
        """
        
        if not self.files_loaded:
            return
        
        # Show a warning message before allowing the titles to be altered
        msg = 'This action will copy the track titles to the listed files\n' \
              'in the file viewer below. Before proceeding, make sure the\n' \
              'tracks are in correct order.\n\n' \
              'Track numbers can be directly edited by double-clicking in\n' \
              'the "#" column. The list can be sorted into order by clicking\n' \
              'on the "#" column heading.\n\nProceed?'
        ask = tk.messagebox.askquestion('WARNING', msg)
        if not ask:
            return
        
        bad_files = []
        i = 0
        for file, iid, title in zip(self.added_files, self.tree.get_children(),
                                    self.listbox.get(0, 'end')):
            
            # If the operation is successful, 'res_str' contains the title
            #   string used to update the treeview widget. If unsuccessful,
            #   'res_str' contains the filename of the inaccessible file
            result, res_str = FileData.UpdateTrackTitle(file, title, iid, i)
            if not result:
                tk.messagebox.showerror('Error', f'Unable to access {res_str}')
                # Add file index to list of inaccessible files
                bad_files.append(i)
            else:
                # Update the treeview widget with the title
                self.tree.set(iid, column='#3', value=res_str)
            
            i += 1
        
        # If inaccessible files were found, offer to remove them from the
        #   program
        if bad_files:
            self.RemoveFiles(bad_files)
    
    
    def CopyTrackNumbers(self):
        """Insert track numbers into file metadata.
        
        This function is called by the 'Fill Track Numbers' button.
        """
        
        if not self.files_loaded:
            return
        
        bad_files = []
        i = 1
        for file, iid in zip(self.added_files, self.tree.get_children()):
            
            # If the operation is unsuccessful, 'res_str' will contain the
            #   filename of the inaccessible file
            result, res_str = FileData.UpdateTrackNumbers(file, iid, i)
            if not result:
                # Add file to list of inaccessible files
                tk.messagebox.showerror('Error', f'Unable to access {res_str}')
                # Add file index to list of inaccessible files
                bad_files.append(i)
            else:
                # Update the treeview widget with the track number
                self.tree.set(iid, column='#1', value=str(i))
            
            i += 1
        
        # If inaccessible files were found, offer to remove them from the
        #   program
        if bad_files:
            self.RemoveFiles(bad_files)
    
    
    def CreateButton(self, parent, _text, _cmd, big_tag):
        """Initialize and return a tkinter Button widget.
        
        Arguments:
        parent -- the Button's parent object
        _text -- the text displayed on the Button
        _cmd -- the function called by the Button
        big_tag -- boolean indicator for the size of Button features
        """
        
        # 'big_tag' buttons are all the buttons not directly tied to sending
        #   individual metadata tags
        if big_tag:
            _height = 2
            _width = 40
            _font = ('Microsoft Tai Le', 15)
        else:
            _height = 1
            _width = 15
            _font = ('Microsoft Tai Le', 12)
     
        return tk.Button(parent, text=_text, command=_cmd, height=_height,
                         width=_width, font=_font, relief='groove',
                         bg=self.bg, activebackground=self.bg,
                         fg=self.fg, activeforeground=self.fg,
                         takefocus=0)
    
    
    def CreateEntry(self, parent, _var, _width=30):
        """Initialize and return a tkinter Entry widget.
        
        Arguments:
        parent -- the Entry's parent frame
        _var -- variable used to retrieve Entry's contents
        _width -- width of the Entry widget
        """
    
        return tk.Entry(parent, textvariable=_var, width=_width,
                        font=self.font)
    
    
    def CreateFileTree(self, parent):
        """Initialize the Treeview used to display the loaded music files.
        
        Arguments:
        parent -- the Treeview's parent frame
        """
        
        self.tree = ttk.Treeview(parent, columns=('#1', '#2', '#3',
                                                  '#4', '#5', '#6',
                                                  '#7', '#8', '#9'))
        self.tree.pack(fill='both', expand='true')
        
        # Set column headings
        self.tree.heading('#1', text='#', command=self.SortByTrackNumber)
        self.tree.heading('#2', text='Filename')
        self.tree.heading('#3', text='Track Title')
        self.tree.heading('#4', text='Artist')
        self.tree.heading('#5', text='Album Artist')
        self.tree.heading('#6', text='Album')
        self.tree.heading('#7', text='Year')
        self.tree.heading('#8', text='Genre')
        self.tree.heading('#9', text='Publisher')
        
        # Hide columns without headings
        self.tree['show'] = 'headings'
        
        # Set column sizes
        self.tree.column('#1', width=30, stretch=False)
        self.tree.column('#2', width=30, stretch=False)
        self.tree.column('#4', width=120, stretch=False)
        self.tree.column('#5', width=120, stretch=False)
        self.tree.column('#6', width=180, stretch=False)
        self.tree.column('#7', width=80, stretch=False)
        self.tree.column('#8', width=100, stretch=False)
        self.tree.column('#9', width=120, stretch=False)
        
        # Create alternative background color for odd rows to improve 
        #   readability
        self.tree.tag_configure('oddrow', background='#cbdaf2')
        
        # Bind double-clicking on cells to edit contents
        self.tree.bind('<Double-Button-1>', self.DoubleClick)
    
    
    def CreateFrame(self, parent):
        """Initialize and return a tkinter Frame widget.
        
        Arguments:
        parent -- the Frame's parent object
        """
    
        return tk.Frame(parent, padx=5, pady=5, bg=self.bg)
    
    
    def CreateLabel(self, parent, _text, _font=None, _anchor='w'):
        """Initialize and return a tkinter Label widget.
        
        Arguments:
        parent -- the Label's parent frame
        _text -- the text displayed on the Label
        _font -- the font used by the Label's text
        _anchor -- text positioning (default w, i.e., left-hand side
        """
    
        if not _font:
            _font = self.font
    
        return tk.Label(parent, text=_text, font=_font, anchor=_anchor,
                        bg=self.bg, fg=self.fg, width=10, padx=5, pady=5)
    
    
    def CreateLoadButtons(self, parent):
        """Initialize buttons used to load music files and copy all metadata.
        
        Arguments:
        parent -- the parent object for the two buttons
        """
    
        frame = self.CreateFrame(parent)
        frame.pack(fill='both', expand='true')
        
        copy_button = self.CreateButton(frame, 'Send All Data To Files',
                                        self.UpdateAll, big_tag=True)
        copy_button.pack(side='left', expand='true')
        
        add_button = self.CreateButton(frame, 'Select Files To Edit',
                                       self.AddFiles, big_tag=True)
        add_button.pack(side='right', expand='true')
    
    
    def CreateMetadataFields(self, text_parent, number_parent):
        """Initialize set of widgets for each editable metadata tag.
        
        Arguments:
        text_parent -- parent object for text-based tags
        number_parent -- parent object for number-based tags
        """
        
        
        def CreateField(parent, label_text, tag, entry_var, e_width=None):
            """Initialize a Frame, Label, Entry, & Button for a metadata tag.
            
            Arguments:
            parent -- parent object for the Frame
            label_text -- text displayed on the Label
            tag -- metadata tag attached to the Button's command function
            entry_var -- retrieval variable for Entry's contents
            e_width -- width of the Entry widget
            """
            
            if not e_width:
                e_width = 30
            
            frame = self.CreateFrame(parent)
            frame.pack(fill='x')
            
            label = self.CreateLabel(frame, label_text)
            label.pack(side='left')
            
            entry = self.CreateEntry(frame, entry_var, e_width)
            entry.pack(side='left')
            
            button = self.CreateButton(frame, 'Send Data',
                                       _cmd=lambda: self.SendData(tag),
                                       big_tag=False)
            button.pack(side='left')
        
        
        self.artist = tk.StringVar()
        CreateField(text_parent, 'Artist', 'Artist', self.artist)
        
        self.album_artist = tk.StringVar()
        CreateField(text_parent, 'Album Artist', 'AlbumArtist',
                    self.album_artist)
        
        self.album = tk.StringVar()
        CreateField(text_parent, 'Album', 'Album', self.album)
        
        self.genre = tk.StringVar()
        CreateField(text_parent, 'Genre', 'Genre', self.genre)
        
        self.publisher = tk.StringVar()
        CreateField(text_parent, 'Publisher', 'Organization', self.publisher)
        
        self.release_date = tk.StringVar()
        CreateField(number_parent, 'Date', 'Date', self.release_date, 10)
        
        self.total_tracks = tk.StringVar()
        CreateField(number_parent, 'Track Total', 'TrackTotal',
                    self.total_tracks, 10)
        
        fill_button = self.CreateButton(number_parent, 'Fill Track Numbers',
                                        self.CopyTrackNumbers, big_tag=False)
        fill_button.pack(fill = 'x')
    
    
    def CreateTracklistView(self, parent):
        """Initialize Listbox widget that holds track titles.
        
        Arguments:
        parent -- the parent frame for all widgets
        """
        
        # Place the listbox within a labelframe with an attached button that
        #   sends the contents to the files
        button = self.CreateButton(parent, 'Send Track Titles',
                                   self.CopyTracklist, big_tag=False)
        labelframe = tk.LabelFrame(parent, labelwidget=button, bg=self.bg)
        labelframe.pack(fill='both', expand='true')
        
        scrollbar = tk.Scrollbar(labelframe)
        scrollbar.pack(side='right', fill='y')
        
        self.listbox = tk.Listbox(labelframe, yscrollcommand=scrollbar.set,
                                  font=self.font)
        self.listbox.pack(side='left', fill='both', expand='true')
        
        scrollbar['command'] = self.listbox.yview
    
    
    def CreateURLFields(self, parent):
        """Initialize a Label, Entry, & Buttons to load a Discogs release URL.
        
        Arguments:
        parent -- parent frame for all widgets
        """
        
        label = self.CreateLabel(parent, 'Enter Discogs URL:',
                                 _font=('Microsoft Tai Le', 16, 'bold'),
                                 _anchor='center')
        label.pack(fill='x')
        
        # Create text entry box to provide Discogs URL
        self.URL = tk.StringVar()
        entry = self.CreateEntry(parent, self.URL, 100)
        entry.pack()
        
        # Create URL load button and window reset button
        button_frame = self.CreateFrame(parent)
        button_frame.pack()
        
        URL_button = self.CreateButton(button_frame, 'Click To Load URL Data',
                                       self.ValidateURL, big_tag=True)
        URL_button.pack(side='left')
        
        reset_button = self.CreateButton(button_frame, 'Reset Window',
                                         self.ResetWindow, big_tag=True)
        reset_button.pack(side='right')
    
    
    def DoubleClick(self, event):
        """Edit the contents of a Treeview cell.
        
        This is an event function bound to double-clicking within the Treeview
            widget. It becomes unbound when the edit window appears and gets
            re-bound when the window is destroyed.
        """
    
        # Retrieve the chosen row and column
        self.clicked_column = self.tree.identify_column(event.x)
        self.clicked_row = self.tree.identify_row(event.y)
        
        # Load a window to edit the value
        self.edit_window = tk.Toplevel(self)
        height = 100
        width = 300
        y_pos = int((self.winfo_screenheight() / 2) - (height / 2))
        x_pos = int((self.winfo_screenwidth() / 2) - (width / 2))
        self.edit_window.geometry(f'{width}x{height}+{x_pos}+{y_pos}')
        
        frame = self.CreateFrame(self.edit_window)
        frame.pack(fill='both', expand='true')
        
        label = self.CreateLabel(frame, 'Enter new value:')
        label.pack(fill='both', expand='true')
        
        self.new_value = tk.StringVar()
        entry = self.CreateEntry(frame, self.new_value)
        entry.pack(fill='x', expand='true')
        entry.focus_force()
        
        button = self.CreateButton(frame, 'Update Field', self.UpdateField,
                                   big_tag=False)
        button.pack(fill='both', expand='true')
        
        # Bind both 'Enter' keys to be equivalent to clicking the button
        self.edit_window.bind('<Return>', lambda e: self.UpdateField())
        self.edit_window.bind('<KP_Enter>', lambda e: self.UpdateField())
        
        # Remove binding on double-click until the current edit window gets
        #   destroyed
        self.tree.unbind('<Double-Button-1>')
        self.edit_window.bind('<Destroy>', self.RestoreDoubleClick)
    
    
    def FillEntrys(self):
        """Populate metadata Entry widgets with corresponding Discogs info.
        
        This function is called by the 'Click To Load URL Data' button. It
            uses the Discogs client API to pull information for each metadata
            tag.
        """
        
        try:
            release = self.client.release(self.release_number)
            
            # Fill the text entry boxes
            self.artist.set(release.artists[0].name.title())
            self.album_artist.set(release.artists[0].name.title())
            self.album.set(release.title.title())
            self.genre.set(release.styles[0].title())
            self.publisher.set(release.labels[0].name.title())
            self.release_date.set(release.year)
            
            # Fill the 'tracklist' listbox
            for i, track_title in enumerate(release.tracklist, 1):
                self.listbox.insert('end', f'{i}. {track_title.title.title()}')
        
        except:
            msg = 'Release not found in Discogs database.\n' \
                  'Please double-check the entered URL.'
            tk.messagebox.showerror('Error', msg)
            return
        
        # Update the flag to prevent loading new data until the window
        #   gets reset
        self.data_loaded = True
    
    
    def GetUserToken(self):
        """Initialize a window to retrieve the user's Discogs API token.
        
        This function is called by the 'Click To Load URL Data' button the
            first time the button is pressed. A user token is necessary to
            enable retrieving information from the Discogs database.
        """
    
        token_h = 100
        token_w = 300
    
        # Obtain x&y coordinates to place window in center of screen
        y_pos = int((self.winfo_screenheight() / 2) - (token_h / 2))
        x_pos = int((self.winfo_screenwidth() / 2) - (token_w / 2))
        
        self.token_win = tk.Toplevel(self)
        self.token_win.geometry(f'{token_w}x{token_h}+{x_pos}+{y_pos}')
        self.token_win.resizable(False, False)
        
        frame = self.CreateFrame(self.token_win)
        frame.pack(fill='both', expand='true')
        
        label = self.CreateLabel(frame, 'Enter user token:')
        label.pack(fill='both', expand='true')
        
        self.user_token = tk.StringVar()
        entry = self.CreateEntry(frame, self.user_token)
        entry.pack(fill='both', expand='true')
        entry.focus_force()
        
        button = self.CreateButton(frame, 'Submit', self.InitializeClient,
                                   big_tag=False)
        button.pack(fill='both', expand='true')
    
    
    def InitializeClient(self):
        """Initialize the Discogs API client.
        
        This function is called by the 'Submit' button located on the window
            created by GetUserToken().
        """
        
        token = self.user_token.get().lstrip().rstrip()
        if not token:
            return
        
        try:
            self.client = discogs_client.Client('UpdateFiles', user_token=token)
        except:
            tk.messagebox.showerror('Error',
                                    'Error authorizing provided credentials.')
        else:
            self.token_flag = True
            self.token_win.destroy()
            self.FillEntrys()
    
    
    def PopulateWindow(self):
        """Initialize the main window Frames and their widget contents."""
        
        # Create a frame that covers the entire window
        self.main_frame = self.CreateFrame(self)
        self.main_frame.pack(fill='both', expand='true')
        
        # Create the URL frame and widgets
        top_frame = self.CreateFrame(self.main_frame)
        top_frame.pack(side='top', fill='x')
        self.CreateURLFields(top_frame)
        
        # Create a frame that holds all of the widgets used to update files
        middle_frame = self.CreateFrame(self.main_frame)
        middle_frame.pack(fill='x')
        
        # Create the metadata fields
        text_fields_frame = self.CreateFrame(middle_frame)
        text_fields_frame.pack(side='left', fill='y')
        number_fields_frame = self.CreateFrame(middle_frame)
        number_fields_frame.pack(side='left', fill='y')
        self.CreateMetadataFields(text_fields_frame, number_fields_frame)
        
        # Create a listbox and labelframe to hold the track titles
        listbox_frame = self.CreateFrame(middle_frame)
        listbox_frame.pack(side='right', fill='both', expand='true')
        self.CreateTracklistView(listbox_frame)
        
        # Create the buttons to load files into the tree and to copy data from
        #   text entry boxes to the files
        button_frame = self.CreateFrame(self.main_frame)
        button_frame.pack(side='top', fill='x')
        self.CreateLoadButtons(button_frame)
        
        # Create the file viewer tree
        file_tree_frame = self.CreateFrame(self.main_frame)
        file_tree_frame.pack(fill='both', expand='true')
        self.CreateFileTree(file_tree_frame)
    
    
    def RemoveFiles(self, index_list):
        """Remove inaccessible files from the Treeview widget.
        
        This function is called whenever another function attempts to edit
            metadata information and is unable to access/alter the file.
        Arguments:
        index_list -- list of files list indeces that were inaccessible
        """
        
        msg = 'Inaccessible files were found in the files list. Would\n' \
              'you like to remove these files from the program?'
        ask = tk.messagebox.askyesno('Remove Files?', msg)
        if not ask:
            return
        
        # Update the list of files added to the program
        new_list = []
        for i, file in enumerate(self.added_files, 0):
            if i in index_list:
                continue
            new_list.append(file)
        self.added_files = new_list
        
        # Remove the bad files from the treeview widget
        tree_contents = self.tree.get_children()
        iid_list = []
        for index in index_list:
            iid_list.append(tree_contents[index])
        for iid in iid_list:
            self.tree.delete(iid)
    
    
    def ResetWindow(self):
        """Return all window widgets and global vars to their initial states.
        
        This function is called by the 'Reset Window' button.
        """
        
        # Reset gobal variables
        self.data_loaded = False
        self.files_loaded = False
        self.added_files = []
        
        # Reset entry variables
        self.URL.set('')
        self.artist.set('')
        self.album_artist.set('')
        self.album.set('')
        self.genre.set('')
        self.publisher.set('')
        self.release_date.set('')
        self.total_tracks.set('')
        
        # Clear the listbox and treeview contents
        self.listbox.delete(0, 'end')
        for iid in self.tree.get_children():
            self.tree.delete(iid)
    
    
    def RestoreDoubleClick(self, event):
        """Re-bind double-clicking to edit Treeview cells."""
        
        self.tree.bind('<Double-Button-1>', self.DoubleClick)
    
    
    def SendData(self, tag):
        """Copy data from Entry widgets to loaded music files.
        
        This function is called by every button created by
            CreateMetadataFields().
        Arguments:
            tag -- the string of the metadata tag name to update
        """
        
        # If no files present to update, take no action
        if not self.files_loaded:
            return
        
        # Access the appropriate entry box variable
        if tag == 'Album':
            var_text = self.album.get().lstrip().rstrip()
        elif tag == 'AlbumArtist':
            var_text = self.album_artist.get().lstrip().rstrip()
        elif tag == 'Artist':
            var_text = self.artist.get().lstrip().rstrip()
        elif tag == 'Date':
            var_text = self.release_date.get().lstrip().rstrip()
        elif tag == 'Genre':
            var_text = self.genre.get().lstrip().rstrip()
        elif tag == 'Organization':
            var_text = self.publisher.get().lstrip().rstrip()
        elif tag == 'TrackTotal':
            var_text = self.total_tracks.get().lstrip().rstrip()
        
        bad_files = []
        i = 0
        for file, iid in zip(self.added_files, self.tree.get_children()):
            
            # If the operation is successful, 'res_str' will contain the
            #   treeview column that needs to be updated. If unsuccessful,
            #   'res_str' will contain the filename of the inaccessible file
            result, res_str = FileData.UpdateMetadata(file, tag, var_text)
            if not result:
                tk.messagebox.showerror('Error', f'Unable to access {res_str}')
                # Add file index to list of inaccessible files
                bad_files.append(i)
            else:
                # Update the treeview widget with the new metadata
                self.tree.set(iid, res_str, value=var_text)
            
            i += 1
        
        # If inaccessible files were found, offer to remove them from the
        #   program
        if bad_files:
            self.RemoveFiles(bad_files)
    
    
    def SortByTrackNumber(self):
        """Sort Treeview files by increasing track number column order."""
        
        def SortFunc(e):
            """Return int value for track number column cell."""
            return int(self.tree.set(e, column='#1'))
        
        # Retrieve the iid for every treeview row
        tree_contents = list(self.tree.get_children())
        
        # Sort list in ascending track number order
        try:
            tree_contents.sort(key=SortFunc)
        except ValueError:
            msg = 'One or more fields does not contain a number'
            tk.messagebox.showerror('Error', msg)
            return

        # Update the treeview rows to match the sorted files
        for i, iid in enumerate(tree_contents, 0):
            self.tree.move(iid, '', i)
        
        # Update the added files list to reflect the sort
        added_copy = self.added_files.copy()
        self.added_files = []
        for iid in tree_contents:
            # IID naming convention is 'song#', this isolates the '#'
            index = int(iid[4:])
            self.added_files.append(added_copy[index])
        
        # Update the tree item tags to maintain row coloring consistent
        #   with the original creation style
        for iid in tree_contents:
            if (self.tree.index(iid)) % 2 == 0:
                self.tree.item(iid, tags='evenrow')
            else:
                self.tree.item(iid, tags='oddrow')
    
    
    def UpdateAll(self):
        """Copy all data from metadata Entry widgets to loaded music files.
        
        This function is called by the 'Send All Data To Files' button. It does
            not send the track titles from the Listbox.
        """
        
        if not self.files_loaded:
            return
        
        data = [['Album', self.album.get().lstrip().rstrip()],
                ['AlbumArtist', self.album_artist.get().lstrip().rstrip()],
                ['Artist', self.artist.get().lstrip().rstrip()],
                ['Date', self.release_date.get().lstrip().rstrip()],
                ['Genre', self.genre.get().lstrip().rstrip()],
                ['Organization', self.publisher.get().lstrip().rstrip()],
                ['TrackTotal', self.total_tracks.get().lstrip().rstrip()]]
        
        for entry in data:
            bad_files = []
            i = 0
            for file, iid in zip(self.added_files, self.tree.get_children()):
                
                # If the operation is successful, 'res_str' will contain the
                #   treeview column that needs to be updated. If unsuccessful,
                #   'res_str' will contain the filename of the inaccessible
                #   file
                result, res_str = FileData.UpdateMetadata(file, entry[0],
                                                          entry[1])
                if not result:
                    tk.messagebox.showerror('Error',
                                            f'Unable to access {res_str}')
                    # Add file index to list of inaccessible files
                    bad_files.append(i)
                else:
                    # Update the treeview widget with the new metadata
                    self.tree.set(iid, res_str, value=entry[1])
                
                i += 1
            
            # If inaccessible files were found, offer to remove them from the
            #   program
            if bad_files:
                self.RemoveFiles(bad_files)
    
    
    def UpdateField(self):
        """Edit the contents of a single, user-clicked Treeview cell.
        
        This function is called by the 'Update Field' button located on the
            pop-up window created by the DoubleClick() function.
        """
        
        _value = self.new_value.get().lstrip().rstrip()
        if not _value:
            return
        
        # Retrieve the filename to update
        file = self.added_files[self.tree.index(self.clicked_row)]
        
        # Retrieve the metadata tag for the cell
        tag = FileData.ConvertColToTag(self.clicked_column)
        
        # If the operation is successful, 'res_str' will contain the treeview
        #   column that needs to be updated. If unsuccessful, 'res_str' will
        #   contain the filename of the inaccessible file
        result, res_str = FileData.UpdateMetadata(file, tag, _value)
        if not result:
            tk.messagebox.showerror('Error', f'Unable to access {res_str}')
            # Offer to remove the inaccessible file. The RemoveFiles() function
            #   expects a list as an arg
            bad_file = []
            bad_file.append(self.tree.index(self.clicked_row))
            self.RemoveFiles(bad_file)
        else:
            # Update the treeview widget with the new metadata
            self.tree.set(self.clicked_row, res_str, value=_value)
        
        # Unbind the enter keys and destroy the window
        self.edit_window.unbind('<Return>')
        self.edit_window.unbind('<KP_Enter>')
        self.edit_window.destroy()
    
    
    def ValidateURL(self):
        """Validate the contents of the URL Entry widget.
        
        This function is called by the 'Click To Load URL Data' button. It
            tests that the data entered into the Entry widget is the URL for
            a specific Discogs release. It then isolates the release's ID.
        """
        
        # Prevent loading new data until the window gets reset
        if self.data_loaded:
            msg = 'Reset window before attempting to load new data.'
            tk.messagebox.showerror('Error', msg)
            return
        
        # Take no action if URL field is empty
        URL_str = self.URL.get().lstrip().rstrip()
        if not URL_str:
            return
        
        # Validate that the URL is from discogs.com
        release_URL = urlparse(URL_str)
        valid_URL = False
        if (release_URL.scheme == 'https' or release_URL.scheme == 'http'):
            
            if (release_URL.netloc == 'www.discogs.com'
                    or release_URL.netloc == 'discogs.com'):
                # URL is valid, retrieve the release path
                valid_URL = True
                release_path = release_URL.path
        
        elif (not release_URL.scheme and not release_URL.netloc):
            splice1 = release_URL.path[:11]
            splice2 = release_URL.path[:15]
            
            if splice1 == 'discogs.com':
                # URL is valid, retrieve the release path
                valid_URL = True
                release_path = release_URL.path[11:]
            
            elif splice2 == 'www.discogs.com':
                # URL is valid, retrieve the release path
                valid_URL = True
                release_path = release_URL.path[15:]
        
        if not valid_URL:
            tk.messagebox.showerror('Error',
                                    'Please enter a URL from www.discogs.com')
            return
        
        # Split the release path to isolate the release number
        path_split = release_path.split('/')
        
        # If the passed URL is valid but doesn't correspond to a specific
        #   release version page (e.g., a master release or a community list
        #   page), attempting to load data throws an error.
        if path_split[1] != 'release':
            msg = 'Unable to process the given URL.\n\n' \
                  'If attempting to load a master release, please use a\n' \
                  'specific release version instead.'
            tk.messagebox.showerror('Error', msg)
            return
        
        path_split = path_split[2].split('-')
        self.release_number = path_split[0]
        
        # If the URL is valid and the user has already provided their Discogs
        #   API user token, populate the entry widgets. Otherwise, call the
        #   function to get the user's token
        if self.token_flag:
            self.FillEntrys()
        else:
            self.GetUserToken()
    
    
if __name__ == '__main__':

    app = TagWindow()
    app.mainloop()
