from construct import *

# File format struct defs

# VSB ------------------------------------------------------------------

# VSB file header format
# Default is SYSTEM.VSB for E2 v2.02
vsb_header = Struct('title' / Default(PaddedString(0x10, 'ascii'), 'KORG SYSTEM FILE'),
                    'dev_name' / Default(PaddedString(0x10, 'ascii'), 'E2'),
                    'file_id' / Default(PaddedString(0x8, 'ascii'), 'SYSTEM'),
                    'rev' / Default(Int16ub, 1),
                    'maj_ver' / Default(Int8ub, 2),
                    'min_ver' / Default(Int8ub, 2), Padding(1),
                    'dev_id' / Default(Hex(Int16ub), 0x123), Padding(1, pattern=b'\xff'), Padding(4),
                    'src_len' / Default(Hex(Int32ul), 0x200000), Padding(4),        # Test what this is actually used for
                    'dest_len' / Default(Hex(Int32ul), 0x200000),                   # Test what this is actually used for
                    'unk_int' / Default(Int16ul, 2), Padding(0xbe, pattern=b'\xff') # Unknown integer                     
                   )

# Oscillators
# Paramters for oscillator
osc_presets = Struct('name' / Default(PaddedString(0x10, 'ascii'), 'OscillatorPreset'),
                    'cat' / Default(Int8ul, 0x00),
                    'unk_int_a' / Default(Int8ul, 0x00),
                    'prog_idx' / Default(Int16ul, 0x00),
                    'unk_int_b' / Default(Int8ul, 0x00),
                    'glide' / Default(Int8ul, 0x00),
                    'min_edit' / Default(Int8ul, 0x00),
                    'max_edit' / Default(Int8ul, 0x7f),
                    'param_1' / Default(Int8ul, 0x40),
                    'edit_1' / Default(Int8ul, 0x01), Padding(0x2),
                    'param_2' / Default(Int8ul, 0x40),
                    'edit_2' / Default(Int8ul, 0x00), Padding(0x2),
                   )
                    

# Oscillator parameters section in firmware
fw_osc = Struct('presets' / Default(osc_presets[409], [None] * 409))

# System firmware binary
system = Struct(Seek(0xbec48),
                'osc' / fw_osc,
               )

# System firmware update VSB file
sys_vsb = Struct('head' / vsb_header,
                 'body' / system
                )


# PCM Flash ------------------------------------------------------------

# PCM section in flash memory
# Defaults match factory e2 Synth
#   UPDATE - Set defaults to empty section


# Unknown
pcm_drmp = Struct('title' / Default(PaddedString(0x4, 'ascii'), 'DRMP'),
                  'unk_int_a' / Default(Int32ul, 0x34),
                  'unk_int_b' / Default(Int32ul, 0x01), Padding(0x14, pattern=b'\xff'),
                  'unk_str' / Default(PaddedString(0x8, 'ascii'), 'Impulse2'),
                  'unk_int_c' / Default(Int32ul, 0x00),
                  'unk_int_d' / Default(Int32ul, 0x1e),
                  'unk_int_e' / Default(Int8ul, 0xc4),
                  'unk_int_f' / Default(Int8ul, 0xc7), Padding(0xe, pattern=b'\xff'),
                  )

# Unknown
pcm_drum = Struct('title' / Default(PaddedString(0x4, 'ascii'), 'DRUM'), Padding(0x4, pattern=b'\xff'),
                  'unk_int_a' / Default(Int32ul, 0x10),
                  'unk_int_b' / Default(Int32ul, 0x54110), Padding(0x10, pattern=b'\xff'),
                  'unk_bytes' / Default(Bytes(0x18), 
                                        (b'\x20\x10\x00\x14\xf0\x1a\xdf\xfd'
                                         b'\xff\xdf\xfe\x00\x28\x1a\xc7\xe0'
                                         b'\x0c\xe3\xb9\x39\xcf\xe4\x80\x0a')),
                                         Padding(0x10, pattern=b'\xff'),
                 )


# Multi-sample program (name and base sample index)
mspr_prog = Struct('name' / Default(PaddedString(0x8, 'ascii'), 'Program '), # Always padded with spaces to 8 characters.  Mtches name in MSVS
                   'base_idx' / Default(Int32ul, 0x00),                    # Index of first sample in SMPR section
                   'unk_flag' / Default(Int8ul, 0x00), Padding(0x3, pattern=b'\x00'),
                  )

pcm_mspr = Struct('title' / Default(PaddedString(0x4, 'ascii'), 'MSPR'),
                  'length' / Default(Int32ul, 0x19d0),                               # Including header
                  'count' / Default(Int32ul, 0x19b), Padding(0x14, pattern=b'\xff'), # Minus 47 oscillators
                  'progs' / Default(mspr_prog[362], [None] * 362)                    # 362 multi-sample programs in facctory synth
                 )




# Multi-sample range and level (keymap)
msrl_map = Struct('max_key' / Default(Int8ul, 0x7f),     # Highest key in group
                  'unk_int_a' / Default(Int8sl, 0x00),   # Usually 0, sometimes small signed value.
                  'sample'  /   Default(Int16ul, 0x00),  # Index of mapped sample
                  'unk_int_b' / Default(Int8ul, 0x00),
                  'root_note' / Default(Int8ul, 0x3c),   # Sample root note
                  'level' / Default(Int16ul, 0xffff),    # Sample level
                  )

pcm_msrl = Struct('title' / Default(PaddedString(0x4, 'ascii'), 'MSRL'),
                  'length' / Default(Int32ul, 0x1070),
                  'count' / Default(Int32ul, 0x20a), Padding(0x14, pattern=b'\xff'),
                  'maps' / Default(msrl_map[522], [None] * 522),
                 )


# Multi-sample velocity set (velocity map)
msvs_map = Struct('name' / Default(PaddedString(0x8, 'ascii'), 'Sample  '),         # Always padded with spaces to 8 characters.  Mtches name in MSPR
                  'vel_limit' / Default(Int8ul[4], [0x7f, 0xff, 0xff, 0xff]),       # Upper limits of velocity groups.  0xff == no group
                                Padding(0x4, pattern=b'\xff'),
                  'sample' / Default(Int16ul[4], [0x00, 0xffff, 0xffff, 0xffff]),   # Index of sample for each group.  0xffff == no group
                  'level' / Default(Int16ul[4], [0x8000, 0xffff, 0xffff, 0xffff]),  # Playback level 0x00-0x8000.  0xffff == no group
                 )
                
pcm_msvs = Struct('title' / Default(PaddedString(0x4, 'ascii'), 'MSVS'),
                  'length' / Default(Int32ul, 0x2d60),
                  'count' / Default(Int32ul, 0x16a), Padding(0x4, pattern=b'\xff'),
                  'unk_int' / Default(Int32ul, 0x01),Padding(0xc, pattern=b'\xff'),
                  'maps' / Default(msvs_map[362], [None] * 362),
                 )
                
                  
