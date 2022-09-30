# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 09:21:00 2022

@author: xyLucas
"""

import time

from ctypes import *
from binascii import hexlify
from ctypes import *

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from pyftdi.ftdi import Ftdi
from pyftdi.gpio import GpioAsyncController
from pyftdi.spi import SpiController
from ui_file import logo_rc
from ui_file import status_rc
from ui_file import struc_rc

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


class REG_STRUCT:
    _structs = []

    def __init__(self, Object,*args, **kwargs):
        super().__init__()
        if len(args) > len(self._structs):
            raise TypeError('Expected {} arguments'.format(len(self._structs)))

        ## Set all the positional arguments
        for name, value in zip(self._structs, args):
            setattr(self, name, value)

        ## Set the remaining keyword arguments
        for name in self._structs[len(args):]:
            setattr(self, name, kwargs.pop(name))

        # Set the additional arguments(if any)
        extra_args = kwargs.keys() - self._structs
        for name in extra_args:
            setattr(self, name, kwargs.pop(name))

        if kwargs:
            raise TypeError('Invalid argument(s): {}'.format(','.join(kwargs)))


class TR9305_CFG(REG_STRUCT):
    _structs = ['fs', 'lanerate']

    def __init__(self, Object,*args, **kwargs):
        self.logfile = None
        self.super_object= Object
        super(TR9305_CFG, self).__init__(Object,*args, **kwargs)

    def write_atom(self, addr, data):
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

    def spi_update(self):
        # Scan device
        # Set channelA
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
            else:
                self.super_object.textBrowser_normal_log("Initialization device success!")
        if self.communicate_mode == 'usb':
            if len(self.super_object.url_port) != 0:
                dq = spi_attribute
                self.super_object.spi_a = self.super_object.port[dq.chn].get_port(dq.cs)
                if self.super_object.lineEdit.text() == '':
                    SPI_Init_ClockSpeed = dq.freq
                else:
                    SPI_Init_ClockSpeed = int(float(self.super_object.lineEdit.text()) * 1000000)
                self.super_object.spi_a.set_frequency(SPI_Init_ClockSpeed)
                self.super_object.spi_a.set_mode(dq.mode)
                self.super_object.textBrowser_normal_log('spi_update success')
            else:
                self.super_object.textBrowser_error_log('spi_update error')

    def read_atom(self, addr):
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
                return read_buffer
            except Exception as e:
                print(e)

    def tr9305_top_config(self):
        if 'communicate_mode' not in dir(self):
            self.communicate_mode = 'log'
        self.spi_config()
        if 'ddc_dcm' not in dir(self):
            self.ddc_dcm = 1
        self.adc_config()
        self.serdes_config()
        self.dig_config()
        # if self.communicate_mode == 'log':
        #     self.logfile.close()

    def spi_config(self):
        if self.communicate_mode == 'box':
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
        if self.communicate_mode == 'log':
            self.logfile = open('addrTbl.txt', 'w')
        if self.communicate_mode == 'usb':
            try:
                Ftdi.show_devices()
                dev_urls = Ftdi.list_devices()
                # Scan device
                if len(dev_urls) == 0:
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
                    self.super_object.textBrowser_normal_log('available device is %s' % ','.join(self.super_object.url_port))
            except Exception as e:
                QMessageBox.information(self.super_object, 'warning', '%s' % e)

    def adc_config(self):
        ## PD on
        self.write_atom(0x1f0d, 0x0)

        for ch_idx in range(2):
            for idx in range(4):
                self.write_atom(0x1001 + idx * 0xa + ch_idx * 0x3c, 0x1)
                self.write_atom(0x1003 + idx * 0xa + ch_idx * 0x3c, 0x3)
                self.write_atom(0x1006 + idx * 0xa + ch_idx * 0x3c, 0x1)
                self.write_atom(0x1008 + idx * 0xa + ch_idx * 0x3c, 0x83)
            self.write_atom(0x1029 + ch_idx * 0x3c, 0x1)
            self.write_atom(0x1033 + ch_idx * 0x3c, 0x0)
            self.write_atom(0x1035 + ch_idx * 0x3c, 0x80)
            self.write_atom(0x1035 + ch_idx * 0x3c, 0x88)
            self.write_atom(0x103b + ch_idx * 0x3c, 0x8)

        self.write_atom(0x1079, 0x6a)
        self.write_atom(0x107a, 0x43)
        self.write_atom(0x107b, 0x0)
        self.write_atom(0x1080, 0x1)
        self.write_atom(0x1081, 0x0)
        self.write_atom(0x1082, 0x0)
        self.write_atom(0x1083, 0x0)
        self.write_atom(0x1085, 0x10)
        self.write_atom(0x1089, 0x1)
        self.write_atom(0x1089, 0x81)
        self.write_atom(0x1089, 0xc1)
        self.write_atom(0x1089, 0xe1)
        self.write_atom(0x1089, 0xf1)
        self.write_atom(0x11a0, 0x3)

    def serdes_config(self):
        if 'ffetap' not in dir(self):
            self.ffetap = '0dB'
        if self.lanerate >= 2e9 and self.lanerate < 3e9:
            rate = 'fullrate'
            fvco_freq = self.lanerate * 2
            postdiv = 1
            ind = 0
            fbc_div = 0x28
        elif self.lanerate >= 3e9 and self.lanerate < 4e9:
            rate = 'fullrate'
            fvco_freq = self.lanerate * 2
            postdiv = 1
            ind = 1
            fbc_div = 0x28
        elif self.lanerate >= 4e9 and self.lanerate < 6e9:
            rate = 'fullrate'
            fvco_freq = self.lanerate
            postdiv = 0
            ind = 0
            fbc_div = 0x28
        elif self.lanerate >= 6e9 and self.lanerate < 8e9:
            rate = 'halfrate'
            fvco_freq = self.lanerate
            postdiv = 1
            ind = 1
            fbc_div = 0x30
        elif self.lanerate >= 8e9 and self.lanerate < 12e9:
            rate = 'halfrate'
            fvco_freq = self.lanerate / 2
            postdiv = 0
            ind = 0
            fbc_div = 0x3c
        elif self.lanerate >= 12e9 and self.lanerate <= 16e9:
            rate = 'qrate'
            fvco_freq = self.lanerate / 2
            postdiv = 1
            ind = 1
            fbc_div = 0x3c

        refdiv = int(fbc_div * self.fs / fvco_freq / 2)

        ##DCC DLL
        for i in range(8):
            self.write_atom(0x108a + i * 0xa, 0xc0)
        for i in range(8):
            self.write_atom(0x108c + i * 0xa, 0xc0)

        if self.ffetap == '0dB':
            for i in range(8):
                self.write_atom(0x108e + i * 0xa, 0xe)
                self.write_atom(0x108f + i * 0xa, 0xf4)
                self.write_atom(0x1090 + i * 0xa, 0x3c)
        elif self.ffetap == '1p1dB':
            for i in range(8):
                self.write_atom(0x108e + i * 0xa, 0x3e)
                self.write_atom(0x108f + i * 0xa, 0xe4)
                self.write_atom(0x1090 + i * 0xa, 0x30)
        elif self.ffetap == '2p9dB':
            for i in range(8):
                self.write_atom(0x108e + i * 0xa, 0x3e)
                self.write_atom(0x108f + i * 0xa, 0xd4)
                self.write_atom(0x1090 + i * 0xa, 0x32)
        elif self.ffetap == '5dB':
            for i in range(8):
                self.write_atom(0x108e + i * 0xa, 0x3e)
                self.write_atom(0x108f + i * 0xa, 0xc4)
                self.write_atom(0x1090 + i * 0xa, 0x38)
        elif self.ffetap == '8dB':
            for i in range(8):
                self.write_atom(0x108e + i * 0xa, 0x3e)
                self.write_atom(0x108f + i * 0xa, 0xb4)
                self.write_atom(0x1090 + i * 0xa, 0x3c)

        ##tsensor
        self.write_atom(0x1154, 0x80)
        self.write_atom(0xef8, 0x3)
        self.write_atom(0xefa, 0x78)
        self.write_atom(0x107e, 0xf0)
        self.write_atom(0x107f, 0xff)

        ##refdiv&fbc_div
        self.write_atom(0x107d, refdiv)
        self.write_atom(0x1148, fbc_div)

        if ind == 1:
            self.write_atom(0x1145, 0x48)
        else:
            self.write_atom(0x1145, 0x8)

        if postdiv == 1:
            self.write_atom(0x114a, 0x70)
        else:
            self.write_atom(0x114a, 0x50)

        ##PLL setting com
        self.write_atom(0x113a, 0x80)
        self.write_atom(0x113b, 0xfc)
        self.write_atom(0x113c, 0x8f)
        self.write_atom(0x113d, 0x8f)
        self.write_atom(0x113e, 0xf8)
        self.write_atom(0x113f, 0x81)
        self.write_atom(0x1140, 0x0)
        self.write_atom(0x1141, 0xf)
        self.write_atom(0x1142, 0x2)
        self.write_atom(0x1143, 0x40)
        self.write_atom(0x1144, 0xf0)
        self.write_atom(0x1146, 0x1f)
        self.write_atom(0x1147, 0x0)
        self.write_atom(0x1149, 0x0)
        self.write_atom(0x114b, 0xa9)
        self.write_atom(0x114c, 0xff)
        self.write_atom(0x114d, 0xff)
        self.write_atom(0x114e, 0x93)
        self.write_atom(0x114f, 0x24)
        self.write_atom(0x1150, 0x49)
        self.write_atom(0x1151, 0x16)
        self.write_atom(0x1152, 0xf)

        ##dll_ana_setting
        for i in range(8):
            self.write_atom(0x1092 + i * 0xa, 0x84)

        for i in range(8):
            self.write_atom(0x1093 + i * 0xa, 0x0)

        for i in range(8):
            self.write_atom(0x10da + i * 0xc, 0x80)
            self.write_atom(0x10db + i * 0xc, 0x80)
            self.write_atom(0x10dc + i * 0xc, 0x0)
            self.write_atom(0x10dd + i * 0xc, 0x2)
            self.write_atom(0x10de + i * 0xc, 0xff)
            self.write_atom(0x10df + i * 0xc, 0xf)
            self.write_atom(0x10e0 + i * 0xc, 0xe0)
            self.write_atom(0x10e1 + i * 0xc, 0x2f)
            self.write_atom(0x10e2 + i * 0xc, 0x0)
            self.write_atom(0x10e3 + i * 0xc, 0x0)
            self.write_atom(0x10e4 + i * 0xc, 0x0)
            self.write_atom(0x10e5 + i * 0xc, 0x0)

        self.write_atom(0x1153, 0x80)
        self.write_atom(0x115b, 0x2)

        for i in range(8):
            if rate == 'fullrate':
                if self.ffetap == '0dB':
                    self.write_atom(0x1091 + i * 0xa, 0x70)
                else:
                    self.write_atom(0x1091 + i * 0xa, 0x73)
            elif rate == 'halfrate':
                if self.ffetap == '0dB':
                    self.write_atom(0x1091 + i * 0xa, 0x60)
                else:
                    self.write_atom(0x1091 + i * 0xa, 0x63)
            elif rate == 'qrate':
                if self.ffetap == '0dB':
                    self.write_atom(0x1091 + i * 0xa, 0x40)
                else:
                    self.write_atom(0x1091 + i * 0xa, 0x43)

        ##txserdes on
        self.write_atom(0x1089, 0xf0)
        time.sleep(1)
        self.write_atom(0x1089, 0xf1)

        for i in range(8):
            self.write_atom(0x10e3 + i * 0xc, 0x2)
        for i in range(8):
            self.write_atom(0x10e3 + i * 0xc, 0x0)

        self.write_atom(0x1087, 0x4)
        self.write_atom(0x1087, 0xc)

    def dig_config(self):
        self.crg_config()
        self.pfilter_config()
        self.fast_detect()
        self.signal_monitor()
        self.ddc_config()
        self.jesd204b_config()
        self.calib_config()

    def crg_config(self):
        if 'chip_mode' not in dir(self):
            self.chip_mode = 'fullband'
        if self.chip_mode == 'fs*4':
            self.write_atom(0xf0a, 0x5)
        else:
            self.write_atom(0xf0a, 0x4)
        link_div = int(10 * self.fs / self.lanerate)
        self.write_atom(0xf0d, link_div)

    def pfilter_config(self):
        if 'pfilter_mode' not in dir(self):
            self.pfilter_mode = 'bypass'

    def fast_detect(self):
        if 'fast_detect_en' not in dir(self):
            self.fast_detect_en = 0

    def signal_monitor(self):
        if 'signal_monitor_en' not in dir(self):
            self.signal_monitor_en = 0

    def ddc_config(self):
        if 'inputMode' not in dir(self):
            self.inputMode = 'Real'
        self.write_atom(0x8, 0x3)
        if self.chip_mode == 'fullband':
            self.write_atom(0x311, 0x4)
            self.Jesd204B_M = 2
            self.Jesd204B_L = 8
        elif self.chip_mode == 'OneDDCmode':
            ddc_num = 1
            if self.inputMode == 'Real':
                self.Jesd204B_M = 1
                self.write_atom(0x200, 0x21)
            elif self.inputMode == 'Complex':
                self.Jesd204B_M = 2
                self.write_atom(0x200, 0x1)
        elif self.chip_mode == 'TwoDDCmode':
            ddc_num = 2
            if self.inputMode == 'Real':
                self.Jesd204B_M = 2
                self.write_atom(0x200, 0x22)
            else:
                self.Jesd204B_M = 4
                self.write_atom(0x200, 0x2)
        elif self.chip_mode == 'FourDDCmode':
            ddc_num = 4
            if self.inputMode == 'Real':
                self.Jesd204B_M = 4
                self.write_atom(0x200, 0x23)
            else:
                self.Jesd204B_M = 8
                self.write_atom(0x200, 0x3)
        if self.chip_mode != 'fullband':
            if 'mixerMode' not in dir(self):
                self.mixerMode = 'real'
            if self.mixerMode == 'real':
                mixer_mode = 0
            else:
                mixer_mode = 1
            if 'gainMode' not in dir(self):
                self.gainMode = '6dB'
            if self.gainMode == '0dB':
                gain_mode = 0
            else:
                gain_mode = 1
            if 'freqMode' not in dir(self):
                self.freqMode = '0 Hz IF mode'
            if self.freqMode == 'Variable IF mode':
                freq_mode = 0
            elif self.freqMode == '0 Hz IF mode':
                freq_mode = 1
            elif self.freqMode == 'fs Hz IF mode':
                freq_mode = 2
            elif self.freqMode == 'Test mode':
                freq_mode = 3
            if 'outputMode' not in dir(self):
                self.outputMode = 'complex'
            if self.outputMode == 'complex':
                complex2real = 0
            else:
                complex2real = 1
            dcm_rate_extend = 0
            if self.ddc_dcm == 1:
                chip_dcm = 0b0000
                if complex2real == 1:
                    dcm_rate = 3
            elif self.ddc_dcm == 2:
                chip_dcm = 0b0001
                if complex2real == 1:
                    dcm_rate = 0
                else:
                    dcm_rate = 3
            elif self.ddc_dcm == 3:
                chip_dcm = 0b1000
                if complex2real == 1:
                    dcm_rate = 4
                else:
                    dcm_rate = 7
                    dcm_rate_extend = 7
            elif self.ddc_dcm == 4:
                chip_dcm = 0b0010
                if complex2real == 1:
                    dcm_rate = 1
                else:
                    dcm_rate = 0
            elif self.ddc_dcm == 5:
                chip_dcm = 0b0101
                if complex2real == 1:
                    dcm_rate = 7
                    dcm_rate_extend = 2
            elif self.ddc_dcm == 6:
                chip_dcm = 0b1001
                if complex2real == 1:
                    dcm_rate = 5
                else:
                    dcm_rate = 4
            elif self.ddc_dcm == 8:
                chip_dcm = 0b0011
                if complex2real == 1:
                    dcm_rate = 2
                else:
                    dcm_rate = 1
            elif self.ddc_dcm == 10:
                chip_dcm = 0b0110
                if complex2real == 1:
                    dcm_rate = 7
                    dcm_rate_extend = 3
                else:
                    dcm_rate = 7
                    dcm_rate_extend = 2
            elif self.ddc_dcm == 12:
                chip_dcm = 0b1010
                if complex2real == 1:
                    dcm_rate = 6
                else:
                    dcm_rate = 5
            elif self.ddc_dcm == 15:
                chip_dcm = 0b0111
                if complex2real == 0:
                    dcm_rate = 7
                    dcm_rate_extend = 8
            elif self.ddc_dcm == 16:
                chip_dcm = 0b0100
                if complex2real == 0:
                    dcm_rate = 2
            elif self.ddc_dcm == 20:
                chip_dcm = 0b1101
                if complex2real == 1:
                    dcm_rate = 7
                    dcm_rate_extend = 4
                else:
                    dcm_rate = 7
                    dcm_rate_extend = 3
            elif self.ddc_dcm == 24:
                chip_dcm = 0b1011
                if complex2real == 1:
                    dcm_rate = 7
                    dcm_rate_extend = 0
                else:
                    dcm_rate = 6
            elif self.ddc_dcm == 30:
                chip_dcm = 0b1110
                if complex2real == 0:
                    dcm_rate = 7
                    dcm_rate_extend = 9
            elif self.ddc_dcm == 40:
                chip_dcm = 0b1111
                if complex2real == 0:
                    dcm_rate = 7
                    dcm_rate_extend = 4
            elif self.ddc_dcm == 48:
                chip_dcm = 0b1100
                if complex2real == 0:
                    dcm_rate = 7
                    dcm_rate_extend = 0
            self.write_atom(0x201, chip_dcm)
            self.write_atom(0x300, 0x3)
            for idx in range(ddc_num):
                self.write_atom(0x310 + 0x20 * idx,
                                mixer_mode * 128 + gain_mode * 64 + freq_mode * 16 + complex2real * 8 + dcm_rate)
                if self.inputMode == 'real':
                    self.write_atom(0x311 + 0x20 * idx, dcm_rate_extend * 16 + 4)
                else:
                    self.write_atom(0x311 + 0x20 * idx, dcm_rate_extend * 16 + 4)
                if self.freqMode == 'Test mode' or self.freqMode == 'Variable IF mode':
                    if 'ncoFTW' not in dir(self):
                        self.ncoFTW = 400e6
                    nco_freq = '{:0>12x}'.format(int(2 ** 48 * self.ncoFTW / self.fs))
                    self.write_atom(0x316 + 0x20 * idx, int(nco_freq[10:], 16))
                    self.write_atom(0x317 + 0x20 * idx, int(nco_freq[8:10], 16))
                    self.write_atom(0x318 + 0x20 * idx, int(nco_freq[6:8], 16))
                    self.write_atom(0x319 + 0x20 * idx, int(nco_freq[4:6], 16))
                    self.write_atom(0x31a + 0x20 * idx, int(nco_freq[2:4], 16))
                    self.write_atom(0x31b + 0x20 * idx, int(nco_freq[:2], 16))
            self.write_atom(0xf2d, 0x10)

    def jesd204b_config(self):
        scr_reg = 0x80
        self.write_atom(0x58b, scr_reg + self.Jesd204B_L - 1)
        self.write_atom(0x58c, self.Jesd204B_F - 1)
        if 'Jesd204B_K' not in dir(self):
            self.Jesd204B_K = 32
        self.write_atom(0x58d, self.Jesd204B_K - 1)
        self.write_atom(0x58e, self.Jesd204B_M - 1)
        self.write_atom(0x58f, self.Jesd204B_N - 1)
        if 'Jesd204B_Ntotal' not in dir(self):
            self.Jesd204B_Ntotal = self.Jesd204B_N
        if 'Jesd204B_subclass' not in dir(self):
            self.Jesd204B_subclass = 1
        self.write_atom(0x590, self.Jesd204B_subclass * 32 + self.Jesd204B_Ntotal - 1)
        if 'Jesd204B_S' not in dir(self):
            self.Jesd204B_S = int(8 * self.Jesd204B_F * self.Jesd204B_L / self.Jesd204B_M / self.Jesd204B_N)
        self.write_atom(0x591, self.Jesd204B_S - 1)
        ##lane cross begin
        self.write_atom(0x5b2, 0x45)
        self.write_atom(0x5b3, 0x76)
        self.write_atom(0x5b5, 0x3)
        self.write_atom(0x5b6, 0x12)
        ##lane cross end
        mframe_len = '{:0>3x}'.format(self.Jesd204B_F * self.Jesd204B_K)
        self.write_atom(0x5e4, int(mframe_len[1:], 16))
        self.write_atom(0x5e5, int(mframe_len[0], 16))
        self.write_atom(0x571, 0x5)
        self.write_atom(0xf0e, 0x40)
        self.write_atom(0xf0e, 0xf0)

    def calib_config(self):
        self.write_atom(0x800, 0x1)
        self.write_atom(0x800 + 0x10, 0x1)  ##dnc_en
        self.write_atom(0x800 + 0x36f, 0x0)  ##gec_coeff_protect
        self.write_atom(0x800 + 0x350, 0x1)  ##gec_en
        self.write_atom(0x800 + 0x3a3, 0x0)  ##tios_refch
        if 'tios_accnum_power2' not in dir(self):
            self.tios_accnum_power2 = 0x14
        self.write_atom(0x800 + 0x3a4, self.tios_accnum_power2)
        self.write_atom(0x800 + 0x3a0, 0x1)  ##tios_en
        self.write_atom(0x800 + 0x3c7, 0x0)  ##tigain_round
        self.write_atom(0x800 + 0x3c0, 0x1)  ##tigain_en
        if 'tiskew_accnum_power2' not in dir(self):
            self.tiskew_accnum_power2 = 0x18
        self.write_atom(0x800 + 0x3f3, self.tiskew_accnum_power2)
        if 'tiskew_code_step' not in dir(self):
            self.tiskew_code_step = 1
        self.write_atom(0x800 + 0x3f8, self.tiskew_code_step)
        self.write_atom(0x800 + 0x3fa, 0x1)  ##tiskew_auto_dir
        self.write_atom(0x800 + 0x3f0, 0x1)  ##tiskew_en
        if 'high_th_dBFs' not in dir(self):
            self.high_th_dBFs = -0.9
        if 'low_th_dBFs' not in dir(self):
            self.low_th_dBFs = -20
        ##gec_overrange config
        overrange_high_th = '{:0>4x}'.format(int(10 ** (self.high_th_dBFs / 20) * 4096))
        overrange_low_th = '{:0>4x}'.format(int(10 ** (self.low_th_dBFs / 20) * 4096))
        self.write_atom(0x800 + 0x445, int(overrange_high_th[2:], 16))
        self.write_atom(0x800 + 0x446, int(overrange_high_th[:2], 16))
        self.write_atom(0x800 + 0x447, int(overrange_low_th[2:], 16))
        self.write_atom(0x800 + 0x448, int(overrange_low_th[:2], 16))
        self.write_atom(0x800 + 0x449, 0x1)  ##high_vol_th
        self.write_atom(0x800 + 0x44a, 0xff)  ##low_vol_th
        self.write_atom(0x800 + 0x444, 0x1)  ##overrange_en
        ##tios_overrange config
        self.write_atom(0x800 + 0x421, int(overrange_high_th[2:], 16))
        self.write_atom(0x800 + 0x422, int(overrange_high_th[:2], 16))
        self.write_atom(0x800 + 0x425, 0x1)
        self.write_atom(0x800 + 0x426, 0xff)
        self.write_atom(0x800 + 0x420, 0x1)  ##overrange_en
        ##tigain_overrange config
        self.write_atom(0x800 + 0x457, int(overrange_high_th[2:], 16))
        self.write_atom(0x800 + 0x458, int(overrange_high_th[:2], 16))
        self.write_atom(0x800 + 0x459, int(overrange_low_th[2:], 16))
        self.write_atom(0x800 + 0x45a, int(overrange_low_th[:2], 16))
        self.write_atom(0x800 + 0x45b, 0x1)  ##high_vol_th
        self.write_atom(0x800 + 0x45c, 0xff)  ##low_vol_th
        self.write_atom(0x800 + 0x456, 0x1)  ##overrange_en
        ##tiskew_overrange_config
        self.write_atom(0x800 + 0x460, int(overrange_high_th[2:], 16))
        self.write_atom(0x800 + 0x461, int(overrange_high_th[:2], 16))
        self.write_atom(0x800 + 0x462, int(overrange_low_th[2:], 16))
        self.write_atom(0x800 + 0x463, int(overrange_low_th[:2], 16))
        self.write_atom(0x800 + 0x464, 0x1)  ##high_vol_th
        self.write_atom(0x800 + 0x465, 0xff)  ##low_vol_th
        self.write_atom(0x800 + 0x45f, 0x1)  ##overrange_en

        self.write_atom(0x801, 0x1)
