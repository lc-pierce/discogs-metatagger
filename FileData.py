#-----------------------------------------------------------------------------#
#   File: FileData.py                                                         #
#   Author: Logan Pierceall                                                   #
#                                                                             #
#   This module accompanies 'Window.py'. It handles all of the code that      #
#       involves directly interacting with the file metadata information.     #
#       Consequently, this file depends on the 'mutagen' package found at     #
#       https://mutagen.readthedocs.io/en/latest/                             #
#-----------------------------------------------------------------------------#

import os

import mutagen
from mutagen import MutagenError
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


# ConvertColToTag() is called when updating a treeview volumn by
#   double-clicking the cell. This function converts the column ID selected by
#   the user into the corresponding metadata tag
# Args:     column = the column containing the cell that the user is editing
# Returns:  the metadata tag associated with the column ID
def ConvertColToTag(column):

    if column == '#1':
        return 'TrackNumber'
    elif column == '#3':
        return 'Title'
    elif column == '#4':
        return 'Artist'
    elif column == '#5':
        return 'AlbumArtist'
    elif column == '#6':
        return 'Album'
    elif column == '#7':
        return 'Date'
    elif column == '#8':
        return 'Genre'
    elif column == '#9':
        return 'Organization'


# ConvertTagToCol() is called when updating metadata tags. This function
#   converts the metadata tag to the corresponding column ID within the
#   treeview object
# Args:     tag = the metadata tag being updated
# Returns:  the treeview column ID associated with the metadata tag
def ConvertTagToCol(tag):

    if tag == 'TrackNumber':
        return '#1'
    elif tag == 'Title':
        return '#3'
    elif tag == 'Artist':
        return '#4'
    elif tag == 'AlbumArtist':
        return '#5'
    elif tag == 'Album':
        return '#6'
    elif tag == 'Date':
        return '#7'
    elif tag == 'Genre':
        return '#8'
    elif tag == 'Organization':
        return '#9'


# ParseFile() is called when music files are added to the program's window.
#   This function attempts to load a file's metadata using Mutagen, retrieves
#   the metadata information, and adds the file to the treeview widget
# Args:     filename = the file to load
#           tree = the treeview widget
#           index = the file's index within the added files list
# Returns:  True and 'None' if all operations were successful
#           False and a filename if the file failed to load via Mutagen
def ParseFile(filename, tree, index):
    
    # Attempt to load the song using Mutagen
    try:
        if ('.flac' in filename or '.FLAC' in filename):
            song = FLAC(filename)
        elif ('.mp3' in filename or '.MP3' in filename):
            song = MP3(filename, ID3=EasyID3)
        else:
            # Selected file is not a currently supported type
            return False, filename
    
    except MutagenError:
        # Send file back so it isn't added to the final files list
        return False, filename
    
    # 'song_iid' and '_tag' are both used by the treeview widget
    song_iid = 'song' + str(index)
    if index % 2 == 0:
        _tag = 'evenrow'
    else:
        _tag = 'oddrow'
    
    # Retrieve the file metadata
    short_name = os.path.basename(filename)
    
    try:
        track_no = song['TrackNumber'][0].split('/')[0]
    except KeyError:
        track_no = ''
    
    try:
        title = song['Title'][0]
    except KeyError:
        title = ''
    
    try:
        album = song['Album'][0]
    except KeyError:
        album = ''
    
    try:
        date = song['Date'][0]
    except KeyError:
        date = ''
    
    try:
        publisher = song['Organization'][0]
    except KeyError:
        publisher = ''
    
    # 'Artist', 'Album Artist', and 'Genre' may have more than one entry.
    #   Create a composite string for each with values separated by ';'
    a_string = ''
    try:
        if len(song['Artist']) > 1:
            for artist in song['Artist']:
                a_string += artist + '; '
            # Remove the final extra '; ' characters
            a_string = a_string.rstrip().rstrip(';')
        else:
            a_string = song['Artist'][0]
    except KeyError:
        pass
    
    aa_string = ''
    try:
        if len(song['AlbumArtist']) > 1:
            for artist in song['AlbumArtist']:
                aa_string += artist + '; '
            # Remove the final extra '; ' characters
            aa_string = aa_string.rstrip().rstrip(';')
        else:
            aa_string = song['AlbumArtist'][0]
    except KeyError:
        pass
    
    g_string = ''
    try:
        if len(song['Genre']) > 1:
            for genre in song['Genre']:
                g_string += genre + '; '
            # Remove the final extra '; ' characters
            g_string = g_string.rstrip().rstrip('; ')
        else:
            g_string = song['Genre'][0]
    except KeyError:
        pass
    
    # Insert the track data into the treeview object
    tree.insert('', 'end', iid=song_iid, tags=_tag,
                values=(track_no, short_name, title, a_string, aa_string,
                        album, date, g_string, publisher))
    
    return True, None


# UpdateMetadata() is called whenever the main program performs an operation
#   that alters the metadata of a file. This function updates the provided
#   metadata tag for the provided song and retrieves the treeview column
#   that needs to be update
# Args:     file = the file to update
#           tag = string containing the metadata tag to update
#           update_string = new value for the metadata tag
# Returns:  True and a column heading ID if successful
#           False and the filename otherwise
def UpdateMetadata(file, tag, update_string):
    
    try:
        if ('.flac' in file or '.FLAC' in file):
            song = FLAC(file)
        elif ('.mp3' in file or '.MP3' in file):
            song = MP3(file, ID3=EasyID3)
        else:
            return False, file
        
    except MutagenError:
        return False, file
        
    song[tag] = update_string
    song.save()
            
    # Find the column ID to return
    col_no = ConvertTagToCol(tag)
    return True, col_no


# UpdateTrackNumbers() is used to update the track number for loaded music
#   files
# Args:     file = filename of the file to update
#           iid = the file's treeview ID
#           track_no = the track number
# Returns:  True and 'None' if all operations were successful
#           False and the inaccesible filename otherwise
def UpdateTrackNumbers(file, iid, track_no):
    
    try:
        if ('.flac' in file or '.FLAC' in file):
            song = FLAC(file)
        elif ('.mp3' in file or '.MP3' in file):
            song = MP3(file, ID3=EasyID3)
        else:
            return False, file
    
    except MutagenError:
        return False, file
    
    song['TrackNumber'] = str(track_no)
    song.save()
    
    return True, None


# UpdateTrackTitle() is used to update the track title for loaded music files
# Args:     file = filename of the file to update
#           title = the track title string
#           iid = the file's treeview ID
#           index = counter that tracks the current file's track number
# Returns:  True and the song title if the update was successful
#           False and the inaccessible filename otherwise
def UpdateTrackTitle(file, title, iid, index):
    
    try:
        if ('.flac' in file or '.FLAC' in file):
            song = FLAC(file)
        elif ('.mp3' in file or '.MP3' in file):
            song = MP3(file, ID3=EasyID3)
        else:
            return False, file
    
    except MutagenError:
        return False, file
    
    # Remove the track number from the beginning of the title string
    if index < 10:
        title = title[3:]
    else:
        title = title[4:]
    song['Title'] = title
    song.save()
    
    return True, title