# Sample Program
smpr_prog = Struct('offset' / Default(Int32ul, 0x00),       # From base address in DSP RAM
                   'loop_start' / Default(Int32ul, 0x00),
                   'length' / Default(Int32ul, 0x01),
                   'unk_int_a' / Default(Int8ul, 0x00),
                   'unk_int_b' / Default(Int8ul, 0x00),
                   'play_mode' / Default(Int8ul, 0x00),     # 0 == Gate, 1 == trigger
                   'unk_int_c' / Default(Int8ul, 0x00),
                 )

pcm_smpr = Struct('title' / Default(PaddedString(0x4, 'ascii'), 'SMPR'),
                  'length' / Default(Int32ul, 0x20c0),                  # Including header
                  'count' / Default(Int32ul, 0x20a), 
                  'unk_int' / Default(Int32ul, 0x41ed),
                              Padding(0x10, pattern=b'\xff'),
                  'progs' / Default(smpr_prog[522], [None] * 522)       # 362 multi-sample programs in facctory synth
                 )


# Compressed sample PCM data
pcm_smpl = Struct('title' / Default(PaddedString(0x4, 'ascii'), 'SMPL'),
                            Padding(0x4, pattern=b'\xff'),
                  'unk_int_a' / Default(Int32ul, 0x7ce14f),             # Address?
                  'unk_int_b' / Default(Int32ul, 0x85204090),           # Checksum?
                                Padding(0x10, pattern=b'\xff'),
                  'data' / Default(GreedyBytes, Byte[0])
                 )


# PCM Section header
# UPDATE - calculate offsets from section lengths
pcm_header = Struct('title' / Default(PaddedString(0xc, 'ascii'), 'KORGelec2PCM'),
                    'checksum' / Default(Int32ul, 0),                                           # Hacktribe ignores checksum
                    'offset_drmp' / Default(Int32ul, 0x40),                                     # Offset to DRMP section
                    'offset_drum' / Default(Int32ul, 0x80),                                     # Offset to DRUM section
                    'offset_mspr' / Default(Int32ul, 0xc0),                                     # Offset to MSPR section
                    'offset_msrl' / Default(Int32ul, 0x1780),                                   # Offset to MSRL section
                    'offset_smpr' / Default(Int32ul, 0x5505),                                   # Offset to SMPR section
                    'offset_smpl' / Default(Int32ul, 0x7610),                                   # Offset to SMPL section
                    'offset_msvs' / Default(Int32ul, 0x27f0), Padding(0x4, pattern=b'\xff'),    # Offset to MSVS section
                    'unk_int' / Default(Int32ul, 0x7ce15f),  Padding(0xc, pattern=b'\xff'),     # Unknown integer
                    )



pcm = Struct('pcm_header' / pcm_header, Seek(0x40),     # Section title and checksum
             'drmp' / pcm_drmp, Seek(0x80),             # Unknown
             'drum' / pcm_drum, Seek(0xc0),             # Unknown
             'mspr' / pcm_mspr, Seek(0x1780),           # Multi-sample program (name and base sample index)
             'msrl' / pcm_msrl, Seek(0x27f0),           # Multi-sample range and level (keygroups)
             'msvs' / pcm_msvs, Seek(0x5550),           # Multi-sample velocity set
             'smpr' / pcm_smpr, Seek(0x7610),           # Sample program (offset in DSP RAM, loop start, length)
             'smpl' / pcm_smpl,                         # Compressed sample pcm data
             )





# Groove ---------------------------------------------------------------

# Groove template
groove_step = Struct('trigger' / Default(Int8ul, 0),
                    'velocity' / Default(Int8ul, 96),
                    'gate' / Default(Int8ul, 96),
                    'null' / Default(Hex(Int8ul), 0xff)
                    )

groove_template = Struct('start_label' / Default(PaddedString(0x10, 'ascii'), 'GVST'),
                         'name' / Default(PaddedString(0xf, 'ascii'), 'Init Groove'), Padding(1), Seek(0x22),
                         'length' / Default(Int8ul, 64), Padding(1, pattern=b'\xff'),
                         'step' / Default(groove_step[64], [None] * 64), Seek(0x13c),
                         'end_label' / Default(PaddedString(0x4, 'ascii'), 'GVED')
                        )

# FX -------------------------------------------------------------------

# FX preset
fx_control = Struct('source_control' / Default(Enum(Int8ul, FX_On=0x41,
                                                            FX_Edit_X=0x42,
                                                            FX_Edit_Y=0x43,
                                                            FX_Edit_X_Hi=0x44,
                                                            FX_Edit_X_Lo=0x45,
                                                            FX_Edit_Y_Hi=0x46,
                                                            FX_Edit_Y_Lo=0x47,
                                                            Press_Play=0x4a),  0x42),
                    'chain_index' / Default(Enum(Int8ul, IFX_1=0x00,
                                                         IFX_2=0x01,
                                                         MFX=0x02,
                                                         Input_Level=0x07,
                                                         Output_Level=0x0a), 0x00),
                    'dest_param' / Default(Int8ul, 0x00), Padding(1),
                    'min_value' / Default(Int8ul, 0x00), Padding(1),
                    'max_value' / Default(Int8ul, 0x7f), Padding(21),
                    )

fx_control_map = Struct('fx_control' / Default(fx_control[10], [None] * 10))


nofx_thru_params = Struct()

I_mkp2_comp_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'envelope_select' / Default(Int8ul, 0x0), Padding(1),
                            'sensitivity' / Default(Int8ul, 0x64), Padding(1),
                            'attack' / Default(Int8ul, 0x0), Padding(1),
                            'output_level' / Default(Int8ul, 0x8), Padding(1),
                            'trim' / Default(Int8ul, 0x7f), Padding(1),
                            'pre_leq_gain' / Default(Int8ul, 0x24), Padding(1),
                            'pre_leq_frequency' / Default(Int8ul, 0xa), Padding(1),
                            'pre_heq_gain' / Default(Int8ul, 0x24), Padding(1),
                            'pre_heq_frequency' / Default(Int8ul, 0x27), Padding(1),
                            )
                            
I_sr1_comp_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'envelope_select' / Default(Int8ul, 0x0), Padding(1),
                            'threshold' / Default(Int8ul, 0x24), Padding(1),
                            'ratio' / Default(Int8ul, 0x8), Padding(1),
                            'knee' / Default(Int8ul, 0x5), Padding(1),
                            'attack' / Default(Int8ul, 0xc), Padding(1),
                            'release' / Default(Int8ul, 0x2), Padding(1),
                            'hold_time' / Default(Int8ul, 0x4), Padding(1),
                            'tube_sat' / Default(Int8ul, 0x3c), Padding(1),
                            'output_gain' / Default(Int8ul, 0x36), Padding(1),
                            )

