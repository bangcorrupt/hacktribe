import mido
from mido import Message
import logging
from subprocess import run

from e2pat2syx import pat_to_syx
from e2syx2pat import syx_to_pat

from e2_syx_codec import syx_enc
from e2_syx_codec import syx_dec

from time import sleep

def main():
    logging.basicConfig(level=logging.DEBUG)
   
    e = E2Sysex()


class E2Sysex:
    def __init__(self, midi=None):
        logging.debug('Initialise SysEx')
        self.midi = midi
        if self.midi is not None:

            self.inport = self.midi.inport
            self.outport = self.midi.outport

        else:
            self.inport = mido.open_input('electribe2 sampler electribe2 s')
            self.outport = mido.open_output('electribe2 sampler electribe2 s')

        self.global_channel, self.id, self.version = self.search_device()
   
        logging.info('Found electribe')
        logging.info('Global channel ' + str(self.global_channel))
        logging.info('Firmware version ' + self.version)
    
        self.sysex_head = [0x42, 0x30 + self.global_channel, 0x00, 0x01, self.id]
 
    def search_device(self):
        
        msg = Message('sysex', data=[0x42, 0x50, 0x00, 0x00])
            
        self.outport.send(msg)
        
        response = self.sysex_response()

        if response[:4] != [0xF0, 0x42, 0x50, 0x01]:
            logging.warning('Invalid response: Not search device reply message.')
            return -1
        
        global_channel = response[4]
        
        electribe_id = response[6]
        
        version = str(response[10]) + '.' + str(response[11])

        return global_channel, electribe_id, version 


    # get pattern from device
    # source is pattern number
    # returns pattern as sysex bytes
    def get_pattern(self, source):
        logging.debug('Called get_pattern')
        msg =  Message('sysex', data=self.sysex_head + 
                                     [0x1C] + 
                                     self.int_to_midi(source))

        self.outport.send(msg)
        response = self.sysex_response()
        
        if response[6] == 0x24:
            logging.warning('DATA LOAD ERROR: Pattern dump request unsuccessful')
            return -1
        
        elif response[6] == 0x4C:
            logging.info('PATTERN DATA DUMP: Pattern dump request successful')
            
            data = response [9:-1]


            return data

    
    # send pattern to device
    # pattern is pattern file as list of sysex bytes
    # dest is pattern number (0-249)
    # returns SysEx response code
    def set_pattern(self, dest, pattern):
        logging.debug('Called set_pattern')
        
        msg =  Message('sysex', data=self.sysex_head + 
                                     [0x4C] + 
                                     self.int_to_midi(dest) + 
                                     pattern)

        logging.debug('Sending pattern')
        self.outport.send(msg)        
        
        response = self.sysex_response()
        logging.debug('Sysex response: ' + str([hex(r) for r in response]))

        if response[6] == 0x24:
            logging.warning('DATA LOAD ERROR: Pattern dump unsuccessful')
            return 0x24
        
        elif response[6] == 0x23:
            logging.info('PATTERN DATA DUMP: Pattern dump successful')            
            return 0x23

        
    # get current pattern edit buffer from device
    # returns current pattern as sysex bytes SysEx error code
    def get_current_pattern(self):
        
        msg =  Message('sysex', data=self.sysex_head+[0x10])
        self.outport.send(msg)
        
        response = self.sysex_response()
        
        if response[6] == 0x24:
            logging.warning('DATA LOAD ERROR: Current pattern dump request unsuccessful')
            return 0x24
        
        elif response[6] == 0x40:
            logging.info('CURRENT PATTERN DATA DUMP: Current pattern dump request successful')
            
            data = response[7:-1]
            return bytes(data)
        
    
    # send pattern to device edit buffer
    # pattern is pattern file as sysex bytes
    # returns SysEx response code
    def set_current_pattern(self, pattern):
        
        
        msg =  Message('sysex', data=self.sysex_head + 
                                     [0x40] + 
                                     pattern)

        self.outport.send(msg)
        response = self.sysex_response()
        
        
        if response[6] == 0x24:
            logging.warning('DATA LOAD ERROR: Current Pattern dump unsuccessful')
            return 0x24
        
        elif response[6] == 0x23:
            logging.info('PATTERN DATA DUMP: Current pattern dump successful')            
            return 0x23


    # writes current edit buffer on device
    # returns SysEx Response code
    def write_pattern(self):
        logging.info('WRITE PATTERN: Not implemented yet')
        
    
    # helper function, uses get_pattern
    # get all patterns from device
    # returns list of pattern files as sysex bytes
    def get_all_patterns(self):
        return [self.get_pattern(i) for i in range(250)]
        

    # helper function, uses set_pattern    
    # sends all patterns to device
    # patterns is list of patterns as sysex bytes
    def set_all_patterns(self, patterns):
        logging.info('SET ALL PATTERNS: Not implemented yet')
    

    # get global settings
    # returns settings as sysex bytes
    def get_global(self):
        msg =  Message('sysex', data=self.sysex_head+[0x1e])
        self.outport.send(msg)

        response = self.sysex_response()

        if response[6] == 0x24:
            logging.warning('DATA LOAD ERROR: Global data dump request unsuccessful')
            return -1
        
        elif response[6] == 0x40:
            logging.info('CURRENT PATTERN DATA DUMP: Global data dump request successful')
            
            data = response[7:-1]
            return bytes(data)
    
 
    
    # sends global settings to device
    # settings is global settings as sysex bytes
    # checks response and returns 0 if successful
    def set_global(self, settings):
        logging.info('SET GLOBAL DATA: Not implemented yet')

  
    def sysex_response(self):
        for msg in self.inport:
            if msg.type == 'sysex':
                response = msg.bytes()
                break
        
        return response
    
    
    # convert integer x <= 255 to midi bytes
    # returns little endian list of 7-bit bytes
    def int_to_midi(self, x):
        return [ x%128, x//128 ]

        

    # val is list of sysex bytes
    def test_sysex_message(self, val):

        msg =  Message('sysex', data=self.sysex_head+val)
        self.outport.send(msg)
        response = self.sysex_response()

        return response


    
    # Read CPU RAM at address for length bytes
    # Returns data as bytearray
    def read_cpu_ram(self, address, length):
        
        # Encode values as sysex
        addr = address.to_bytes(4, byteorder='little')
        leng = length.to_bytes(4, byteorder='little')
        syx_al = syx_enc(addr+leng)
        
        # Send message
        msg =  Message('sysex', data=self.sysex_head+[0x52]+syx_al)
        self.outport.send(msg)
        response = self.sysex_response()
        
        # Decode sysex response
        byt_data = syx_dec(response[9:-1])
       
        return bytearray(byt_data)
        
    
    # Write data to CPU RAM at address
    # data is byte list
    def write_cpu_ram(self, address, data):
        logging.debug('Called write_cpu_ram')
        # First, set write address and length
        # Encode values as sysex
        addr = address.to_bytes(4, byteorder='little')
        leng = len(data).to_bytes(4, byteorder='little')
        syx_al = syx_enc(addr+leng)
        
        # Send first message
        msg =  Message('sysex', data=self.sysex_head+[0x53]+syx_al)
        logging.debug('Send addres+length')
        self.outport.send(msg)
        response = self.sysex_response()
        logging.debug('Sysex response: ' + str([hex(r) for r in response]))
        # Ignore response for now
        # UPDATE - test for success
        
        # Now send data to write
        # Encode data as sysex
        syx_dat = syx_enc(data)
        
        # Send final message
        msg =  Message('sysex', data=self.sysex_head+[0x54]+syx_dat)
        
        logging.debug('Sending data')
        self.outport.send(msg)
        
        response = self.sysex_response()
        logging.debug('Sysex response: ' + str([hex(r) for r in response]))
        
        return response
        

    # Get IFX preset from CPU RAM at index ifx_idx
    # Returns preset as bytearray
    # Uses get_cpu_ram for now
    # UPDATE - Add firmware hack for specific sysex function
    def get_ifx(self, ifx_idx):
        
        if ifx_idx > 99 or ifx_idx < 0:
            logging.warning('IFX index out of range - must be >= 0 & < 100.')
            return
        
        # Calculate IFX preset address
        ifx_base = 0xc00a80f0
        ifx_leng = 0x20c
        ifx_addr = ifx_base + ifx_leng * ifx_idx
        
        # Read IFX preset from CPU RAM
        ifx = self.read_cpu_ram(ifx_addr, ifx_leng)
        
        return ifx

    
    # Set IFX preset in CPU RAM at index ifx_idx
    # ifx is byte list
    # Uses write_cpu_ram for now
    # UPDATE - Add firmware hack for specific sysex function
    def set_ifx(self, ifx_idx, ifx):
        logging.debug('Called set_ifx')
        
        if ifx_idx > 99 or ifx_idx < 0:
            logging.warning('IFX index out of range - must be >= 0 & < 100.')
            return
        
        # Calculate IFX preset address
        ifx_base = 0xc00a80f0
        ifx_leng = 0x20c
        ifx_addr = ifx_base + ifx_leng * ifx_idx
        
        # Write IFX preset from CPU RAM
        # Writing in two halves fails less often
        ifx_a = ifx[:0x100]
        self.write_cpu_ram(ifx_addr, ifx_a)
        
        ifx_b = ifx[0x100:]
        self.write_cpu_ram(ifx_addr+0x100, ifx_b)
        
        return  
        
        
    # Add new IFX preset, increasing total count
    # ifx is byte list
    def add_ifx(self, ifx):
         
        # Get current max IFX index
        ifx_idx = self.read_cpu_ram(0xc003efdc, 1)[0]

        if ifx_idx > 99 or ifx_idx < 0:
            logging.warning('IFX index out of range - must be >= 0 & < 100.')
            return

        # Set IFX preset data
        self.set_ifx(ifx_idx, ifx)
        
        # Increase limits for menu and saved parameters
        # UPDATE - Add firmware hack to set these values in one location
        self.write_cpu_ram(0xc003efdc, [ifx_idx+1])
        self.write_cpu_ram(0xc0048f80, [ifx_idx])
        self.write_cpu_ram(0xc0049ef0, [ifx_idx])
        self.write_cpu_ram(0xc004a1f8, [ifx_idx])
        self.write_cpu_ram(0xc009814c, [ifx_idx])
        self.write_cpu_ram(0xc0098150, [ifx_idx+1])
        self.write_cpu_ram(0xc0098188, [ifx_idx])
        self.write_cpu_ram(0xc0098194, [ifx_idx+1])
        self.write_cpu_ram(0xc00980e8, [ifx_idx])
        self.write_cpu_ram(0xc00980ec, [ifx_idx+1])
        self.write_cpu_ram(0xc009809c, [ifx_idx+1])
        self.write_cpu_ram(0xc009811c, [ifx_idx+1])
        self.write_cpu_ram(0xc0098138, [ifx_idx+1])
 
        return

    
    # Get groove template from CPU RAM at index gv_idx
    # Returns preset as list of bytearray
    # Uses get_cpu_ram for now
    # UPDATE - Add firmware hack for specific sysex function
    def get_groove(self, gv_idx):
        
        if gv_idx > 127 or gv_idx < 0:
            logging.warning('Groove index out of range - must be >= 0 & < 128.')
            return
        
        # Calculate groove template address
        gv_base = 0xc0143b00
        gv_leng = 0x140
        gv_addr = gv_base + gv_leng * gv_idx
        
        # Read groove template from CPU RAM
        gv = self.read_cpu_ram(gv_addr, gv_leng)
        
        return gv

    
    # Set Groove template in CPU RAM at index gv_idx
    # gv is byte list
    # Uses write_cpu_ram for now
    # UPDATE - Add firmware hack for specific sysex function
    def set_groove(self, gv_idx, gv):
        
        if gv_idx > 127 or gv_idx < 0:
            logging.warning('Groove index out of range - must be >= 0 & < 128.')
            return
        
        # Calculate groove template address
        gv_base = 0xc0143b00
        gv_leng = 0x140
        gv_addr = gv_base + gv_leng * gv_idx
        
        # Write Groove template from CPU RAM
        self.write_cpu_ram(gv_addr, gv)

        return
        
    
    # Add new groove template, increasing total count
    # gv is byte list
    def add_groove(self, gv):

        # Get current max groove index
        gv_idx = self.read_cpu_ram(0xc007bb88, 1)[0]

        if gv_idx > 127 or gv_idx < 0:
            logging.warning('Groove index out of range - must be >= 0 & < 128.')
            return

        # Set groove template data
        self.set_groove(gv_idx, gv)

        # Increase limits for menu and saved parameters
        # UPDATE - Add firmware hack to set these values in one location
        self.write_cpu_ram(0xc0049da4, [gv_idx])
        self.write_cpu_ram(0xc007bb90, [gv_idx])
        self.write_cpu_ram(0xc007bb88, [gv_idx+1])
        self.write_cpu_ram(0xc007bb94, [gv_idx+1])

        return


if __name__ == '__main__':
    main()    
