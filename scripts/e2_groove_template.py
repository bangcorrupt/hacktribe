from e2sysex import *

def main():
    
    # Instantiate SysEx communication
    e = E2Sysex()
    
    # Create blank groove template
    groove = E2Groove.new()
    
    # Set groove name
    groove.name = "Test groove 1"
    
    # Set groove loop length (re-triggers on pattern loop)
    groove.length = 13
    
    # Move 5th step forward half a step
    groove.edit_step(4, 'trigger', 48)
    
    # Move 13th step backward half a step
    groove.edit_step(12, 'trigger', -48)
    
    # Decrease 1st step velocity by 32
    groove.edit_step(0, 'velocity', -32)
    
    # Set 3rd step velocity to 127
    groove.step[2].velocity = 127
    
    # Set 11th step gate time to 96 (tie)
    groove.step[10].gate = 96
    
    # Send new groove template to 1st position in list
    groove_index = 0
    e.set_groove(groove_index, groove.data)
    

class E2Groove:

    # Returns E2Groove object with initialised parameter values
    def new():
        gv = bytearray(0x140)
        
        # Groove start
        gv[:4] = b'GVST'
        
        # Groove name
        gv[0x10:0x1f] = b'Init Groove'.ljust(0x0f, b'\x00')[:0x0f]
        
        # Groove length
        gv[0x22] = 0x40
        gv[0x23] = 0xff
        
        # Trigger, velocity, gate
        base = 0x30
        leng = 4
        for i in range(0,   0x100, 4):
            offset = base + int(i/4) * leng
            gv[offset] = 0x00
            gv[offset+1] = 0x60
            gv[offset+2] = 0x60
            gv[offset+3] = 0xff

        # Groove end
        gv[-4:] = b'GVED'
        
        return E2Groove(gv)


    # gv_data is bytearray
    def __init__(self, gv_data):
        self.data = gv_data

        self._name = str(self.data[0x10:0x20], 'ascii').strip('\x00')
        self._length = self.data[0x22]
        
        self.step = []
        for i in range(0x40):
            self.step.append(E2GrooveStep(self.data, i))

    
    # Groove name
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, strn):
        self.data[0x10:0x1f] = strn.encode('ascii').ljust(0x0f, b'\x00')[:0x0f]
        self._name = str(self.data[0x10:0x1f], 'ascii').strip('\x00')

    
    # Groove length
    @property
    def length(self):
        return self._length
    
    @length.setter
    def length(self, val):
        self.data[0x22] = val
        self._length = self.data[0x22]


    # Edit parameter value at step
    # param is target parameter, one of 'trigger', 'velocity', 'gate'
    # delta is integer change to existing value
    def edit_step(self, step_idx, param, delta):
        
        if param not in ['trigger', 'velocity', 'gate']:
            return
        
        if param == 'trigger':
            self.step[step_idx].trigger = self.step[step_idx].trigger + delta
        
        elif param == 'velocity':
            self.step[step_idx].velocity = self.step[step_idx].velocity + delta
            
        elif param == 'gate':
            self.step[step_idx].gate = self.step[step_idx].gate + delta
        
        else:
            return


class E2GrooveStep:
    def __init__(self, data, idx):
        self.data = data
        
        base = 0x30
        leng = 4
        self.offset = base + idx * leng
        
        self._trigger = self.data[self.offset]
        self._velocity = self.data[self.offset+1]
        self._gate = self.data[self.offset+2]
        self._null = self.data[self.offset+3]
    
    
    # Trigger time
    @property
    def trigger(self):
        return self._trigger
    
    @trigger.setter
    def trigger(self, val):
        
        # Clamp to valid range
        if val > 0x30:
            val = 0x30
        elif val < -0x30:
            val = -0x30
        
        # Two's complement
        if val < 0:
            val = 0x100 + val
        
        self.data[self.offset] = val
        self._val = self.data[self.offset]


    # Velocity
    @property
    def velocity(self):
        return self._velocity
    
    @velocity.setter
    def velocity(self, val):
        
        # Clamp to valid range
        if val > 0x7f:
            val = 0x7f
        elif val < 0:
            val = 0

        self.data[self.offset+1] = val
        self._val = self.data[self.offset+1]


    # Gate time
    @property
    def gate(self):
        return self._gate
    
    @gate.setter
    def gate(self, val):
        
        # Clamp to valid range
        if val > 0x60:
            val = 0x60
        elif val < 0:
            val = 0

        self.data[self.offset+2] = val
        self._val = self.data[self.offset+2]


    # null
    @property
    def null(self):
        return self._null
    
    @null.setter
    def null(self, val):

        self.data[self.offset+3] = val
        self._val = self.data[self.offset+3]


if __name__ == '__main__':
    main() 