I_cheap_comp_params = Struct('hpf_b1' / Default(Int8ul, 0x7f), Padding(1),
                                'peak_hold_b1' / Default(Int8ul, 0x7f), Padding(1),
                                'env_lpf_a0(c2)' / Default(Int8ul, 0x40), Padding(1),
                                'env_bit_shift_amount' / Default(Int8ul, 0x4), Padding(1),
                                'sens(c1)' / Default(Int8ul, 0x40), Padding(1),
                                'output_level' / Default(Int8ul, 0xc), Padding(1),
                                )

I_punch_params = Struct()

I_limiter_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'envelope_select' / Default(Int8ul, 0x0), Padding(1),
                            'threshold' / Default(Int8ul, 0x30), Padding(1),
                            'attack' / Default(Int8ul, 0xa), Padding(1),
                            'release' / Default(Int8ul, 0x3), Padding(1),
                            'hold_time' / Default(Int8ul, 0x3), Padding(1),
                            'tubesat' / Default(Int8ul, 0x64), Padding(1),
                            'output_gain' / Default(Int8ul, 0x40), Padding(1),
                            )

I_eq_2_band_params = Struct('trim' / Default(Int8ul, 0x7f), Padding(1),
                                'b1_type' / Default(Int8ul, 0x0), Padding(1),
                                'b2_type' / Default(Int8ul, 0x0), Padding(1),
                                'b1_frequency' / Default(Int8ul, 0xc), Padding(1),
                                'b1_q' / Default(Int8ul, 0x5), Padding(1),
                                'b1_gain' / Default(Int8ul, 0x24), Padding(1),
                                'b2_frequency' / Default(Int8ul, 0x38), Padding(1),
                                'b2_q' / Default(Int8ul, 0x5), Padding(1),
                                'b2_gain' / Default(Int8ul, 0x24), Padding(1),
                                )

I_eq_4_band_params = Struct('trim' / Default(Int8ul, 0x7f), Padding(1),
                            'b1_type' / Default(Int8ul, 0x2), Padding(1),
                            'b2_type' / Default(Int8ul, 0x0), Padding(1),
                            'b3_type' / Default(Int8ul, 0x0), Padding(1),
                            'b4_type' / Default(Int8ul, 0x1), Padding(1),
                            'b1_frequency' / Default(Int8ul, 0x10), Padding(1),
                            'b1_q' / Default(Int8ul, 0x5), Padding(1),
                            'b1_gain' / Default(Int8ul, 0x24), Padding(1),
                            'b2_frequency' / Default(Int8ul, 0x21), Padding(1),
                            'b2_q' / Default(Int8ul, 0x5), Padding(1),
                            'b2_gain' / Default(Int8ul, 0x24), Padding(1),
                            'b3_frequency' / Default(Int8ul, 0x30), Padding(1),
                            'b3_q' / Default(Int8ul, 0x5), Padding(1),
                            'b3_gain' / Default(Int8ul, 0x24), Padding(1),
                            'b4_frequency' / Default(Int8ul, 0x34), Padding(1),
                            'b4_q' / Default(Int8ul, 0x5), Padding(1),
                            'b4_gain' / Default(Int8ul, 0x24), Padding(1),
                            )

I_exciter_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'blend' / Default(Int8ul, 0x34), Padding(1),
                            'input_trim' / Default(Int8ul, 0x7f), Padding(1),
                            'pre_leq_gain' / Default(Int8ul, 0x24), Padding(1),
                            'pre_leq_frequency' / Default(Int8ul, 0x10), Padding(1),
                            'pre_heq_gain' / Default(Int8ul, 0x30), Padding(1),
                            'pre_heq_frequency' / Default(Int8ul, 0x2c), Padding(1),
                            'emphatic_point' / Default(Int8ul, 0x0), Padding(1),
                            'emphatic_lag' / Default(Int8ul, 0x0), Padding(1),
                            )

I_decimator_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'pre_lpf_sw' / Default(Int8ul, 0x0), Padding(1),
                            'pre_lpf' / Default(Int8ul, 0x7f), Padding(1),
                            'hi_damp' / Default(Int8ul, 0x74), Padding(1),
                            'sample_freq' / Default(Int8ul, 0x3f), Padding(1),
                            'bit_depth' / Default(Int8ul, 0x8), Padding(1),
                            'output_level' / Default(Int8ul, 0x7f), Padding(1),
                            'mask_type' / Default(Int8ul, 0x0), Padding(1),
                            )

I_filter_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'output_select' / Default(Int8ul, 0x0), Padding(1),
                            'frequency' / Default(Int8ul, 0x7f), Padding(1),
                            'resonance' / Default(Int8ul, 0x40), Padding(1),
                            )

I_distortion_params = Struct('dry_wet' / Default(Int8ul, 0x0), Padding(1),
                                'gain' / Default(Int8ul, 0x40), Padding(1),
                                'pre_eq_frequency' / Default(Int8ul, 0x23), Padding(1),
                                'pre_eq_q' / Default(Int8ul, 0xf), Padding(1),
                                'pre_eq_gain' / Default(Int8ul, 0x30), Padding(1),
                                'post_eq1_frequency' / Default(Int8ul, 0x10), Padding(1),
                                'post_eq1_q' / Default(Int8ul, 0x5), Padding(1),
                                'post_eq1_gain' / Default(Int8ul, 0x24), Padding(1),
                                'post_eq2_frequency' / Default(Int8ul, 0x2b), Padding(1),
                                'post_eq2_q' / Default(Int8ul, 0x5), Padding(1),
                                'post_eq2_gain' / Default(Int8ul, 0x2a), Padding(1),
                                'post_eq3_frequency' / Default(Int8ul, 0x35), Padding(1),
                                'post_eq3_q' / Default(Int8ul, 0x5), Padding(1),
                                'post_eq3_gain' / Default(Int8ul, 0x19), Padding(1),
                                'output_level' / Default(Int8ul, 0x19), Padding(1),
                                )
                                
I_acid_driver_params = Struct('drive' / Default(Int8ul, 0x1e), Padding(1),
                                'output_level' / Default(Int8ul, 0x28), Padding(1),
                                )

I_chorus_params = Struct('dry_wet' / Default(Int8ul, 0x32), Padding(1),
                            'mod_src' / Default(Int8ul, 0x0), Padding(1),
                            'mod_int' / Default(Int8ul, 0x40), Padding(1),
                            'lfo_wave' / Default(Int8ul, 0x1), Padding(1),
                            'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_speed' / Default(Int8ul, 0x1c), Padding(1),
                            'lfo_sync_note' / Default(Int8ul, 0x6), Padding(1),
                            'lfo_phase' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset_phase' / Default(Int8ul, 0x24), Padding(1),
                            'pre_leq_gain' / Default(Int8ul, 0x0), Padding(1),
                            'pre_leq_frequency' / Default(Int8ul, 0x0), Padding(1),
                            'pre_heq_gain' / Default(Int8ul, 0x0), Padding(1),
                            'pre_heq_frequency' / Default(Int8ul, 0x0), Padding(1),
                            'l_delay' / Default(Int8ul, 0x2e), Padding(1),
                            'r_delay' / Default(Int8ul, 0x0), Padding(1),
                            'lodamp' / Default(Int8ul, 0x0), Padding(1),
                            'hidamp' / Default(Int8ul, 0x0), Padding(1),
                            'spread' / Default(Int8ul, 0x0), Padding(1),
                            )

