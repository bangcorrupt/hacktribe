# Encode/decode bytes to/from SysEx for Electribe 2

"""
The dump data conversion

   DATA ( 1set = 8bit x 7Byte )
   b7     ~      b0   b7     ~      b0   b7   ~~    b0   b7     ~      b0
   +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
   | | | | | | | | |  | | | | | | | | |  | | |    | | |  | | | | | | | | |
   +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
         7n+0               7n+1          7n+2 ~~ 7n+5         7n+6

    MIDI DATA ( 1set = 7bit x 8Byte )
      b7b7b7b7b7b7b7     b6    ~     b0     b6 ~~    b0     b6    ~     b0
   +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
   |0| | | | | | | |  |0| | | | | | | |  |0| |    | | |  |0| | | | | | | |
   +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
   7n+6,5,4,3,2,1,0         7n+0          7n+1 ~~ 7n+5         7n+6
"""

def syx_enc(byt):
    
    lng = len(byt)
    lst = []
    tmp = []
    b = 0
    cnt = 7
    lim = 0
    for i,e in enumerate(byt):

        if lng < 7:
            lim = 7 - lng

        a = e & ~0b10000000
        b |= ((e & 0b10000000)>>cnt)
        
        tmp.append(a)
        
        cnt -= 1
        if cnt == lim:
            lst.append([b])
            lst.append(tmp)
            tmp = []
            b = 0
            cnt = 7

            if (lng - i) < 7:
                lim = 7 - (lng - i) + 1

    syx = [item for sublist in lst for item in sublist]

    return syx


def syx_dec(syx):

    chk = [syx[i:i + 8] for i in range(0, len(syx), 8)]

    lst = []
    tmp = []
    a = 0
    
    for l in chk:
        for i in range(len(l)-1):
            a = l[i+1]
            a |= ((l[0] & (1<<i))>>i)<<7
            
            tmp.append(a)

        lst.append(tmp)
        tmp = []
    
    byt = [item for sublist in lst for item in sublist]
    
    return byt
