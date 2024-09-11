# Replace boot splash screen image.

import os
import argparse
import hashlib

from PIL import Image
from PIL import ImageOps


# Return 1bpp image from bytes.
def get_image(data, width, height):
    image = Image.new("1", (width, height))

    for i in range(len(data) // width):
        # get 8 pixel high row of image
        row = data[i * width : i * width + width]

        img = Image.frombytes("1", (8, width), bytes(row), decoder_name="raw").rotate(
            270, expand=True
        )

        # build image from rows
        image.paste(img, (0, img.height * i))

    image = ImageOps.mirror(image)

    return image


# Path to 1bpp image file, length of buffer in firmware.
def set_image(path, length):
    image = Image.open(path)

    image = ImageOps.mirror(image)

    width, height = image.size
    pixel_data = []

    # Transform image.
    for i in range(length // height):
        upper = i * 8
        lower = upper + 8
        row = (
            image.crop((0, upper, width, lower))
            .rotate(90, expand=True)
            .tobytes(encoder_name="raw")
        )
        pixel_data.extend(row)

    pixel_data = bytes(pixel_data)

    # truncate / extend data
    pixel_data = pixel_data[:length].ljust(length)

    return pixel_data


def get_digest(path):
    h = hashlib.sha256()

    with open(path, "rb") as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def main():
    usage = """ Replace boot splash screen in Hacktribe firmware.
                """
    parser = argparse.ArgumentParser(epilog=usage)
    parser.add_argument("input_path", help="/path/to/hacked-SYSTEM.VSB")
    parser.add_argument("image_path", help="/path/to/image.bmp")
    parser.add_argument(
        "-b", "--backup", dest="backup_path", help="/path/to/backup.bmp"
    )
    args = parser.parse_args()

    input_path = args.input_path
    image_path = args.image_path
    backup_path = args.backup_path

    hash_path = "./hash/hacked-SYSTEM.VSB.sha"
    hash_path_mod = "./hash/modified-hacked-SYSTEM.VSB.sha"
    hash_path_og = "./hash/SYSTEM.VSB.sha"

    with open(hash_path, "r") as f:
        hash = f.readlines()[0].split()[0]

    with open(hash_path_mod, "r") as f:
        hash_mod = f.readlines()[0].split()[0]

    with open(hash_path_og, "r") as f:
        hash_og = f.readlines()[0].split()[0]

    if os.path.exists(input_path):
        print("Found firmware file:", os.path.basename(input_path))
    else:
        print("Firmware file not found:", os.path.basename(input_path))
        exit()

    if os.path.exists(image_path):
        print("Found firmware file:", os.path.basename(image_path))
    else:
        print("Image file not found:", os.path.basename(image_path))
        exit()

    if get_digest(input_path) == hash:
        print("Input hash matches Hacktribe firmware.")

    elif get_digest(input_path) == hash_mod:
        print("Input hash matches Hacktribe firmware with modified header.")

    elif get_digest(input_path) == hash_og:
        print("Input hash matches Electribe 2 Sampler firmware.")

    else:
        print("Input hash does not match any supported firmware.")
        exit()

    with open(input_path, "rb") as f:
        vsb = bytearray(f.read())

    head = vsb[:0x100]
    body = vsb[0x100:]

    base = 0xF9854
    length = 128 * 8

    start = base
    end = base + length

    pre_hash_head = hashlib.sha256(head).hexdigest()
    pre_hash_before = hashlib.sha256(body[:start]).hexdigest()
    pre_hash_after = hashlib.sha256(body[end:]).hexdigest()

    if backup_path:
        print("Backing up existing splash image.")
        old_bmp = body[start:end]
        old_bmp = get_image(old_bmp, 128, 64)
        old_bmp.save(backup_path, mode="1")

    body[start:end] = set_image(image_path, length)

    post_hash_head = hashlib.sha256(head).hexdigest()
    post_hash_before = hashlib.sha256(body[:start]).hexdigest()
    post_hash_after = hashlib.sha256(body[end:]).hexdigest()

    if (
        (pre_hash_before != post_hash_before)
        or (pre_hash_after != post_hash_after)
        or (pre_hash_head != post_hash_head)
    ):
        print("Output hash error, firmware corrupt!")
        exit()
    else:
        print("Output hash matches, only splash image bytes may have changed.")

    vsb = head + body

    assert len(vsb) == 0x200100

    print("Everything appears to be OK, writing firmware.")

    output_path = input_path
    with open(output_path, "wb") as f:
        f.write(vsb)


if __name__ == "__main__":
    main()