I_flanger_params = Struct('dry_wet' / Default(Int8ul, 0x4b), Padding(1),
                            'mod_src' / Default(Int8ul, 0x0), Padding(1),
                            'mod_int' / Default(Int8ul, 0x4b), Padding(1),
                            'lfo_wave' / Default(Int8ul, 0x1), Padding(1),
                            'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_speed' / Default(Int8ul, 0x6), Padding(1),
                            'lfo_sync_note' / Default(Int8ul, 0x1), Padding(1),
                            'lfo_shape' / Default(Int8ul, 0x32), Padding(1),
                            'lfo_phase' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset_phase' / Default(Int8ul, 0x12), Padding(1),
                            'manual' / Default(Int8ul, 0x0), Padding(1),
                            'delay' / Default(Int8ul, 0x2), Padding(1),
                            'lodamp' / Default(Int8ul, 0x0), Padding(1),
                            'hidamp' / Default(Int8ul, 0x0), Padding(1),
                            'feedback' / Default(Int8ul, 0x4b), Padding(1),
                            'fb_hicut' / Default(Int8ul, 0x0), Padding(1),
                            )

I_phaser_params = Struct('dry_wet' / Default(Int8ul, 0x32), Padding(1),
                            'type' / Default(Int8ul, 0x1), Padding(1),
                            'manual' / Default(Int8ul, 0x64), Padding(1),
                            'modint' / Default(Int8ul, 0x3c), Padding(1),
                            'resonance' / Default(Int8ul, 0x68), Padding(1),
                            'phase' / Default(Int8ul, 0x0), Padding(1),
                            'high_damp' / Default(Int8ul, 0x2), Padding(1),
                            'mod_wave' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_speed' / Default(Int8ul, 0x5), Padding(1),
                            'lfo_sync_note' / Default(Int8ul, 0x2), Padding(1),
                            'lfo_phase' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset_phase' / Default(Int8ul, 0x12), Padding(1),
                            )

I_tremolo_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'mod_src' / Default(Int8ul, 0x0), Padding(1),
                            'mod_int' / Default(Int8ul, 0x64), Padding(1),
                            'lfo_wave' / Default(Int8ul, 0x2), Padding(1),
                            'lfo_squ_dur' / Default(Int8ul, 0x32), Padding(1),
                            'lfo_squ_lag' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_speed' / Default(Int8ul, 0x50), Padding(1),
                            'lfo_sync_note' / Default(Int8ul, 0x6), Padding(1),
                            'lfo_shape' / Default(Int8ul, 0x32), Padding(1),
                            'do_nothing' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset_phase' / Default(Int8ul, 0x12), Padding(1),
                            )
                            
I_level_mod_params = Struct('amp_level' / Default(Int8ul, 0x7f), Padding(1),
                            'output_gain' / Default(Int8ul, 0x18), Padding(1),
                            'level_mod_source' / Default(Int8ul, 0x6), Padding(1),
                            'level_mod_int' / Default(Int8ul, 0x7e), Padding(1),
                            'level_mod_type' / Default(Int8ul, 0x0), Padding(1),
                            'saturation' / Default(Int8ul, 0x1), Padding(1),
                            'lfo_sync' / Default(Int8ul, 0x1), Padding(1),
                            'lfo_speed' / Default(Int8ul, 0x21), Padding(1),
                            'lfo_sync_note' / Default(Int8ul, 0x6), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset_phase' / Default(Int8ul, 0x12), Padding(1),
                            )

I_ring_mod_params = Struct('dry_wet' / Default(Int8ul, 0x32), Padding(1),
                            'osc_freq' / Default(Int8ul, 0x43), Padding(1),
                            'mod_int' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_speed' / Default(Int8ul, 0xe), Padding(1),
                            'lfo_syncnote' / Default(Int8ul, 0x2), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset_phase' / Default(Int8ul, 0x12), Padding(1),
                            'input_level' / Default(Int8ul, 0x7f), Padding(1),
                            'delay' / Default(Int8ul, 0x0), Padding(1),
                            'hi_damp' / Default(Int8ul, 0x7f), Padding(1),
                            'feedback' / Default(Int8ul, 0x32), Padding(1),
                            'delay_lag' / Default(Int8ul, 0x0), Padding(1),
                            )
                            
I_short_delay_params = Struct('dry_level' / Default(Int8ul, 0x78), Padding(1),
                                'wet_level' / Default(Int8ul, 0x1e), Padding(1),
                                'input_trim' / Default(Int8ul, 0x7f), Padding(1),
                                'tempo_sync' / Default(Int8ul, 0x0), Padding(1),
                                'off_time_ratio' / Default(Int8ul, 0x41), Padding(1),
                                'off_delay_time' / Default(Int8ul, 0x18), Padding(1),
                                'on_time_ratio' / Default(Int8ul, 0x23), Padding(1),
                                'on_syncnote' / Default(Int8ul, 0x11), Padding(1),
                                'fb_depth' / Default(Int8ul, 0x24), Padding(1),
                                'high_damp' / Default(Int8ul, 0x0), Padding(1),
                                'low_damp' / Default(Int8ul, 0x0), Padding(1),
                                'delay_lag' / Default(Int8ul, 0xf), Padding(1),
                                )


nofx_mute_params = Struct('fader' / Default(Int8ul, 0x0))

M_mkp2_comp_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'envelope_select' / Default(Int8ul, 0x0), Padding(1),
                            'sensitivity' / Default(Int8ul, 0x31), Padding(1),
                            'attack' / Default(Int8ul, 0x32), Padding(1),
                            'output_level' / Default(Int8ul, 0xc), Padding(1),
                            'trim' / Default(Int8ul, 0x7f), Padding(1),
                            'pre_leq_gain' / Default(Int8ul, 0x24), Padding(1),
                            'pre_leq_frequency' / Default(Int8ul, 0x10), Padding(1),
                            'pre_heq_gain' / Default(Int8ul, 0x24), Padding(1),
                            'pre_heq_frequency' / Default(Int8ul, 0x32), Padding(1),
                            )

M_sr1_comp_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'envelope_select' / Default(Int8ul, 0x0), Padding(1),
                            'threshold' / Default(Int8ul, 0x2a), Padding(1),
                            'ratio' / Default(Int8ul, 0x8), Padding(1),
                            'knee' / Default(Int8ul, 0x6), Padding(1),
                            'attack' / Default(Int8ul, 0xb), Padding(1),
                            'release' / Default(Int8ul, 0x5), Padding(1),
                            'hold_time' / Default(Int8ul, 0x0), Padding(1),
                            'tube_sat' / Default(Int8ul, 0x0), Padding(1),
                            'output_gain' / Default(Int8ul, 0x30), Padding(1),
                            )
                            
