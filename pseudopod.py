from struct import pack, unpack
from time import sleep
import serial

class IPodPacket(object):
    header   = '\xFF\x55'
    length   = 0
    mode     = '\x00'
    command  = ''
    payload  = None
    checksum = None

    def __init__(self, mode, command, header='\xFF\x55', length=0, payload=None, checksum=None):

        self.mode     = mode
        self.command  = command
        self.payload  = payload
        self.checksum = checksum
        self.header   = header
        self.length   = length

    def calc_length(self):
        length = 0
        if self.payload != None:
            length += len(self.payload)
        length += len(self.command) + len(self.mode)
        return length

    def calc_checksum(self):
        payload = 0x00
        if self.payload != None:
            payload  = self.addCharacters(self.payload)

        length = self.length
        if length == 0:
            length = self.calc_length()
        checksum = (0x100 - (length + self.addCharacters(self.mode) + self.addCharacters(self.command) + payload) & 0xFF)
        return pack('>B',checksum)

    def addCharacters(self, hex):
        return sum([ord(x) for x in hex])

    def get_text(self):
        length      = self.calc_length()
        length_text = ''

        if length < 255:
            length_text = pack('>B', length)
        else:
            length_text = '\x00' + pack('>H', length)
        text = self.header + length_text + self.mode + self.command

        if self.payload != None:
            text += self.payload
        text += self.calc_checksum()
        return text

    def set_payload(self, payload):
        self.payload = payload

    def __len__(self):
        return len(self.__str__())


class IPodRemote(object):
    serial = None

    request_mode_command =  IPodPacket(mode='\x00', command='\x00\x03')

    def __init__(self, serial):
        self.serial = serial

    def execute_command(self, command):
        self.serial.open()
        self.serial.write(command.get_text())
        response = None

        header = self.serial.read(2)
        if header == '\xFF\x55':
            length   = ord(self.serial.read(1))
            message  = self.serial.read(length)
            checksum = self.serial.read(1)
            mode     = message[0]
            command  = message[1:3]
            print translate(command)
            payload  = message[3:]
            print translate(payload)
            response = IPodPacket(mode, command, header, length, payload, checksum)
        if response != None and response.checksum != response.calc_checksum():
            response = None
        return response

    def request_mode(self):
        response = self.execute_command(self.request_mode_command)
        return response.payload



