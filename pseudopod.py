from struct import pack, unpack
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


    def intToHex(self, value):
        return pack('>B', value)

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
        checksum = (0x100 - (length + self.addCharacters(self.mode) + self.addCharacters(self.command) + payload)) & 0xFF
        return self.intToHex(checksum)

    def addCharacters(self, hex):
        return sum([ord(x) for x in hex])

    def get_text(self):
        text = self.header + self.intToHex(self.calc_length()) + self.mode + self.command
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

    request_mode_command =  IPodPacket(mode='\x00', command='\x03')

    def __init__(self, serial):
        self.serial = serial

    def execute_command(self, command, wait_for_response=False):
        self.serial.open()
        self.serial.write(command.get_text())
        response = None

        if wait_for_response:
            header = self.serial.read(2)
            if header == '\xFF\x55':
                length   = ord(self.serial.read(1))
                message  = self.serial.read(length)
                checksum = self.serial.read(1)
                print(translate(checksum))
                mode     = message[0]
                command  = message[1:3]
                print(translate(command))
                payload  = message[3:-1]
                print(translate(payload))
                response = IPodPacket(mode, command, header, length, payload, checksum)
                print(translate(response.calc_checksum()))
        if response != None and response.checksum != response.calc_checksum():
            response = None
        return response

    def request_mode(self):
        response = self.execute_command(self.request_mode_command, True)



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

    def execute_command(self, command, wait_for_response=False):
        super(SimpleRemote, self).execute_command(self.switch_mode_command)
        response = super(SimpleRemote, self).execute_command(command, wait_for_response)
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

    switch_mode_command                     = IPodPacket(mode = '\x00', command = '\x01\x04')
    get_ipod_name_command                   = IPodPacket(mode = mode, command   = '\x00\x14')
    switch_to_main_library_playlist_command = IPodPacket(mode = mode, command   = '\x00\x15')
    switch_to_item_number_command           = IPodPacket(mode = mode, command   = '\x00\x17')
    get_amount_for_type_command             = IPodPacket(mode = mode, command   = '\x00\x18')
    get_names_for_items_command             = IPodPacket(mode = mode, command   = '\x00\x1A')
    get_time_and_status_info_command        = IPodPacket(mode = mode, command   = '\x00\x1C')


    def execute_command(self, command, wait_for_response=False):
        super(AdvancedRemote, self).execute_command(self.switch_mode_command)
        response = super(AdvancedRemote, self).execute_command(command, wait_for_response)
        return response

    def get_name(self):
        response = self.execute_command(self.get_ipod_name_command, True)
        name = response.payload[:-1]
        return name

    def switch_to_main_library_playlist(self):
       self.execute_command(self.switch_to_main_library_playlist)

    def switch_to_item(self, item_type, number):
        command = self.switch_to_item_number_command
        command.set_payload(self.types[item_type] + self.intToHex(number))
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
        response = self.execute_command(command, True)
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
            response = super(AdvancedRemote, self).execute_command(command, True)
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
        response = self.execute_command(self.get_time_and_status_info_command, True)
        track_length = unpack('>i',response.payload[0:4])[0]
        elapsed_time = unpack('>i', response.payload[4:8])[0]
        status       = ord(response.payload[-1])

        return {
                'track_length': track_length,
                'elapsed_time': elapsed_time,
                'status'      : status
               }

ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1)


def translate(hexadec):
    return " ".join(hex(ord(n)) for n in hexadec)

remote = AdvancedRemote(ser)
#remote = SimpleRemote(ser)
print(remote.get_time_and_status_info())