M_limiter_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                        'envelope_select' / Default(Int8ul, 0x0), Padding(1),
                        'threshold' / Default(Int8ul, 0x24), Padding(1),
                        'attack' / Default(Int8ul, 0x0), Padding(1),
                        'release' / Default(Int8ul, 0x8), Padding(1),
                        'hold_time' / Default(Int8ul, 0x8), Padding(1),
                        'tube_sat' / Default(Int8ul, 0x32), Padding(1),
                        'output_gain' / Default(Int8ul, 0x48), Padding(1),
                        )

M_eq_4_band_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'trim' / Default(Int8ul, 0x7f), Padding(1),
                            'b1_type' / Default(Int8ul, 0x2), Padding(1),
                            'b2_type' / Default(Int8ul, 0x0), Padding(1),
                            'b3_type' / Default(Int8ul, 0x0), Padding(1),
                            'b4_type' / Default(Int8ul, 0x1), Padding(1),
                            'b1_frequency' / Default(Int8ul, 0x10), Padding(1),
                            'b1_q' / Default(Int8ul, 0x5), Padding(1),
                            'b1_gain' / Default(Int8ul, 0x24), Padding(1),
                            'b2_frequency' / Default(Int8ul, 0x21), Padding(1),
                            'b2_q' / Default(Int8ul, 0x5), Padding(1),
                            'b2_gain' / Default(Int8ul, 0x24), Padding(1),
                            'b3_frequency' / Default(Int8ul, 0x30), Padding(1),
                            'b3_q' / Default(Int8ul, 0x5), Padding(1),
                            'b3_gain' / Default(Int8ul, 0x24), Padding(1),
                            'b4_frequency' / Default(Int8ul, 0x34), Padding(1),
                            'b4_q' / Default(Int8ul, 0x5), Padding(1),
                            'b4_gain' / Default(Int8ul, 0x24), Padding(1),
                            )
                            
M_wah_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                                'wah_type' / Default(Int8ul, 0x0), Padding(1),
                                'mod_src' / Default(Int8ul, 0x0), Padding(1),
                                'mod_int' / Default(Int8ul, 0x7f), Padding(1),
                                'control' / Default(Int8ul, 0x1), Padding(1),
                                'env_select' / Default(Int8ul, 0x1), Padding(1),
                                'env_response' / Default(Int8ul, 0x1), Padding(1),
                                'env_sens' / Default(Int8ul, 0x7f), Padding(1),
                                'lfo_step' / Default(Int8ul, 0x0), Padding(1),
                                'lfo_wave' / Default(Int8ul, 0x0), Padding(1),
                                'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                                'lfo_speed' / Default(Int8ul, 0x2f), Padding(1),
                                'lfo_syncnote' / Default(Int8ul, 0x6), Padding(1),
                                'lfo_rch_degree' / Default(Int8ul, 0x13), Padding(1),
                                'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                                'lfo_resetphase' / Default(Int8ul, 0x0), Padding(1),
                                'manual' / Default(Int8ul, 0x38), Padding(1),
                                )
                                
M_multimodefilter_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                'trim' / Default(Int8ul, 0x7f), Padding(1),
                'frequency' / Default(Int8ul, 0x5), Padding(1),
                'resonance' / Default(Int8ul, 0x4b), Padding(1),
                'mod_source' / Default(Int8ul, 0x1), Padding(1),
                'mod_lag' / Default(Int8ul, 0x40), Padding(1),
                'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                'lfo_speed' / Default(Int8ul, 0x19), Padding(1),
                'lfo_syncnote' / Default(Int8ul, 0x6), Padding(1),
                'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                'lfo_resetphase' / Default(Int8ul, 0x24), Padding(1),
                'freq_mod_int' / Default(Int8ul, 0x3f), Padding(1),
                'drive' / Default(Int8ul, 0x28), Padding(1),
                'drive_mod_int' / Default(Int8ul, 0x3f), Padding(1),
                'drive_tone' / Default(Int8ul, 0x7f), Padding(1),
                'hpf_level' / Default(Int8ul, 0x0), Padding(1),
                'bpf_level' / Default(Int8ul, 0x0), Padding(1),
                'lpf_level' / Default(Int8ul, 0x0), Padding(1),
                'lpf24_level' / Default(Int8ul, 0x7f), Padding(1),
                )


M_distortion_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                    'gain' / Default(Int8ul, 0x46), Padding(1),
                    'pre_eq_frequency' / Default(Int8ul, 0x23), Padding(1),
                    'pre_eq_q' / Default(Int8ul, 0x5), Padding(1),
                    'pre_eq_gain' / Default(Int8ul, 0x24), Padding(1),
                    'post_eq1_frequency' / Default(Int8ul, 0xe), Padding(1),
                    'post_eq1_q' / Default(Int8ul, 0x5), Padding(1),
                    'post_eq1_gain' / Default(Int8ul, 0x24), Padding(1),
                    'post_eq2_frequency' / Default(Int8ul, 0x2c), Padding(1),
                    'post_eq2_q' / Default(Int8ul, 0x5), Padding(1),
                    'post_eq2_gain' / Default(Int8ul, 0x24), Padding(1),
                    'post_eq3_frequency' / Default(Int8ul, 0x34), Padding(1),
                    'post_eq3_q' / Default(Int8ul, 0x5), Padding(1),
                    'post_eq3_gain' / Default(Int8ul, 0x24), Padding(1),
                    'output_level' / Default(Int8ul, 0x2d), Padding(1),
                    )


M_tubepre_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                        'tube1_gain' / Default(Int8ul, 0x30), Padding(1),
                        'tube1_sat' / Default(Int8ul, 0x4c), Padding(1),
                        'tube2_gain' / Default(Int8ul, 0x30), Padding(1),
                        'tube2_sat' / Default(Int8ul, 0x6c), Padding(1),
                        'lo_cut1' / Default(Int8ul, 0x4), Padding(1),
                        'hi_cut1' / Default(Int8ul, 0x7a), Padding(1),
                        'lo_cut2' / Default(Int8ul, 0x4), Padding(1),
                        'hi_cut2' / Default(Int8ul, 0x7e), Padding(1),
                        'tube1_bias' / Default(Int8ul, 0x1e), Padding(1),
                        'tube1_phase' / Default(Int8ul, 0x0), Padding(1),
                        'tube2_bias' / Default(Int8ul, 0x28), Padding(1),
                        'output_level' / Default(Int8ul, 0x34), Padding(1),
                        )
                        
                        