class SimpleRemote(IPodRemote):

    mode = '\x02'

    switch_mode_command       = IPodPacket(mode='\x00', command='\x01\x02')
    button_release_command    = IPodPacket(mode=mode, command='\x00\x00')
    play_pause_command        = IPodPacket(mode=mode, command='\x00\x01')
    vol_up_command            = IPodPacket(mode=mode, command='\x00\x02')
    vol_down_command          = IPodPacket(mode=mode, command='\x00\x04')
    skip_fwd_command          = IPodPacket(mode=mode, command='\x00\x08')
    skip_back_command         = IPodPacket(mode=mode, command='\x00\x10')
    next_album_command        = IPodPacket(mode=mode, command='\x00\x20')
    previous_album_command    = IPodPacket(mode=mode, command='\x00\x40')
    stop_command              = IPodPacket(mode=mode, command='\x00\x80')
    play_command              = IPodPacket(mode=mode, command='\x00\x00\x01')
    pause_command             = IPodPacket(mode=mode, command='\x00\x00\x02')
    mute_unmute_command       = IPodPacket(mode=mode, command='\x00\x00\x04')
    next_playlist_command     = IPodPacket(mode=mode, command='\x00\x00\x20')
    previous_playlist_command = IPodPacket(mode=mode, command='\x00\x00\x40')
    toggle_shuffle_command    = IPodPacket(mode=mode, command='\x00\x00\x80')
    toggle_repeat_command     = IPodPacket(mode=mode, command='\x00\x00\x00\x01')
    power_off_command         = IPodPacket(mode=mode, command='\x00\x00\x00\x04')
    power_on_command          = IPodPacket(mode=mode, command='\x00\x00\x00\x08')
    menu_command              = IPodPacket(mode=mode, command='\x00\x00\x00\x40')
    ok_command                = IPodPacket(mode=mode, command='\x00\x00\x00\x80')
    scroll_up_command         = IPodPacket(mode=mode, command='\x00\x00\x00\x00\x01')
    scroll_down_command       = IPodPacket(mode=mode, command='\x00\x00\x00\x00\x02')

    def execute_command(self, command):
        super(SimpleRemote, self).execute_command(self.switch_mode_command)
        response = super(SimpleRemote, self).execute_command(command)
        super(SimpleRemote, self).execute_command(self.button_release_command)
        return response

    def play_pause(self):
        self.execute_command(self.play_pause_command)

    def vol_up(self, points=1):
        for i in range(0, points):
            self.execute_command(self.vol_up_command)

    def vol_down(self, points=1):
        for i in range(0, points):
            self.execute_command(self.vol_down_command)

    def skip_forward(self, times=1):
        for i in range(0, times):
            self.execute_command(self.skip_fwd_command)

    def skip_back(self, times=1):
        for i in range(0, times):
            self.execute_command(self.skip_back_command)

    def next_album(self, times=1):
        for i in range(0, times):
            self.execute_command(self.next_album_command)

    def previous_album(self, times=1):
        for i in range(0, times):
            self.execute_command(self.previous_album_command)

    def stop(self):
        self.execute_command(self.stop_command)

    def play(self):
        self.execute_command(self.play_command)

    def pause(self):
        self.execute_command(self.pause_command)

    def mute_unmute(self):
        self.execute_command(self.mute_unmute_command)

    def next_playlist(self, times=1):
        for i in range(0, times):
            self.execute_command(self.next_playlist_command)

    def previous_playlist(self, times=1):
        for i in range(0, times):
            self.execute_command(self.previous_playlist_command)

    def toggle_shuffle(self):
        self.execute_command(self.toggle_shuffle_command)

    def toggle_repeat(self):
        self.execute_command(self.toggle_repeat_command)

    def power_off(self):
        self.execute_command(self.power_off_command)

    def power_on(self):
        self.execute_command(self.power_on_command)

    def menu(self):
        self.execute_command(self.menu_command)

    def ok(self):
        self.execute_command(self.ok_command)

    def scroll_down(self, times=1):
        for i in range(0, times):
            self.execute_command(self.scroll_down_command)

    def scroll_up(self, times=1):
        for i in range(0, times):
            self.execute_command(self.scroll_up_command)


