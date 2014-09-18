# -*- coding: utf-8 -*-
import struct
import random
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import task

from device import DevicePirit
from utils import *


class HaveCommand(Exception):
    """Уже есть команда в обработке"""
    pass

class PacketError(Exception):
    """Ошибка форматирования пакета"""
    pass

class STXError(PacketError):
    pass

class PackageIDError(PacketError):
    pass

class ResponseCommandIDNotEqError(PacketError):
    pass

class ETXError(PacketError):
    pass

class CRCResponseError(PacketError):
    pass

class CommandError(Exception):
    """Ошибка с оборудования"""
    pass


class Command(object):
    """
    Команда.
    Способ использования
    from xxx import SomeCommand
    c = SomeCommand(some_args)
    c.addCallback(что выполнится при успехе)
    c.addErrback(что выполнится при фейле)
    """
    CODE = None

    def __init__(self):
        device = DevicePirit()
        self._connect_to_device(device)

    def start(self):
        self.d = defer.Deferred()
        t = task.deferLater(reactor, 0, self.run)
        t.addErrback(lambda err: self.d.errback(err))
        return self.d

    def _connect_to_device(self, device):
        self.device = device
        if self.device.current_command is not None:
            raise HaveCommand()
        self.device.current_command = self

    def run(self):
        msg = self.make_packet()
        self.device.sendString(msg)

    def make_packet(self):
        #STX
        msg = struct.pack('!B', 0x02)
        #Пароль связи
        password = self.device.get_password()
        assert(len(password) == 4, "Поддерживается только 4х сильмвольный пароль")
        msg += ''.join([struct.pack('!c', s) for s in password])
        #ID пакета
        self.package_id = random.randrange(0x20, 0xF0)
        msg += struct.pack('!B', self.package_id)
        #код команды
        code = str(self.CODE)
        assert(len(code) == 2, "Код должен быть 2х символьным")
        msg += ''.join([struct.pack('!c', s) for s in code])
        #Данные
        msg += self.get_payload()
        #ETX
        msg += struct.pack('!B', 0x03)
        #CRC
        msg += make_checksum(msg)
        return msg


    def get_payload(self):
        """Нужно переопределить, если есть данные"""
        return ""

    def process_data(self, data):
        offset = 0
        #STX
        stx = struct.unpack_from('!B', data, offset=offset)[0]
        if stx != 0x02:
            self.d.errback(STXError())
            return
        offset += 1
        #PacketID
        p_id = struct.unpack_from('!B', data, offset=offset)[0]
        if p_id != self.package_id:
            self.d.errback(PackageIDError())
            return
        offset += 1
        #command id
        cmd_id = ''.join(struct.unpack_from('<cc', data, offset=offset))
        if cmd_id != str(self.CODE):
            self.d.errback(ResponseCommandIDNotEqError())
            return
        offset += 2
        #ErrorCode
        err_code = ''.join(struct.unpack_from('<cc', data, offset=offset))
        if err_code != '00':
            self.d.errback(CommandError(err_code))
            return
        offset += 2
        #payload
        length, payload = self.process_payload(data, offset)
        offset += length
        #ETX
        etx = struct.unpack_from('!B', data, offset=offset)[0]
        if etx != 0x03:
            self.d.errback(ETXError())
            return
        offset += 1
        #CRC
        if data[offset:2] != make_checksum(data[:offset+2]):
            self.d.errback(CRCResponseError())
            return
        #all ok
        self.d.callback(('ok', payload))

    def process_payload(self, data, offset):
        """
        Нужно переопределить
        Возвращает кортедж (кол-во байт, данные)
        """
        return (0, "")

    def command_end(self):
        """Завершение"""
        self.device.current_command = None


class PrintActivizationReportEKLZCommand(Command):
    """
    Распечатать отчет по активизации ЕКЛЗ
    """
    CODE = '76'