M_chorus_params = Struct('dry_wet' / Default(Int8ul, 0x32), Padding(1),
                        'mod_src' / Default(Int8ul, 0x0), Padding(1),
                        'mod_int' / Default(Int8ul, 0x32), Padding(1),
                        'lfo_wave' / Default(Int8ul, 0x1), Padding(1),
                        'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_speed' / Default(Int8ul, 0x23), Padding(1),
                        'lfo_sync_note' / Default(Int8ul, 0x5), Padding(1),
                        'lfo_phase' / Default(Int8ul, 0x24), Padding(1),
                        'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_reset_phase' / Default(Int8ul, 0x24), Padding(1),
                        'pre_leq_gain' / Default(Int8ul, 0x24), Padding(1),
                        'pre_leq_frequency' / Default(Int8ul, 0x10), Padding(1),
                        'pre_heq_gain' / Default(Int8ul, 0x24), Padding(1),
                        'pre_heq_frequency' / Default(Int8ul, 0x32), Padding(1),
                        'l_delay' / Default(Int8ul, 0x2e), Padding(1),
                        'r_delay' / Default(Int8ul, 0x40), Padding(1),
                        'lo_damp' / Default(Int8ul, 0x1a), Padding(1),
                        'hi_damp' / Default(Int8ul, 0x7f), Padding(1),
                        'spread' / Default(Int8ul, 0x7f), Padding(1),
                        )
                        

M_flanger_params = Struct('dry_wet' / Default(Int8ul, 0x4b), Padding(1),
                        'mod_src' / Default(Int8ul, 0x0), Padding(1),
                        'mod_int' / Default(Int8ul, 0x55), Padding(1),
                        'lfo_wave' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_speed' / Default(Int8ul, 0xe), Padding(1),
                        'lfo_syncnote' / Default(Int8ul, 0x3), Padding(1),
                        'lfo_shape' / Default(Int8ul, 0x59), Padding(1),
                        'lfo_phase' / Default(Int8ul, 0x1b), Padding(1),
                        'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_resetphase' / Default(Int8ul, 0x1b), Padding(1),
                        'manual' / Default(Int8ul, 0x0), Padding(1),
                        'delay' / Default(Int8ul, 0xb), Padding(1),
                        'lo_damp' / Default(Int8ul, 0xa), Padding(1),
                        'hi_damp' / Default(Int8ul, 0x7f), Padding(1),
                        'feedback' / Default(Int8ul, 0x4b), Padding(1),
                        'fb_hicut' / Default(Int8ul, 0x7f), Padding(1),
                        )

M_phaser_params = Struct('dry_wet' / Default(Int8ul, 0x32), Padding(1),
                        'type' / Default(Int8ul, 0x1), Padding(1),
                        'manual' / Default(Int8ul, 0x5a), Padding(1),
                        'mod_int' / Default(Int8ul, 0x3f), Padding(1),
                        'resonance' / Default(Int8ul, 0x55), Padding(1),
                        'phase' / Default(Int8ul, 0x0), Padding(1),
                        'high_damp' / Default(Int8ul, 0x0), Padding(1),
                        'mod_wave' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_speed' / Default(Int8ul, 0x13), Padding(1),
                        'lfo_syncnote' / Default(Int8ul, 0x3), Padding(1),
                        'lfo_phase' / Default(Int8ul, 0x1b), Padding(1),
                        'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_resetphase' / Default(Int8ul, 0x9), Padding(1),
                        )
                        

M_tremolo_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                        'mod_src' / Default(Int8ul, 0x0), Padding(1),
                        'mod_int' / Default(Int8ul, 0x50), Padding(1),
                        'lfo_wave' / Default(Int8ul, 0x2), Padding(1),
                        'lfo_squdur' / Default(Int8ul, 0x32), Padding(1),
                        'lfo_squlag' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_sync' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_speed' / Default(Int8ul, 0x42), Padding(1),
                        'lfo_sync_note' / Default(Int8ul, 0x1), Padding(1),
                        'lfo_shape' / Default(Int8ul, 0x19), Padding(1),
                        'lfo_phase' / Default(Int8ul, 0x24), Padding(1),
                        'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                        'lfo_reset_phase' / Default(Int8ul, 0x12), Padding(1),
                        )

M_level_mod_params = Struct('amp_level' / Default(Int8ul, 0x7f), Padding(1),
                            'output_gain_adjust' / Default(Int8ul, 0x18), Padding(1),
                            'level_mod_source' / Default(Int8ul, 0x2), Padding(1),
                            'level_mod_int' / Default(Int8ul, 0x7e), Padding(1),
                            'level_mod_type' / Default(Int8ul, 0x0), Padding(1),
                            'saturation' / Default(Int8ul, 0x1), Padding(1),
                            'lfo_sync' / Default(Int8ul, 0x1), Padding(1),
                            'lfo_speed' / Default(Int8ul, 0x21), Padding(1),
                            'lfo_sync_note' / Default(Int8ul, 0x6), Padding(1),
                            'lfo_phase' / Default(Int8ul, 0x1b), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'lfo_reset_phase' / Default(Int8ul, 0x24), Padding(1),
                            )
                            
M_hall_reverb_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                                'time' / Default(Int8ul, 0x26), Padding(1),
                                'hi_damp' / Default(Int8ul, 0x5c), Padding(1),
                                'pre_delay' / Default(Int8ul, 0x26), Padding(1),
                                'trim' / Default(Int8ul, 0x30), Padding(1),
                                'trim2' / Default(Int8ul, 0x7f), Padding(1),
                                'lo_eq' / Default(Int8ul, 0x1e), Padding(1),
                                'hi_eq' / Default(Int8ul, 0x1e), Padding(1),
                                'pd_thru' / Default(Int8ul, 0x1a), Padding(1),
                                )
                                
M_smooth_hall_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'time' / Default(Int8ul, 0x26), Padding(1),
                            'hi_damp' / Default(Int8ul, 0x4e), Padding(1),
                            'pre_delay' / Default(Int8ul, 0x26), Padding(1),
                            'trim' / Default(Int8ul, 0x35), Padding(1),
                            'trim2' / Default(Int8ul, 0x7f), Padding(1),
                            'lo_eq' / Default(Int8ul, 0x1e), Padding(1),
                            'hi_eq' / Default(Int8ul, 0x1e), Padding(1),
                            'pd_thru' / Default(Int8ul, 0x1a), Padding(1),
                            )
                            
M_wet_plate_reverb_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                                    'time' / Default(Int8ul, 0x1f), Padding(1),
                                    'hi_damp' / Default(Int8ul, 0x6a), Padding(1),
                                    'pre_delay' / Default(Int8ul, 0x26), Padding(1),
                                    'trim' / Default(Int8ul, 0x2b), Padding(1),
                                    'trim2' / Default(Int8ul, 0x5f), Padding(1),
                                    'lo_eq' / Default(Int8ul, 0x1e), Padding(1),
                                    'hi_eq' / Default(Int8ul, 0x1e), Padding(1),
                                    'pd_thru' / Default(Int8ul, 0x1a), Padding(1),
                                    )

M_dry_plate_reverb_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                                    'time' / Default(Int8ul, 0x1f), Padding(1),
                                    'hi_damp' / Default(Int8ul, 0x3d), Padding(1),
                                    'pre_delay' / Default(Int8ul, 0x33), Padding(1),
                                    'trim' / Default(Int8ul, 0x27), Padding(1),
                                    'trim2' / Default(Int8ul, 0x40), Padding(1),
                                    'lo_eq' / Default(Int8ul, 0x1e), Padding(1),
                                    'hi_eq' / Default(Int8ul, 0x1e), Padding(1),
                                    'pd_thru' / Default(Int8ul, 0x1a), Padding(1),
                                    )
                                    
