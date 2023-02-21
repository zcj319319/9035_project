# -*- coding: utf-8 -*-
import json
import os
import sys
from binascii import hexlify

import xlwt
import time

from run_project.config_choose import TR9305_DFT_LIST


# 生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class TR9305_DFT:
    defaultVal = {}
    ex = {}
    real = {}
    sel = 2
    spi = None

    def __init__(self, spi):
        self.spi = spi
        self.sel = 2
        tblNameList = ['CALIB_ALG_PARA', 'CALIB_TOP_PARA', 'CALIB_ALG_PARA', 'CALIB_TOP_PARA', 'RFADC_ANA_PARA',
                       'RFADC_TOP_PARA']
        tblNameOut = ['CALIB_ALG_PARA_I', 'CALIB_TOP_PARA_I', 'CALIB_ALG_PARA_Q', 'CALIB_TOP_PARA_Q', 'RFADC_ANA_PARA',
                      'RFADC_TOP_PARA']
        tblNamecnt = 0
        for regName in tblNameList:
            filename = resource_path(os.path.join("res",regName + '.JSON'))
            defaultVal = json.load(open(filename, 'r'))
            cnt = 0
            regNameTmp = tblNameOut[tblNamecnt]
            self.defaultVal[regNameTmp] = []
            regTmp = {}
            for reginfo in defaultVal:
                if reginfo['offsetAddr'] > cnt:
                    for i in range(reginfo['offsetAddr'] - cnt):
                        regTmp['attri'] = 'E'
                        regTmp['val'] = 0
                        self.defaultVal[regNameTmp].append(regTmp.copy())
                        cnt = cnt + 1
                regTmp['attri'] = reginfo['attribute']
                regTmp['val'] = reginfo['default']
                self.defaultVal[regNameTmp].append(regTmp.copy())
                cnt = cnt + 1
            tblNamecnt = tblNamecnt + 1
        tblNamecnt = 0
        for regName in tblNameList:
            filename = resource_path(os.path.join("res", regName + '.JSON'))
            defaultVal = json.load(open(filename, 'r'))
            cnt = 0
            regNameTmp = tblNameOut[tblNamecnt]
            self.ex[regNameTmp] = []
            regTmp = {}
            for reginfo in defaultVal:
                if reginfo['offsetAddr'] > cnt:
                    for i in range(reginfo['offsetAddr'] - cnt):
                        regTmp['attri'] = 'E'
                        regTmp['val'] = 0
                        self.ex[regNameTmp].append(regTmp.copy())
                        cnt = cnt + 1
                regTmp['attri'] = reginfo['attribute']
                regTmp['val'] = reginfo['default']
                self.ex[regNameTmp].append(regTmp.copy())
                cnt = cnt + 1
            tblNamecnt = tblNamecnt + 1
        tblNamecnt = 0
        for regName in tblNameList:
            filename = resource_path(os.path.join("res", regName + '.JSON'))
            defaultVal = json.load(open(filename, 'r'))
            cnt = 0
            regNameTmp = tblNameOut[tblNamecnt]
            self.real[regNameTmp] = []
            regTmp = {}
            for reginfo in defaultVal:
                if reginfo['offsetAddr'] > cnt:
                    for i in range(reginfo['offsetAddr'] - cnt):
                        regTmp['attri'] = 'E'
                        regTmp['val'] = 0
                        self.real[regNameTmp].append(regTmp.copy())
                        cnt = cnt + 1
                regTmp['attri'] = reginfo['attribute']
                regTmp['val'] = reginfo['default']
                self.real[regNameTmp].append(regTmp.copy())
                cnt = cnt + 1
            tblNamecnt = tblNamecnt + 1
        self.regRange = [{'tbl': 'CALIB_ALG_PARA', 'rangestart': 0x800, 'rangeEnd': 0xcff, 'base': 0x800},
                         {'tbl': 'CALIB_TOP_PARA', 'rangestart': 0x700, 'rangeEnd': 0x7ff, 'base': 0x800},
                         {'tbl': 'RFADC_ANA_PARA', 'rangestart': 0x1000, 'rangeEnd': 0x1fff, 'base': 0x1000},
                         {'tbl': 'RFADC_TOP_PARA', 'rangestart': 0x0, 'rangeEnd': 0x6ff, 'base': 0x0},
                         {'tbl': 'RFADC_TOP_PARA', 'rangestart': 0xD00, 'rangeEnd': 0xFFF, 'base': 0x0}
                         ]

    def findTbl(self, addr, val):
        ret = {}
        for tbl in self.regRange:
            if (addr >= tbl['rangestart']) and (addr <= tbl['rangeEnd']):
                ret['tbl'] = tbl['tbl']
                ret['base'] = tbl['base']
                return ret
        print('find addr 0x{:0>4x} tbl fail\n'.format(addr))
        return ret

    def write2ExTble(self, tblinfo, addr, val):
        offset = addr - tblinfo['base']
        if offset >= len(self.ex[tblinfo['tbl']]):
            print('addr 0x{:0>4x} can not reach err\n'.format(addr))
            return
        if self.ex[tblinfo['tbl']][offset]['attri'] == 'E':
            print('addr 0x{:0>4x} can not reach\n'.format(addr))
            pass
        elif self.ex[tblinfo['tbl']][offset]['attri'] == 'RO':
            print('addr 0x{:0>4x} is read only, can not write\n'.format(addr))
            pass
        else:
            self.ex[tblinfo['tbl']][offset]['val'] = val

    def write2Ex(self, addr, val):
        tblinfo = self.findTbl(addr, val)
        if 'tbl' in tblinfo:
            if (tblinfo['tbl'] == 'CALIB_ALG_PARA') or (tblinfo['tbl'] == 'CALIB_TOP_PARA'):
                if self.sel == 0:
                    tblTmp = tblinfo.copy()
                    tblTmp['tbl'] = tblinfo['tbl'] + '_I'
                    self.write2ExTble(tblTmp, addr, val)
                elif self.sel == 1:
                    tblTmp = tblinfo.copy()
                    tblTmp['tbl'] = tblinfo['tbl'] + '_Q'
                    self.write2ExTble(tblTmp, addr, val)
                elif self.sel == 2:
                    tblTmp = tblinfo.copy()
                    tblTmp['tbl'] = tblinfo['tbl'] + '_I'
                    self.write2ExTble(tblTmp, addr, val)
                    tblTmp['tbl'] = tblinfo['tbl'] + '_Q'
                    self.write2ExTble(tblTmp, addr, val)
            else:
                self.write2ExTble(tblinfo, addr, val)
        else:
            pass

    def TR9305_DFT_LOG(self, addr, val):
        if addr == 8:
            if val == 1:
                self.sel = 0
            elif val == 2:
                self.sel = 1
            else:
                self.sel = 2
        self.write2Ex(addr, val)

    def dumpChipVal(self):
        tblNameList = ['CALIB_ALG_PARA_I', 'CALIB_TOP_PARA_I', 'CALIB_ALG_PARA_Q', 'CALIB_TOP_PARA_Q', 'RFADC_ANA_PARA',
                       'RFADC_TOP_PARA']
        writeVal = [1, 1, 2, 2, 3, 3]
        baseAddr = [0x800, 0x700, 0x800, 0x700, 0x1000, 0x0]
        default = self.spi.read_atom(0x8)
        for j in range(len(writeVal)):
            self.spi.write_atom(0x8, writeVal[j])
            baseAddrTmp = baseAddr[j]
            tblName = tblNameList[j]
            cnt = 0
            for i in range(len(self.ex[tblName])):
                if self.ex[tblName][i]['attri'] == 'E':
                    self.real[tblName][cnt]['val'] = 0
                else:
                    val = self.spi.read_atom(baseAddrTmp + i)
                    if val[0] != 0:
                        self.real[tblName][cnt]['val'] = int(hexlify(val[0]).decode(), 16)
                    else:
                        self.real[tblName][cnt]['val'] = 0
                cnt = cnt + 1
        # self.spi.write_atom(0x8, default)

    def printDumpInfo(self):
        tblNameList = ['CALIB_ALG_PARA_I', 'CALIB_TOP_PARA_I', 'CALIB_ALG_PARA_Q', 'CALIB_TOP_PARA_Q', 'RFADC_ANA_PARA',
                       'RFADC_TOP_PARA']
        regbase = [0x800, 0x700, 0x800, 0x700, 0x1000, 0x0]
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        regbaseIdx = 0
        styleerr = xlwt.easyxf('pattern: pattern solid, fore_colour red; font: bold on')
        style = xlwt.easyxf('pattern: pattern solid, fore_colour green; font: bold on')
        for i in tblNameList:
            sheet = book.add_sheet(i, cell_overwrite_ok=True)
            sheet.write(0, 0, 'baseaddr')
            sheet.write(0, 1, 'offset')
            sheet.write(0, 2, 'addr')
            sheet.write(0, 3, 'default')
            sheet.write(0, 4, 'ex')
            sheet.write(0, 5, 'real')
            sheet.write(0, 6, 'cmp:ex&real')
            sheet.write(0, 6, 'cmp:default&real')
            addrCnt = 0
            colCnt = 1
            for j in self.defaultVal[i]:
                addrCnt = addrCnt + 1
                if j['attri'] == 'E':
                    continue
                sheet.write(colCnt, 0, '0x{:0>4x}'.format(regbase[regbaseIdx]))
                sheet.write(colCnt, 1, '0x{:0>4x}'.format(addrCnt - 1))
                sheet.write(colCnt, 2, '0x{:0>4x}'.format(regbase[regbaseIdx] + addrCnt - 1))
                sheet.write(colCnt, 3, '0x{:0>2x}'.format(j['val']))
                sheet.write(colCnt, 4, '0x{:0>2x}'.format(self.ex[i][addrCnt - 1]['val']))
                if len(self.real[i]) == 0:
                    sheet.write(colCnt, 5, '0x{:0>2x}'.format(0))
                    sheet.write(colCnt, 6, 'E', styleerr)
                    sheet.write(colCnt, 7, 'E', styleerr)
                else:
                    sheet.write(colCnt, 5, '0x{:0>2x}'.format(self.real[i][addrCnt - 1]['val']))
                    if self.ex[i][addrCnt - 1]['val'] == self.real[i][addrCnt - 1]['val']:
                        sheet.write(colCnt, 6, 'P', style)
                    else:
                        sheet.write(colCnt, 6, 'E', styleerr)
                    if j['val'] == self.real[i][addrCnt - 1]['val']:
                        sheet.write(colCnt, 7, 'P', style)
                    else:
                        sheet.write(colCnt, 7, 'E', styleerr)
                colCnt = colCnt + 1
            regbaseIdx = regbaseIdx + 1

        savepath = './dft_' + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) + '.xls'
        book.save(savepath)
        reg_map_file = resource_path(os.path.join("res",'reg_map.json'))
        dftList = TR9305_DFT_LIST.DFT_XLS_LIST(self.real,reg_map_file)
        filename = resource_path(os.path.join("res", 'dft_list.xls'))
        dftList.readTblList(filename)
