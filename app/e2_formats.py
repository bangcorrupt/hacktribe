from construct import *

# File format struct defs

# VSB file header format
# Default is SYSTEM.VSB for E2S v2.02
vsb_header = Struct('title' / Default(PaddedString(0x10, 'ascii'), 'KORG SYSTEM FILE'),
                    'dev_name' / Default(PaddedString(0x10, 'ascii'), 'E2S'),
                    'file_id' / Default(PaddedString(0x8, 'ascii'), 'SYSTEM'),
                    'rev' / Default(Int16ub, 1),
                    'maj_ver' / Default(Int8ub, 2),
                    'min_ver' / Default(Int8ub, 2),
                    Padding(1),
                    'dev_id' / Default(Hex(Int16ub), 0x124),
                    Padding(1, pattern=b'\xff'),
                    Padding(4),
                    'src_len' / Default(Hex(Int32ul), 0x200000),        # Test what this is actually used for
                    Padding(4),
                    'dest_len' / Default(Hex(Int32ul), 0x200000),       # Test what this is actually used for
                    'unk_int' / Default(Int16ul, 2),                    # Unknown integer
                    Padding(0xbe, pattern=b'\xff')
                   )


# System firmware binary
system = Struct('data' / Bytes(0x200000)
               )

# System firmware update VSB file
system_vsb = Struct('head' / vsb_header,
                    'body' / system
                   )


# Groove template
groove_template = Struct('start_label' / Default(PaddedString(0x10, 'ascii'), 'GVST'),
                         'name' / Default(PaddedString(0xf, 'ascii'), 'Init Groove'),
                         Padding(1),
                         Seek(0x22),
                         'length' / Default(Int8ul, 64),
                         Padding(1, pattern=b'\xff'),
                         'step' / Default(Struct(
                                        'trigger' / Default(Int8ul, 0),
                                        'velocity' / Default(Int8ul, 96),
                                        'gate' / Default(Int8ul, 96),
                                        'null' / Default(Hex(Int8ul), 0xff)
                                        )[64], [None] * 64),
                         Seek(0x13c),
                         'end_label' / Default(PaddedString(0x4, 'ascii'), 'GVED')
                        )
