# -*- coding: utf-8 -*-

def make_checksum(bytestr):
    checksum_bin = reduce(lambda crc, x: crc ^ ord(x), bytestr[1:], 0)
    checksum = '{0:2x}'.format(checksum_bin)
    return checksum

# from serial.tools import list_ports
# print [p for p in list_ports.comports() if p[2] != 'n/a']