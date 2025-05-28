import sys
import mido
import logging

from pathlib import Path
from time import sleep

from e2sysex import *


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def display_menu(menu):
    for k, v in menu.items():
        print(k, v)


def bytes_to_string(byt):
    return " ".join([hex(b)[2:].upper().rjust(2, "0") for b in byt])


logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) < 2:
    print("Usage:\n")
    print("python execute_freetribe.py FILE_PATH [PORT_NAME]\n")
    exit(0)

bin_path = Path(sys.argv[1])

in_port = None
out_port = None

if len(sys.argv) > 2:
    in_port = sys.argv[2]

if len(sys.argv) > 3:
    out_port = sys.argv[3]


if not bin_path.is_file():
    logging.error("File not found: " + str(bin_path))
    exit(0)


logging.info("Load and execute Freetribe.")

logging.info("Initialising MIDI connection.")

e = E2Sysex(in_port, out_port)

logging.info("Pivoting to Freetribe loader.")

msg = mido.Message("sysex", data=e.sysex_head + [0x58] + syx_enc(bytes(8)))
e.outport.send(msg)

sleep(1)

logging.info("Sending magic word.")

r = e.test_sysex_message(list(b"\x64\x01\x23\x45\x67"))

logging.debug("Received message: " + bytes_to_string(r))

response_word = r[5:9]
if response_word != [0x76, 0x54, 0x32, 0x10]:
    logging.error("Incorrect response: " + bytes_to_string(response_word))
    exit(0)

logging.info("Loading binary...")

with open(bin_path, "rb") as f:
    code = f.read()

code_chunks = list(chunks(code, 0x100))
num_chunks = len(code_chunks)

for i, chunk in enumerate(code_chunks):
    logging.info("Loading chunk: " + str(i) + " of " + str(num_chunks))

    chunk = chunk.ljust(256, b"\x00")[:256]

    r = e.load_cpu_ram(chunk)

    logging.debug("Received message: " + bytes_to_string(r))

    if r[5] != 0x21:
        logging.error("Load chunk failed.")
        exit(0)
    else:
        logging.info("Load chunk success.")


execute_address = 0x80000000
r = e.execute_cpu_ram(execute_address)

print()
print(bytes(r[1:-1]).decode("ascii"))

for msg in e.inport:
    if msg.type == "sysex":
        print("".join(chr(i) for i in msg.data))
