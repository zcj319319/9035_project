#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Time    : 2022/10/17 12:16
Author  : zhuchunjin
Email   : chunjin.zhu@taurentech.net
File    : spi_interface.py
Software: PyCharm
'''
import time
from binascii import hexlify
from ctypes import *
from PyQt5 import QtGui, QtWidgets
from pyftdi.ftdi import Ftdi
from pyftdi.gpio import GpioAsyncController
from pyftdi.spi import SpiController

from run_project.config_choose import ControlSPI
from run_project.config_choose.tr9305_case import spi_attribute

from ui_file.box_usb_link import Ui_MainWindow


class LoadMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.url_port = []
        self.port = []
        self.spi_a = None
        super().__init__()
        self.setupUi(self)
        self.log_textBrowser.setText("{0} initializing...".format(time.strftime("%F %T")))

    def textBrowser_normal_log(self, info):
        self.log_textBrowser.append("<font color='black'>" + "{0} {1}".format(time.strftime("%F %T"), info))

    def textBrowser_error_log(self, info):
        self.log_textBrowser.append("<font color='red'>" + '{0} {1}'.format(time.strftime("%F %T"), info))


class spi_interface:

    def __init__(self, Object):
        self.logfile = None
        self.super_object = Object
        self.communicate_mode = None

    def write_atom(self, addr, data):
        # 读操作
        if self.communicate_mode == 'box':
            write_buffer = (c_ubyte * 3)()
            read_buffer = (c_ubyte * 1)()
            addr_str = '{:0>4x}'.format(addr)
            write_buffer[0] = int(addr_str[0:2], 16)
            write_buffer[1] = int(addr_str[2:], 16)
            write_buffer[2] = data
            nRet = ControlSPI.VSI_WriteBytes(ControlSPI.VSI_USBSPI, 0, 0, write_buffer, 3)
        if self.communicate_mode == 'log':
            self.logfile.write('0x{:0>4x} 0x{:0>2x}\n'.format(addr, data))
            self.super_object.textBrowser_normal_log('0x{:0>4x} 0x{:0>2x}\n'.format(addr, data))
        if self.communicate_mode == 'usb':
            addr_str_1 = '%#x' % addr
            data_str_1 = '%#x' % data
            self.super_object.textBrowser_normal_log('write addr = ' + addr_str_1 + ' data = ' + data_str_1)
            try:
                write_buffer = []
                addr_str = addr_str_1.split('x')[1]
                if len(addr_str) != 4:
                    new_addr = '0' * (4 - len(addr_str)) + addr_str
                else:
                    new_addr = addr_str
                write_buffer.append(int(new_addr[0:2], 16))
                write_buffer.append(int(new_addr[2:], 16))
                write_buffer.append(int(data_str_1.split('x')[1], 16))
                self.super_object.spi_a.write(write_buffer, 1)
            except Exception as e:
                self.super_object.textBrowser_error_log('write_atom err:%s' % e)

    def read_atom(self, addr):
        # 写操作
        if self.communicate_mode == 'box':
            write_buffer = (c_ubyte * 2)()
            read_buffer = (c_ubyte * 1)()
            addr_str = '{:0>4x}'.format(addr)
            write_buffer[0] = int(addr_str[0:2], 16) + 128
            write_buffer[1] = int(addr_str[2:], 16)
            nRet = ControlSPI.VSI_WriteReadBytes(ControlSPI.VSI_USBSPI, 0, 0, write_buffer, 2, read_buffer, 1)
            info = 'read addr = ' + addr_str + ' data = ' + str(read_buffer[0])
            self.super_object.textBrowser_normal_log(info)
            return read_buffer
        if self.communicate_mode == 'usb':
            addr_str_1 = '%#x' % addr
            try:
                write_buffer = []
                read_buffer = []
                addr_str = addr_str_1.split('x')[1]
                if len(addr_str) != 4:
                    new_addr = '0' * (4 - len(addr_str)) + addr_str
                else:
                    new_addr = addr_str
                write_buffer.append(int(new_addr[0:2], 16) + 128)
                write_buffer.append(int(new_addr[2:], 16))
                read_data = self.super_object.spi_a.exchange(write_buffer, 1)
                read_buffer.append(read_data)
                read_data_str = hex(int(hexlify(read_data).decode(), 16))
                info = 'read addr = ' + addr_str + ' data = ' + read_data_str
                self.super_object.textBrowser_normal_log(info)
                if read_buffer == [bytearray(b' ')]:
                    read_buffer = [0]
                return read_buffer
            except Exception as e:
                print(e)

    def spi_config(self):
        # 初始化
        if self.communicate_mode == 'box':
            try:
                nRet = ControlSPI.VSI_ScanDevice(1)
                # Initialize device
                SPI_Init = ControlSPI.VSI_INIT_CONFIG()
                SPI_Init.ClockSpeed = 1125000
                SPI_Init.ControlMode = 3
                SPI_Init.CPHA = 0
                SPI_Init.CPOL = 0
                SPI_Init.LSBFirst = 0
                SPI_Init.MasterMode = 1
                SPI_Init.SelPolarity = 0
                SPI_Init.TranBits = 8
                nRet = ControlSPI.VSI_InitSPI(ControlSPI.VSI_USBSPI, 0, byref(SPI_Init))
                if (nRet <= 0):
                    self.super_object.textBrowser_error_log("No device connect!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/OFF.png"))
                else:
                    self.super_object.textBrowser_normal_log("Connected device number is:" + repr(nRet))
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/on.png"))
                    # Open device
                nRet = ControlSPI.VSI_OpenDevice(ControlSPI.VSI_USBSPI, 0, 0)
                if (nRet != ControlSPI.ERR_SUCCESS):
                    self.super_object.textBrowser_error_log("Open device error!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/OFF.png"))
                else:
                    self.super_object.textBrowser_normal_log("Open device success!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/on.png"))
                    # Initialize device
                nRet = ControlSPI.VSI_InitSPI(ControlSPI.VSI_USBSPI, 0, byref(SPI_Init))
                if (nRet != ControlSPI.ERR_SUCCESS):
                    self.super_object.textBrowser_error_log("Initialization device error!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/OFF.png"))
                else:
                    self.super_object.textBrowser_normal_log("Initialization device success!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/on.png"))
            except Exception as e:
                self.super_object.textBrowser_normal_log("%s" % e)
        if self.communicate_mode == 'log':
            self.logfile = open('addrTbl.txt', 'w')
        if self.communicate_mode == 'usb':
            try:
                Ftdi.show_devices()
                dev_urls = Ftdi.list_devices()
                # Scan device
                if len(dev_urls) == 0:
                    self.super_object.textBrowser_error_log("Initialization device error!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/OFF.png"))
                else:
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/on.png"))
                    for i in range(dev_urls[0][1]):
                        self.super_object.url_port.append(
                            r'ftdi://ftdi:4232:' + str(dev_urls[0][0].bus) + ':' + str(
                                hex(dev_urls[0][0].address)) + r'/' + str(
                                i + 1))
                    self.super_object.port.append(SpiController())
                    self.super_object.port[0].configure(self.super_object.url_port[0], cs_count=1)
                    self.super_object.port.append(SpiController())
                    self.super_object.port[1].configure(self.super_object.url_port[1], cs_count=1)
                    self.super_object.port.append(GpioAsyncController())
                    self.super_object.port[2].configure(self.super_object.url_port[2], direction=0xff, initial=0x83)
                    self.super_object.port.append(GpioAsyncController())
                    self.super_object.port[3].configure(self.super_object.url_port[3], direction=0x00, initial=0x0)
                    # Set channelA
                    dq = spi_attribute
                    self.super_object.spi_a = self.super_object.port[dq.chn].get_port(dq.cs)
                    self.super_object.spi_a.set_frequency(dq.freq)
                    self.super_object.spi_a.set_mode(dq.mode)
                    self.super_object.textBrowser_normal_log(
                        'available device is %s' % ','.join(self.super_object.url_port))
            except Exception as e:
                self.super_object.textBrowser_normal_log("%s" % e)

    def spi_release(self):
        try:
            self.super_object.port[0].close()
            self.super_object.port[1].close()
            self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/OFF.png"))
            self.super_object.textBrowser_normal_log("release spi")
        except Exception as e:
            self.super_object.textBrowser_error_log('%s' % e)

    def spi_update(self):
        # 更新
        # Scan device
        # Set channelA
        try:
            if self.communicate_mode == 'box':
                nRet = ControlSPI.VSI_ScanDevice(1)
                if nRet <= 0:
                    self.super_object.textBrowser_error_log('No device connect!')
                else:
                    self.super_object.textBrowser_normal_log("Connected device number is:" + repr(nRet))
                # Open device
                nRet = ControlSPI.VSI_OpenDevice(ControlSPI.VSI_USBSPI, 0, 0)
                if nRet != ControlSPI.ERR_SUCCESS:
                    self.super_object.textBrowser_error_log("Open device error!")
                else:
                    self.super_object.textBrowser_normal_log("Open device success!")
                # Initialize device
                SPI_Init = ControlSPI.VSI_INIT_CONFIG()
                if self.super_object.lineEdit.text() == '':
                    SPI_Init.ClockSpeed = 1125000
                else:
                    SPI_Init.ClockSpeed = int(float(self.super_object.lineEdit.text()) * 1000000)
                SPI_Init.ControlMode = 3
                SPI_Init.CPHA = 0
                SPI_Init.CPOL = 0
                SPI_Init.LSBFirst = 0
                SPI_Init.MasterMode = 1
                SPI_Init.SelPolarity = 0
                SPI_Init.TranBits = 8
                nRet = ControlSPI.VSI_InitSPI(ControlSPI.VSI_USBSPI, 0, byref(SPI_Init))
                if nRet != ControlSPI.ERR_SUCCESS:
                    self.super_object.textBrowser_error_log("Initialization device error!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/OFF.png"))
                else:
                    self.super_object.textBrowser_normal_log("Initialization device success!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/on.png"))
            if self.communicate_mode == 'usb':
                Ftdi.show_devices()
                dev_urls = Ftdi.list_devices()
                # Scan device
                if len(dev_urls) == 0:
                    self.super_object.textBrowser_error_log("Initialization device error!")
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/OFF.png"))
                else:
                    self.super_object.label_6.setPixmap(QtGui.QPixmap(":/status/on.png"))
                    if len(self.super_object.port) > 0:
                        self.super_object.port[0].close()
                        self.super_object.port[1].close()
                        self.super_object.port = []
                        self.super_object.url_port = []
                    for i in range(dev_urls[0][1]):
                        self.super_object.url_port.append(
                            r'ftdi://ftdi:4232:' + str(dev_urls[0][0].bus) + ':' + str(
                                hex(dev_urls[0][0].address)) + r'/' + str(
                                i + 1))
                    self.super_object.port.append(SpiController())
                    self.super_object.port[0].configure(self.super_object.url_port[0], cs_count=1)
                    self.super_object.port.append(SpiController())
                    self.super_object.port[1].configure(self.super_object.url_port[1], cs_count=1)
                    # self.super_object.port.append(GpioAsyncController())
                    # self.super_object.port[2].configure(self.super_object.url_port[2], direction=0xff, initial=0x83)
                    # self.super_object.port.append(GpioAsyncController())
                    # self.super_object.port[3].configure(self.super_object.url_port[3], direction=0x00, initial=0x0)
                    # Set channelA
                    dq = spi_attribute
                    self.super_object.spi_a = self.super_object.port[dq.chn].get_port(dq.cs)
                    if self.super_object.lineEdit.text() == '':
                        SPI_Init_ClockSpeed = dq.freq
                    else:
                        SPI_Init_ClockSpeed = int(float(self.super_object.lineEdit.text()) * 1000000)
                    self.super_object.spi_a.set_frequency(SPI_Init_ClockSpeed)
                    self.super_object.spi_a.set_mode(dq.mode)
                    self.super_object.textBrowser_normal_log(
                        'available device is %s' % ','.join(self.super_object.url_port))
        except Exception as e:
            self.super_object.textBrowser_normal_log("%s" % e)