M_room_reverb_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                                'time' / Default(Int8ul, 0x1f), Padding(1),
                                'hi_damp' / Default(Int8ul, 0x44), Padding(1),
                                'pre_delay' / Default(Int8ul, 0x7), Padding(1),
                                'trim' / Default(Int8ul, 0x2e), Padding(1),
                                'trim2' / Default(Int8ul, 0x7f), Padding(1),
                                'lo_eq' / Default(Int8ul, 0x1e), Padding(1),
                                'hi_eq' / Default(Int8ul, 0x1e), Padding(1),
                                'pd_thru' / Default(Int8ul, 0x0), Padding(1),
                                'rev_level' / Default(Int8ul, 0x66), Padding(1),
                                'er_level' / Default(Int8ul, 0x40), Padding(1),
                                )

M_mod_delay_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                    'wet_spread' / Default(Int8ul, 0x7f), Padding(1),
                    'input_trim' / Default(Int8ul, 0x32), Padding(1),
                    'pre_leq_gain' / Default(Int8ul, 0x24), Padding(1),
                    'pre_leq_frequency' / Default(Int8ul, 0x14), Padding(1),
                    'pre_heq_gain' / Default(Int8ul, 0x24), Padding(1),
                    'pre_heq_frequency' / Default(Int8ul, 0x2c), Padding(1),
                    'delay_time_tempo_sync' / Default(Int8ul, 0x1), Padding(1),
                    'off_time_ratio' / Default(Int8ul, 0x41), Padding(1),
                    'off_l_delay_time' / Default(Int8ul, 0x2f), Padding(1),
                    'off_r_delay_time' / Default(Int8ul, 0x29), Padding(1),
                    'on_time_ratio' / Default(Int8ul, 0x23), Padding(1),
                    'on_l_syncnote' / Default(Int8ul, 0x11), Padding(1),
                    'on_r_syncnote' / Default(Int8ul, 0x2b), Padding(1),
                    'fb_type' / Default(Int8ul, 0x0), Padding(1),
                    'fb_depth' / Default(Int8ul, 0x46), Padding(1),
                    'high_damp' / Default(Int8ul, 0x0), Padding(1),
                    'low_damp' / Default(Int8ul, 0x0), Padding(1),
                    'mod_depth' / Default(Int8ul, 0x23), Padding(1),
                    'mod_wave' / Default(Int8ul, 0x1), Padding(1),
                    'mod_freq' / Default(Int8ul, 0x1a), Padding(1),
                    'mod_rch_degree' / Default(Int8ul, 0x9), Padding(1),
                    'delay_lag' / Default(Int8ul, 0x0), Padding(1),
                    )

M_tape_echo_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                    'time_ratio' / Default(Int8ul, 0x19), Padding(1),
                    'sync_on' / Default(Int8ul, 0x1), Padding(1),
                    's_note1' / Default(Int8ul, 0x8), Padding(1),
                    's_note2' / Default(Int8ul, 0x8), Padding(1),
                    'time1' / Default(Int8ul, 0x13), Padding(1),
                    'time2' / Default(Int8ul, 0x13), Padding(1),
                    'delay_lag' / Default(Int8ul, 0x1), Padding(1),
                    'output_level' / Default(Int8ul, 0x35), Padding(1),
                    'tap1_level' / Default(Int8ul, 0x58), Padding(1),
                    'tap2_level' / Default(Int8ul, 0x58), Padding(1),
                    'feedback' / Default(Int8ul, 0x46), Padding(1),
                    'hi_damp' / Default(Int8ul, 0x4d), Padding(1),
                    'lo_damp' / Default(Int8ul, 0x30), Padding(1),
                    'trim' / Default(Int8ul, 0x50), Padding(1),
                    'saturation' / Default(Int8ul, 0x35), Padding(1),
                    'gain' / Default(Int8ul, 0x37), Padding(1),
                    'gainshift' / Default(Int8ul, 0x5), Padding(1),
                    'lfo_wave' / Default(Int8ul, 0x2), Padding(1),
                    'lfo_depth' / Default(Int8ul, 0x0), Padding(1),
                    'lfo_speed' / Default(Int8ul, 0x7f), Padding(1),
                    'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                    'pre_lpf' / Default(Int8ul, 0x6d), Padding(1),
                    'spread' / Default(Int8ul, 0x64), Padding(1),
                    )

M_grain_shifter_params = Struct('dry_wet' / Default(Int8ul, 0x32), Padding(1),
                                'duration_bpm_sync' / Default(Int8ul, 0x0), Padding(1),
                                'off_time_ratio' / Default(Int8ul, 0x2d), Padding(1),
                                'off_duration' / Default(Int8ul, 0x2a), Padding(1),
                                'on_time_ratio' / Default(Int8ul, 0x3), Padding(1),
                                'on_duration' / Default(Int8ul, 0x6), Padding(1),
                                'lfo_bpm_sync' / Default(Int8ul, 0x0), Padding(1),
                                'off_lfo_freq' / Default(Int8ul, 0x4e), Padding(1),
                                'on_sync_note' / Default(Int8ul, 0x7), Padding(1),
                                'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                                'duration_lag' / Default(Int8ul, 0x0), Padding(1),
                                )

M_decimator_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'pre_lpf_sw' / Default(Int8ul, 0x0), Padding(1),
                            'pre_lpf' / Default(Int8ul, 0x7f), Padding(1),
                            'hi_damp' / Default(Int8ul, 0x7f), Padding(1),
                            'sample_freq' / Default(Int8ul, 0x2d), Padding(1),
                            'bit_depth' / Default(Int8ul, 0x8), Padding(1),
                            'output_level' / Default(Int8ul, 0x7f), Padding(1),
                            'mask_type' / Default(Int8ul, 0x0), Padding(1),
                            'mod_src' / Default(Int8ul, 0x0), Padding(1),
                            'mod_int' / Default(Int8ul, 0x0), Padding(1),
                            'wave' / Default(Int8ul, 0x1), Padding(1),
                            'squ_dur' / Default(Int8ul, 0x32), Padding(1),
                            'lfo_reset' / Default(Int8ul, 0x0), Padding(1),
                            'reset_phase' / Default(Int8ul, 0x12), Padding(1),
                            'sync_on' / Default(Int8ul, 0x0), Padding(1),
                            'off_freq' / Default(Int8ul, 0x22), Padding(1),
                            'on_sync_note' / Default(Int8ul, 0x4), Padding(1),
                            )
                            
