import os
import sys

if len(sys.argv) < 3:
    print("Usage:")
    print()
    print("e2pat_convert.py FILE_PATH [synth|sampler]")
    exit(0)

path = sys.argv[1]
device = sys.argv[2]

if os.path.exists(path):

    filename, extension = os.path.splitext(path)

    if extension == ".e2spat" or extension == ".e2pat":
        postfix = "pat"

    elif extension == ".e2sallpat" or extension == ".e2allpat":
        postfix = "allpat"

    else:
        print("File type not supported.")
        exit(0)

    with open(path, "rb") as f:
        hak = bytearray(f.read())

    if device == "sampler":
        # e2s
        hak[0x10:0x20] = "e2sampler".encode("ascii").ljust(16, b"\x00")
        prefix = ".e2s"

    elif device == "synth":
        # e2
        hak[0x10:0x20] = "electribe".encode("ascii").ljust(16, b"\x00")
        prefix = ".e2"

    else:
        print(
            "Incorrect argument:",
            device + ".",
            "Must be either 'synth' or 'sampler'.",
        )
        exit(0)

    print("Modified header of", os.path.basename(path))

    output_dir = os.path.dirname(path)

    output_filename = "converted-" + filename + prefix + postfix

    output_path = os.path.join(output_dir, output_filename)

    print("Saved to", output_path)

    with open(output_path, "wb") as f:
        f.write(hak)

else:
    print("File not found.")