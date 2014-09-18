# -*- coding: utf-8 -*-
import serial
from twisted.internet import protocol, reactor, task
from twisted.internet.serialport import SerialPort
from twisted.protocols import basic


class DevicePirit(protocol.Protocol, object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DevicePirit, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if getattr(self, 'state', None) is not None:
            return
        self.last_error = ''
        self.state = ''
        self.current_command = None

    def connectionMade(self):
        self.state = 'called Connection made'
        print 'Connection made!'

    def _retry_connect(self, reason):
        self.state = reason
        d = task.deferLater(reactor, 60, self.makeConnection)
        d.addErrback(lambda reason: self._retry_connect(reason))

    def connectionLost(self, reason):
        print 'Connection lost!'
        print reason
        self._retry_connect('called Connection lost')

    def dataReceived(self, data):
        print "Response: {0}".format(data)
        if not self.current_command:
            print 'No command for data processing!!!'
            return
        self.current_command.process_data(data)

    def sendString(self, msg):
        self.transport.write(msg)

    def get_password(self):
        return self.transport.pirit_password