M_kpq_looper_params = Struct('loopswitch' / Default(Int8ul, 0x0), Padding(1),
                            'loop_length' / Default(Int8ul, 0x32), Padding(1),
                            'loop_type' / Default(Int8ul, 0x0), Padding(1),
                            'loop_trigger' / Default(Int8ul, 0x0), Padding(1),
                            'reset' / Default(Int8ul, 0x0), Padding(1),
                            'step' / Default(Int8ul, 0xd), Padding(1),
                            'fine' / Default(Int8ul, 0x40), Padding(1),
                            'pitch_lag' / Default(Int8ul, 0x65), Padding(1),
                            )


M_vinyl_break_params = Struct('dry_wet' / Default(Int8ul, 0x64), Padding(1),
                            'pad_on' / Default(Int8ul, 0x0), Padding(1),
                            'delta_pitch' / Default(Int8ul, 0x50), Padding(1),
                            'scratch' / Default(Int8ul, 0x0), Padding(1),
                            'scratch_width' / Default(Int8ul, 0x32), Padding(1),
                            'scratch_lag' / Default(Int8ul, 0x2), Padding(1),
                            'asobi' / Default(Int8ul, 0x10), Padding(1),
                            )



ifx_device = Default(Enum(Int8ul, nofx_thru=0x0,
                            I_mkp2_comp=0x1,
                            I_sr1_comp=0x2,
                            I_cheap_comp=0x3,
                            I_punch=0x4,
                            I_limiter=0x5,
                            I_eq_2_band=0x6,
                            I_eq_4_band=0x7,
                            I_exciter=0x8,
                            I_decimator=0x9,
                            I_filter=0xa,
                            I_distortion=0xf,
                            I_acid_driver=0x10,
                            I_chorus=0x11,
                            I_flanger=0x12,
                            I_phaser=0x13,
                            I_tremolo=0x14,
                            I_level_mod=0x15,
                            I_ring_mod=0x16,
                            I_short_delay=0x18,
                            nofx_mute=0x27),
                            0)
                            


mfx_device = Default(Enum(Int8ul, nofx_thru=0x0,
                            nofx_mute=0x27,
                            M_mkp2_comp=0x28,
                            M_sr1_comp=0x29,
                            M_limiter=0x2a,
                            M_eq_4_band=0x2b,
                            M_wah=0x2c,
                            M_multimodefilter=0x2d,
                            M_distortion=0x2e,
                            M_tubepre=0x2f,
                            M_chorus=0x31,
                            M_flanger=0x32,
                            M_phaser=0x33,
                            M_tremolo=0x34,
                            M_level_mod=0x35,
                            M_hall_reverb=0x36,
                            M_smooth_hall=0x37,
                            M_wet_plate_reverb=0x38,
                            M_dry_plate_reverb=0x39,
                            M_room_reverb=0x3a,
                            M_mod_delay=0x3b,
                            M_tape_echo=0x3c,
                            M_grain_shifter=0x3d,
                            M_decimator=0x3e,
                            M_kpq_looper=0x3f,
                            M_vinyl_break=0x40),
                            0)


ifx_1_params = Switch(this.ifx_1_device, {'nofx_thru':nofx_thru_params,
                                            'I_mkp2_comp':I_mkp2_comp_params,
                                            'I_sr1_comp':I_sr1_comp_params,
                                            'I_cheap_comp':I_cheap_comp_params,
                                            'I_punch':I_punch_params,
                                            'I_limiter':I_limiter_params,
                                            'I_eq_2_band':I_eq_2_band_params,
                                            'I_eq_4_band':I_eq_4_band_params,
                                            'I_exciter':I_exciter_params,
                                            'I_decimator':I_decimator_params,
                                            'I_filter':I_filter_params,
                                            'I_distortion':I_distortion_params,
                                            'I_acid_driver':I_acid_driver_params,
                                            'I_chorus':I_chorus_params,
                                            'I_flanger':I_flanger_params,
                                            'I_phaser':I_phaser_params,
                                            'I_tremolo':I_tremolo_params,
                                            'I_level_mod':I_level_mod_params,
                                            'I_ring_mod':I_ring_mod_params,
                                            'I_short_delay':I_short_delay_params,
                                            'nofx_mute':nofx_mute_params}, 
                                            default=nofx_thru_params)

ifx_2_params = If (this.ifx_1_device in ['nofx_thru', 'I_cheap_comp', 
                                         'I_punch', 'I_eq_2_band', 'I_filter', 
                                         'I_acid_driver', 'nofx_mute'], 
                                          Switch(this.ifx_2_device, {
                                             'nofx_thru':nofx_thru_params,
                                             'I_cheap_comp':I_cheap_comp_params,
                                             'I_punch':I_punch_params,
                                             'I_eq_2_band':I_eq_2_band_params,
                                             'I_filter':I_filter_params,
                                             'I_acid_driver':I_acid_driver_params,
                                             'nofx_mute':nofx_mute_params},
                                             default=nofx_thru_params))


mfx_params = Switch(this.mfx_device, {'nofx_thru':nofx_thru_params,
                                        'nofx_mute':nofx_mute_params,
                                        'M_mkp2_comp':M_mkp2_comp_params,
                                        'M_sr1_comp':M_sr1_comp_params,
                                        'M_limiter':M_limiter_params,
                                        'M_eq_4_band':M_eq_4_band_params,
                                        'M_wah':M_wah_params,
                                        'M_multimodefilter':M_multimodefilter_params,
                                        'M_distortion':M_distortion_params,
                                        'M_tubepre':M_tubepre_params,
                                        'M_chorus':M_chorus_params,
                                        'M_flanger':M_flanger_params,
                                        'M_phaser':M_phaser_params,
                                        'M_tremolo':M_tremolo_params,
                                        'M_level_mod':M_level_mod_params,
                                        'M_hall_reverb':M_hall_reverb_params,
                                        'M_smooth_hall':M_smooth_hall_params,
                                        'M_wet_plate_reverb':M_wet_plate_reverb_params,
                                        'M_dry_plate_reverb':M_dry_plate_reverb_params,
                                        'M_room_reverb':M_room_reverb_params,
                                        'M_mod_delay':M_mod_delay_params,
                                        'M_tape_echo':M_tape_echo_params,
                                        'M_grain_shifter':M_grain_shifter_params,
                                        'M_decimator':M_decimator_params,
                                        'M_kpq_looper':M_kpq_looper_params,
                                        'M_vinyl_break':M_vinyl_break_params}, 
                                        default=nofx_mute_params)


fx_preset = Struct(Seek(0x01),
                    'name' / Default(PaddedString(0xf, 'ascii'), 'Init FX Preset'), Padding(2),
                    'fx_control_map' / Default(fx_control_map, None), Seek(0x12a),
                    'ifx_1_device' / ifx_device, Seek(0x135),
                    'ifx_1_params' / ifx_1_params, Seek(0x174),
                    'ifx_2_device' / ifx_device, Seek(0x17f),
                    'ifx_2_params' / ifx_2_params, Seek(0x1be), 
                    'mfx_device' / mfx_device, Seek(0x1c9),
                    'mfx_params' / mfx_params, Seek(0x209), Padding(3),
                    )
                    
