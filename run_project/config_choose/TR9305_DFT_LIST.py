# -*- coding: utf-8 -*-

from run_project.config_choose import *
import xlwt
import xlrd
import json
import time

class DFT_XLS_LIST:
    tblList = {}   #'cat'归属于哪个页签  'reg'计算出来的值或寄存器读出值 'type'函数还是计算  可选项：'depend' 依赖值  'dependVal'被依赖数据真值 'valLog' 输出值打印解释 'mask'掩码信息
    lineIdx = 0
    sheetColIdx = 0
    funcPara = []
    funcParaNum = 0
    regTblNeedcon = True
    regTblIdx = 0
    def __init__(self, regInfo,reg_map_file):
        self.regInfo = regInfo
        super(DFT_XLS_LIST, self).__init__()
        self.regRange = json.load(open(reg_map_file, 'r'))
    def PrintSheetLog(self, sheetW, val, idx, addLine):
        sheetW.write(self.lineIdx, idx, val)
        if addLine:
            self.lineIdx = self.lineIdx + 1
    def GetFuncParaList(self, sheet, line, maxNum):
        self.funcParaNum = 0
        self.funcPara.clear()
        nullIdx = 0
        for i in range(self.sheetColIdx, maxNum):
            val = sheet.cell_value(line, i)
            if val != '':
                self.funcPara.append(self.tblList[val]['reg'])
                self.funcParaNum = self.funcParaNum + 1
            else:
                nullIdx = i
                break
        val = sheet.cell_value(line, nullIdx + 1)
        if val == '':
            self.sheetColIdx = 0
        else:
            self.sheetColIdx = nullIdx + 1
    def GetAddr(self, addr):
        ret = {}
        val = 0
        for i in range(len(self.regRange)):
            if addr >= int(self.regRange[i]['rangestart'], 16) and addr <= int(self.regRange[i]['rangeEnd'], 16):
                ret['tbl'] = self.regRange[i]['file'][self.regTblIdx]
                ret['base'] = int(self.regRange[i]['base'], 16)
                if self.regTblIdx == len(self.regRange[i]['file']) - 1:
                    self.regTblNeedcon = False
                break
        if 'tbl' in ret:
            if (addr - ret['base']) < len(self.regInfo[ret['tbl']]):
                val = self.regInfo[ret['tbl']][addr - ret['base']]['val']
            else:
                print("addr 0x{:0>4x} out range".format(addr))
        else:
            print("find addr 0x{:0>4x} error".format(addr))
        return val
        
    def GetRegVal(self, sheet, line, maxNum):
        bitMaskVaild = [0x1, 0x3, 0x7, 0xf, 0x1f, 0x3f, 0x7f, 0xff]
        nullIdx = 0
        start = self.sheetColIdx
        val = 0
        regVal = 0
        startBit = 0
        endBit = 0
        for i in range(self.sheetColIdx, maxNum):
            sheetVal = sheet.cell_value(line, i)
            if sheetVal != '':
                regFlag = (i - start) % 2
                if regFlag == 0:
                    regAddrVal = int(sheetVal, 16)
                    regVal = self.GetAddr(regAddrVal)
                else:
                    mIdx = sheetVal.find(':')
                    endBit = int(sheetVal[ : mIdx])
                    startBit = int(sheetVal[mIdx + 1 :])
                    byteVal = (regVal >> startBit) & bitMaskVaild[endBit - startBit]
                    val = (val << (endBit - startBit + 1)) + byteVal
            else:
                nullIdx = i
                break
        sheetVal = sheet.cell_value(line, nullIdx + 1)
        if sheetVal == '':
            self.sheetColIdx = 0
        else:
            self.sheetColIdx = nullIdx + 1
        return val
    def GenParaVal(self, sheet, line, maxNum, name):
        valLog = {}
        maskLog = {}
        cntNull = 0
        for i in range(self.sheetColIdx, maxNum):
            sheetVal = sheet.cell_value(line, i)
            sheetVal = sheetVal.replace('\n', '').replace('\r', '')
            if 'val' in sheetVal:
                mIdx0 = sheetVal.find(':')
                mIdx1 = sheetVal[mIdx0 + 1: ].find(':') + mIdx0 + 1
                valLog['val'] = int(sheetVal[mIdx0 + 1: mIdx1])
                valLog['log'] = sheetVal[mIdx1 + 1: ]
                if 'valLog' in self.tblList[name]:
                    pass
                else:
                    self.tblList[name]['valLog'] = []
                self.tblList[name]['valLog'].append(valLog.copy())
                
            elif 'depend' in sheetVal:
                mIdx0 = sheetVal.find(':')
                dependVal = int(sheetVal[mIdx0 + 1: ])
                if dependVal == self.tblList[name]['reg']:
                    self.tblList[name]['dependVal'] = 1
                else:
                    self.tblList[name]['dependVal'] = 0
            elif 'mask' in sheetVal:
                maskLog.clear()
                mIdx0 = sheetVal.find(':')
                mIdx1 = sheetVal[mIdx0 + 1: ].find(':') + mIdx0 + 1
                mIdx2 = sheetVal[mIdx1 + 1: ].find(':') + mIdx1 + 1
                mIdx3 = sheetVal[mIdx2 + 1: ].find(';') + mIdx2 + 1
                maskLog['endBit'] = int(sheetVal[mIdx1 + 1: mIdx2])
                maskLog['startBit'] = int(sheetVal[mIdx0 + 1: mIdx1])
                maskLog['logVal'] = sheetVal[mIdx2 + 1: mIdx3]
                maskLog['val'] = []
                maskLogVal = {}
                sheetValN = sheetVal[mIdx3 + 1 :]
                cnt = 1 << (maskLog['endBit'] - maskLog['startBit'] + 1)
                for j in range(cnt):
                    maskLogVal.clear()
                    mIdxN = sheetValN.find(':')
                    maskLogVal['val'] = int(sheetValN[:mIdxN])
                    mIdxM = sheetValN[mIdxN + 1 :].find(';')
                    if mIdxM == -1:
                        maskLogVal['log'] = sheetValN[mIdxN + 1 :]
                        maskLog['val'].append(maskLogVal.copy())
                        break
                    else:
                        maskLogVal['log'] = sheetValN[mIdxN + 1 : mIdxM + mIdxN + 1]
                        maskLog['val'].append(maskLogVal.copy())
                        sheetValN = sheetValN[mIdxM + 1 + mIdxN + 1: ]
                if 'mask' in self.tblList[name]:
                    cntNull = cntNull + 1
                    pass
                else:
                    self.tblList[name]['mask'] = []
                self.tblList[name]['mask'].append(maskLog.copy())
            elif 'tail' in sheetVal:
                mIdx0 = sheetVal.find(':')
                tailVal = sheetVal[mIdx0 + 1: ]
                self.tblList[name]['tail'] = tailVal
            elif 'p:' in sheetVal:
                mIdx0 = sheetVal.find('p:')
                self.tblList[name]['p'] = sheetVal[mIdx0 + 2: ]
            elif 'hide:' in sheetVal:
                self.tblList[name]['hide'] = True
            elif 'operation:' in sheetVal:
                mIdx0 = sheetVal.find(':')
                mIdx1 = sheetVal[mIdx0 + 1: ].find(':') + mIdx0 + 1
                operation = sheetVal[mIdx0 + 1: mIdx1]
                operationVal = int(sheetVal[mIdx1 + 1:])
                if operation == 'add':
                    self.tblList[name]['hide'] = self.tblList[name]['hide'] + operationVal
                elif operation == 'sub':
                    self.tblList[name]['hide'] = self.tblList[name]['hide'] - operationVal
                elif operation == 'mul':
                    self.tblList[name]['hide'] = self.tblList[name]['hide'] * operationVal
                elif operation == 'div':
                    self.tblList[name]['hide'] = self.tblList[name]['hide'] / operationVal
                else:
                    print("sheet val err  " + sheetVal)
            else:                
                if sheetVal == '':
                    break
                else:
                    print("sheet val err  " + sheetVal)
    def PrintLineInfo(self, sheetW, name):
        bitMaskVaild = [0x1, 0x3, 0x7, 0xf, 0x1f, 0x3f, 0x7f, 0xff]
        if 'hide' in self.tblList[name]:
            return
        self.PrintSheetLog(sheetW, self.tblList[name]['logCol'], 0, False)
        if 'p' in self.tblList[name]:
            self.PrintSheetLog(sheetW, self.tblList[name]['reg'], 1, False)
        else:
            self.PrintSheetLog(sheetW, "0x{:x}".format(self.tblList[name]['reg']), 1, False)
        idx = 2
        if 'tail' in self.tblList[name]:
            self.PrintSheetLog(sheetW, self.tblList[name]['tail'], idx, False)
            idx = idx + 1
        if 'valLog' in self.tblList[name]:
            for valLog in self.tblList[name]['valLog']:
                if valLog['val'] == self.tblList[name]['reg']:
                    self.PrintSheetLog(sheetW, valLog['log'], idx, False)
                    idx = idx + 1
                    break
        if 'mask' in self.tblList[name]:
            for maskLog in self.tblList[name]['mask']:
                maskVal = self.tblList[name]['reg']
                maskVal = maskVal >> maskLog['startBit']
                maskLen = maskLog['endBit'] - maskLog['startBit']
                maskVal = maskVal & bitMaskVaild[maskLen]
                if len(maskLog['val']) == 0:
                    self.PrintSheetLog(sheetW, maskLog['logVal'] + str(maskVal), idx, False)
                    idx = idx + 1
                else:
                    findFlag = False
                    for maskLogVal in maskLog['val']:
                        if maskVal == maskLogVal['val']:
                            self.PrintSheetLog(sheetW, str(maskVal) + ' : ' + maskLog['logVal'] + maskLogVal['log'], idx, False)
                            idx = idx + 1
                            findFlag = True
                            break
                    if not findFlag:
                        self.PrintSheetLog(sheetW, maskLog['logVal'] +  str(maskVal), idx, False)
                        idx = idx + 1
        self.PrintSheetLog(sheetW, '', idx, True)
    def genCmd(self, sheet, sn, sheetW):
        rowsNum = sheet.nrows
        colsNum = sheet.ncols
        for r in range(2, rowsNum):
            logCol0 = sheet.cell_value(r, 0)
            if logCol0 == '':
                self.PrintSheetLog(sheetW, '', 0, True)
                continue
            name = sheet.cell_value(r, 1)
            depend = sheet.cell_value(r, 2)
            if depend != '':
                if depend in self.tblList:
                    if 'dependVal' in self.tblList[depend]:
                        if self.tblList[depend]['dependVal'] == 1:
                            self.tblList[name] = {}
                            self.tblList[name]['depend'] = depend
                        else:
                            continue
                    else:
                        print("can not find depend {}".format(depend))
                        continue
                else:
                    print("can not find depend {}".format(depend))
                    continue
            else:
                self.tblList[name] = {}
            self.tblList[name]['cat'] = sn
            regfirst = sheet.cell_value(r, 3)
            if regfirst == 'function':
                self.tblList[name]['type'] = 'f'
                funcName = sheet.cell_value(r, 4)
                moduleName = __import__("TR9305_DFT_FUNC")
                calledFunc = getattr(moduleName, funcName)
                self.sheetColIdx = 5
                self.GetFuncParaList(sheet, r, colsNum)
                self.tblList[name]['reg'] = calledFunc(self.funcPara)
            else:
                self.tblList[name]['type'] = 'r'
                self.sheetColIdx = 3
                self.tblList[name]['reg'] = self.GetRegVal(sheet, r, colsNum)
            if self.sheetColIdx != 0:
                self.GenParaVal(sheet, r, colsNum, name)
            self.tblList[name]['logCol'] = logCol0
            self.PrintLineInfo(sheetW, name)
    def readTblList(self, listName):
        bookW = xlwt.Workbook(encoding='utf-8', style_compression=0)
        workbook = xlrd.open_workbook(listName)
        sheets = workbook.sheets()
        sheetNames = workbook.sheet_names()        
        sheetW = bookW.add_sheet('Info', cell_overwrite_ok=True)
        for sn in sheetNames:            
            indx = sheetNames.index(sn)
            for i in range(4):
                testVal = sheets[indx].cell_value(0, i)
                self.regTblIdx = i
                if testVal == '':
                    self.PrintSheetLog(sheetW, sn + ' start', 0, True)
                else:
                    self.PrintSheetLog(sheetW, testVal + ' ' + sn + ' start', 0, True)
                ret = self.genCmd(sheets[indx], sn, sheetW)
                self.PrintSheetLog(sheetW, sn + ' end', 0, True)
                self.PrintSheetLog(sheetW, '', 0, True)
                self.PrintSheetLog(sheetW, '', 0, True)
                if sheets[indx].cell_value(0, 1) == '':
                    break
                else:
                    if sheets[indx].cell_value(0, i + 1) == '':
                        break
        savepath = './dft_list_' + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) + '.xls'
        bookW.save(savepath)