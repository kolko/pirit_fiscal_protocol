# -*- coding: utf-8 -*-
import serial
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort

from device import DevicePirit
from commands import PrintActivizationReportEKLZCommand

# http://www.1c.ru/news/info.jsp?id=12122
# http://erpandcrm.ru/sbis_presto_userguide.ru/10/otkritie_smeni.htm


p = SerialPort(DevicePirit(), '/dev/ttyUSB0', reactor, baudrate=57600, bytesize=8,
                       parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
p.pirit_password = 'PIRI'

c = PrintActivizationReportEKLZCommand().start()

def pr(x, y=None):
    print '321'
    print x, y

c.addCallback(lambda x: pr(x))
c.addErrback(lambda x: pr('!', x))
reactor.run()