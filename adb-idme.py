#!/usr/bin/env python3
#
# This file is part of 'adb-idme'. Copyright (c) 2024 bengris32.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from ctypes import Structure, sizeof, c_byte, c_uint
from sys import argv

FOS_FLAGS_ADB_ON = 0x1
FOS_FLAGS_CONSOLE_ON = 0x4
FOS_FLAGS_RAMDUMP_ON = 0x8
FOS_FLAGS_VERBOSITY_ON = 0x10
FOS_FLAGS_ADB_AUTH_DISABLE = 0x20
FOS_FLAGS_BOOT_DEXOPT = 0x100

class idme_entry(Structure):
    _fields_ = [
        ('name', c_byte * 16), # 16 byte string
        ('size', c_uint), # 4 byte unsigned integer
        ('unk1', c_uint), # 4 byte unsigned integer ?
        ('unk2', c_uint), # 4 byte unsigned integer ?
    ]

def find_idme_entry(idme, entry_name):
    idme_size = len(idme)
    offset = 0x10

    while offset < idme_size:
        entry_bytes = idme[offset:offset+sizeof(idme_entry)]

        entry = idme_entry.from_buffer_copy(entry_bytes)
        name = bytes(entry.name).rstrip(b'\x00').decode('utf-8')
        if name == entry_name:
            # return struct and offset of data
            return (entry, offset + sizeof(idme_entry))

        offset += sizeof(idme_entry) + entry.size

    raise RuntimeError("Entry %s not found in IDME" % entry_name)

def main():
    if len(argv) > 2:
        input = argv[1]
        output = argv[2]
    else:
        print("Usage: %s <input> <output>" % argv[0])
        exit(1)

    with open(input, 'rb') as idme:
        idme = bytearray(idme.read())

    header = idme[:8]
    assert header == b'beefdeed', "Invalid header"

    entry, flags_offset = find_idme_entry(idme, 'fos_flags')
    print("Found fos_flags at offset: 0x%0x" % flags_offset)

    flags = int.from_bytes(idme[flags_offset:flags_offset+entry.size], 'little')

    print("ADB Enabled = %s" % ((flags & FOS_FLAGS_ADB_ON) != 0))
    print("ADB Auth Disabled = %s" % ((flags & FOS_FLAGS_ADB_AUTH_DISABLE) != 0))
    print("Serial Console Enabled = %s" % ((flags & FOS_FLAGS_CONSOLE_ON) != 0))
    print("Ramdump Enabled = %s" % ((flags & FOS_FLAGS_RAMDUMP_ON) != 0))
    print("Verbosity Enabled = %s" % ((flags & FOS_FLAGS_VERBOSITY_ON) != 0))
    print("Dexopt on boot Enabled = %s" % ((flags & FOS_FLAGS_BOOT_DEXOPT) != 0))

    # Enable serial console, adb, and disable adb auth.
    # The FOS_FLAGS_ADB_AUTH_DISABLE flag may not work on
    # some devices (more commonly seen on Echo devices).
    flags |= FOS_FLAGS_ADB_ON
    flags |= FOS_FLAGS_ADB_AUTH_DISABLE
    flags |= FOS_FLAGS_CONSOLE_ON

    idme[flags_offset:flags_offset+entry.size] = flags.to_bytes(entry.size, 'little')

    with open(output, 'wb') as output:
        output.write(idme)

    print("Successfully patched idme to enable ADB.")

if __name__ =='__main__':
    main()