class AdvancedRemote(IPodRemote):

    mode = '\x04'

    types = {
                'playlist' : '\x01',
                'artist'   : '\x02',
                'album'    : '\x03',
                'genre'    : '\x04',
                'song'     : '\x05',
                'composer' : '\x06'
            }

    playback = {
                'play_pause'   : '\x01',
                'stop'         : '\x02',
                'skip_forward' : '\x03',
                'skip_back'    : '\x04',
                'fast_forward' : '\x05',
                'fast_rewind'  : '\x06',
                'stop_ff_rw'   : '\x07'
            }

    shuffle = {
                'off'    : '\x00',
                'songs'  : '\x01',
                'albums' : '\x02'
            }

    repeat = {
                'off'       : '\x00',
                'one_song'  : '\x01',
                'all_songs' : '\x02'
            }

    switch_mode_command                             = IPodPacket(mode = '\x00', command = '\x01\x04')
    get_ipod_name_command                           = IPodPacket(mode = mode, command   = '\x00\x14')
    switch_to_main_library_playlist_command         = IPodPacket(mode = mode, command   = '\x00\x15')
    switch_to_item_number_command                   = IPodPacket(mode = mode, command   = '\x00\x17')
    get_amount_for_type_command                     = IPodPacket(mode = mode, command   = '\x00\x18')
    get_names_for_items_command                     = IPodPacket(mode = mode, command   = '\x00\x1A')
    get_time_and_status_info_command                = IPodPacket(mode = mode, command   = '\x00\x1C')
    get_current_position_command                    = IPodPacket(mode = mode, command   = '\x00\x1E')
    get_title_for_song_number_command               = IPodPacket(mode = mode, command   = '\x00\x20')
    get_artist_for_song_number_command              = IPodPacket(mode = mode, command   = '\x00\x22')
    get_album_for_song_number_command               = IPodPacket(mode = mode, command   = '\x00\x24')
    set_polling_mode_command                        = IPodPacket(mode = mode, command   = '\x00\x26')
    execute_playlist_switch_command                 = IPodPacket(mode = mode, command   = '\x00\x28')
    execute_playback_command_command                = IPodPacket(mode = mode, command   = '\x00\x29')
    get_shuffle_mode_command                        = IPodPacket(mode = mode, command   = '\x00\x2C')
    set_shuffle_mode_command                        = IPodPacket(mode = mode, command   = '\x00\x2E')
    get_repeat_mode_command                         = IPodPacket(mode = mode, command   = '\x00\x2F')
    set_repeat_mode_command                         = IPodPacket(mode = mode, command   = '\x00\x31')
    get_number_of_songs_in_current_playlist_command = IPodPacket(mode = mode, command   = '\x00\x35')
    jump_to_song_number_command                     = IPodPacket(mode = mode, command   = '\x00\x37')
    get_screen_size_command                         = IPodPacket(mode = mode, command   = '\x00\x33')
    send_pictute_command                            = IPodPacket(mode = mode, command   = '\x00\x32')

    def execute_command(self, command):
        # TODO: Switch mode only once
        super(AdvancedRemote, self).execute_command(self.switch_mode_command)
        response = super(AdvancedRemote, self).execute_command(command)
        return response

    def get_name(self):
        response = self.execute_command(self.get_ipod_name_command)
        name = response.payload[:-1]
        return name

    def switch_to_main_library_playlist(self):
       self.execute_command(self.switch_to_main_library_playlist)

    def switch_to_item(self, item_type, number):
        command = self.switch_to_item_number_command
        command.set_payload(self.types[item_type] + pack('>i', number))
        self.execute_command(command)

    def switch_to_playlist(self, number):
        self.switch_to_item('playlist', number)

    def switch_to_artist(self, number):
        self.switch_to_item('artist', number)

    def switch_to_album(self, number):
        self.switch_to_item('album', number)

    def switch_to_genre(self, number):
        self.switch_to_item('genre', number)

    def switch_to_song(self, number):
        self.switch_to_item('song', number)

    def switch_to_composer(self, number):
        self.switch_to_item('composer', number)

    def get_amount_for_type(self, item_type):
        command = self.get_amount_for_type_command
        command.set_payload(self.types[item_type])
        response = self.execute_command(command)
        return unpack('>i', response.payload)[0]

    def get_amount_of_playlists(self):
        return self.get_amount_for_type('playlist')

    def get_amount_of_artists(self):
        return self.get_amount_for_type('artist')

    def get_amount_of_albums(self):
        return self.get_amount_for_type('album')

    def get_amount_of_genres(self):
        return self.get_amount_for_type('genre')

    def get_amount_of_songs(self):
        return self.get_amount_for_type('song')

    def get_amount_of_composers(self):
        return self.get_amount_for_type('composer')

    def get_names_for_items(self, item_type, offset, number):
        super(AdvancedRemote, self).execute_command(self.switch_mode_command)
        command = self.get_names_for_items_command
        command.set_payload(self.types[item_type] + pack('>i', offset) + pack('>i',number))
        names = []
        for i in range(0,number):
            response = super(AdvancedRemote, self).execute_command(command)
            offset = unpack('>i', response.payload[0:4])[0]
            name = response.payload[4:]
            names.append((offset, name))
        return names

    def get_names_for_playlists(self, offset, number):
        return self.get_names_for_items('playlist', offset, number)

    def get_names_for_artists(self, offset, number):
        return self.get_names_for_items('artist', offset, number)

    def get_names_for_albums(self, offset, number):
        return self.get_names_for_items('album', offset, number)

    def get_names_for_genres(self, offset, number):
        return self.get_names_for_items('genre', offset, number)

    def get_names_for_songs(self, offset, number):
        return self.get_names_for_items('song', offset, number)

    def get_names_for_composers(self, offset, number):
        return self.get_names_for_items('composer', offset, number)

    def get_time_and_status_info(self):
        response = self.execute_command(self.get_time_and_status_info_command)
        track_length = unpack('>i',response.payload[0:4])[0]
        elapsed_time = unpack('>i', response.payload[4:8])[0]
        status       = ord(response.payload[-1])

        return {
                'track_length': track_length,
                'elapsed_time': elapsed_time,
                'status'      : status
               }
    def get_current_position_in_playlist(self):
        response = self.execute_command(self.get_current_position_command)
        current_position = unpack('>i', response.payload[0:4])[0]
        return current_position

    ''' The following four methods need the ipod to be playing a set of songs
        in order to work '''
    def get_information_for_song_number(self, number, command):
        command.set_payload(pack('>i', number))
        response = self.execute_command(command)
        return response.payload[:-1]

    def get_title_for_song_number(self,number):
        command = self.get_title_for_song_number_command
        return self.get_information_for_song_number(number,command)

    def get_artist_for_song_number(self,number):
        command = self.get_artist_for_song_number_command
        return self.get_information_for_song_number(number,command)

    def get_album_for_song_number(self, number):
        command = self.get_album_for_song_number_command
        return self.get_information_for_song_number(number,command)

    def set_polling_mode(self, polling_mode):
        command = self.set_polling_mode_command
        command.set_payload(polling_mode)
        return self.execute_command(command)

    # TODO: Make a thread that receives responses every 500ms
    def start_polling_mode(self):
        response = self.set_polling_mode('\x01')
        return unpack('>i', response.payload)

    # TODO: Check response
    def stop_polling_mode(self):
        response = self.set_polling_mode('\x00')

    ''' Executes the playlist switch made with one of the switch_to_items_command '''
    def execute_playlist_switch(self, song_number=-1):
        command = self.execute_playlist_switch_command
        command.set_payload(pack('>i', song_number))
        response = self.execute_command(command)

    def execute_playback_command(self, commandName):
        command = self.execute_playback_command_command
        command.set_payload(self.playback[commandName])
        self.execute_command(command)

    def play_pause(self):
        self.execute_playback_command('play_pause')

    def stop(self):
        self.execute_playback_command('stop')

    def skip_forward(self):
        self.execute_playback_command('skip_forward')

    def skip_back(self):
        self.execute_playback_command('skip_back')

    def fast_forward(self):
        self.execute_playback_command('fast_forward')

    def fast_rewind(self):
        self.execute_playback_command('fast_rewind')

    def stop_fast_forward_rewind(self):
        self.execute_playback_command('stop_ff_rw')

    def get_shuffle_mode(self):
        response = self.execute_command(self.get_shuffle_mode_command)
        return response.payload

    def set_shuffle_mode(self, shuffle_mode):
        command = self.set_shuffle_mode_command
        command.set_payload(self.shuffle[shuffle_mode])
        self.execute_command(command)

    def set_shuffle_off(self):
        self.set_shuffle_mode('off')

    def set_shuffle_songs(self):
        self.set_shuffle_mode('songs')

    def set_shuffle_albums(self):
        self.set_shuffle_mode('albums')

    def get_repeat_mode(self):
        response = self.execute_command(self.get_repeat_mode_command)
        return response.payload

    def set_repeat_mode(self, repeat_mode):
        command = self.set_repeat_mode_command
        command.set_payload(self.repeat[repeat_mode])
        self.execute_command(command)

    def set_repeat_off(self):
        self.set_repeat_mode('off')

    def set_repeat_one_song(self):
        self.set_repeat_mode('one_song')

    def set_repeat_all_songs(self):
        self.set_repeat_mode('all_songs')

    def get_number_of_songs_in_current_playlist(self):
        response = self.execute_command(get_number_of_songs_in_current_playlist_command)
        return unpack('>i', response.payload)[0]

    def jump_to_song_number(self, number):
        command = self.jump_to_song_number_command
        command.set_payload(number)
        self.execute_command(command)

    def get_screen_size(self):
        response = self.execute_command(self.get_screen_size_command)
        return {
                "width"  : unpack('>H', response.payload[:2])[0],
                "height" : unpack('>H', response.payload[2:4])[0],
                "extra"  : response.payload[-1]
            }

ser = serial.Serial(
    port='/dev/ttyAMA0',
#    port='/dev/ttyUSB0',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1)


def translate(hexadec):
    return " ".join(hex(ord(n)) for n in hexadec)

