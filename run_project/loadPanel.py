#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Time    : 2022/9/29 15:11
Author  : zhuchunjin
Email   : chunjin.zhu@taurentech.net
File    : loadPanel.py
Software: PyCharm
'''
import os
import re
import threading
import time
from binascii import hexlify

import xlrd
import xlwt

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from run_project.config_choose import TR9305_CFG
from run_project.config_choose.spi_interface import LoadMainWindow, spi_interface

from run_project.mainDialog1 import MainDialog1
from ui_file import logo_rc
from ui_file import status_rc
from ui_file import struc_rc


class LoadingPanel(LoadMainWindow):
    def __init__(self):
        super().__init__()
        self.sheet_sel_lst = None
        self.running_case = None
        self.reg_struct = None
        self.spi_obj = None
        self.config_transfer = {}
        self.init_param()
        self.run_project_button.clicked.connect(self.run_btn_project)
        self.clear_log_btn.clicked.connect(self.clear_log_content)
        self.view_all_log_btn.clicked.connect(self.get_log_content)
        self.init_button.clicked.connect(self.load_test_seq)
        self.mem_rd_button.clicked.connect(self.mem_read)
        self.read_button.clicked.connect(self.read_addr)
        self.write_button.clicked.connect(self.write_addr)
        self.pushButton.clicked.connect(self.spi_update_command)
        self.release_btn.clicked.connect(self.spi_release_command)
        self.DFT_Btn.clicked.connect(self.dft_wei_test)

    def init_param(self):
        self.lineEdit.setText('1.25')
        self.lineEdit_2.setText('8')
        self.communicate_mode_comboBox.setCurrentIndex(0)
        self.samplingFreqHz_lineEdit.setText("3e9")
        self.lanerate_lineEdit.setText("15e9")
        self.chip_mode_comboBox.setCurrentIndex(0)
        self.mixerMode_comboBox.setCurrentIndex(1)
        self.ddc_dcm_lineEdit.setText("2")
        self.inputMode_comboBox.setCurrentIndex(1)
        self.outputMode_comboBox.setCurrentIndex(1)
        self.ffetap_comboBox.setCurrentIndex(3)
        self.gainMode_comboBox.setCurrentIndex(1)
        self.freqMode_comboBox.setCurrentIndex(1)
        self.ncoFTW_lineEdit.setText("400e6")
        self.Jesd204B_K_lineEdit.setText("32")
        self.Jesd204B_M_lineEdit.setText("2")
        self.Jesd204B_N_lineEdit.setText("16")
        self.Jesd204B_F_lineEdit.setText("2")
        self.Jesd204B_L_lineEdit.setText("4")
        self.Jesd204B_subclass_lineEdit.setText("1")
        self.tios_accnum_power2_lineEdit.setText("0x14")
        self.tiskew_accnum_power2_lineEdit.setText("0x18")
        self.tiskew_code_step_lineEdit.setText("1")
        self.high_th_dBFs_lineEdit.setText("-0.9")
        self.low_th_dBFs_lineEdit.setText("-20")
        self.phy_lane0_comboBox.setCurrentIndex(5)
        self.phy_lane1_comboBox.setCurrentIndex(4)
        self.phy_lane2_comboBox.setCurrentIndex(6)
        self.phy_lane3_comboBox.setCurrentIndex(7)
        self.phy_lane4_comboBox.setCurrentIndex(3)
        self.phy_lane5_comboBox.setCurrentIndex(0)
        self.phy_lane6_comboBox.setCurrentIndex(2)
        self.phy_lane7_comboBox.setCurrentIndex(1)

    def check_parm(self):
        self.config_transfer['communicate_mode'] = self.communicate_mode_comboBox.currentText()
        if self.samplingFreqHz_lineEdit.text().strip(" ") == "":
            self.config_transfer['fs'] = 3e9
        else:
            self.config_transfer['fs'] = float(self.samplingFreqHz_lineEdit.text())
        if self.lanerate_lineEdit.text().strip(" ") == "":
            self.config_transfer['lanerate'] = 15e9
        else:
            self.config_transfer['lanerate'] = float(self.lanerate_lineEdit.text())
        self.config_transfer['chip_mode'] = self.chip_mode_comboBox.currentText()
        self.config_transfer['mixerMode'] = self.mixerMode_comboBox.currentText()
        if self.ddc_dcm_lineEdit.text().strip(" ") == "":
            self.config_transfer['ddc_dcm'] = 2
        else:
            self.config_transfer['ddc_dcm'] = int(self.ddc_dcm_lineEdit.text())
        self.config_transfer['inputMode'] = self.inputMode_comboBox.currentText()
        self.config_transfer['outputMode'] = self.outputMode_comboBox.currentText()
        self.config_transfer['ffetap'] = self.ffetap_comboBox.currentText()
        self.config_transfer['gainMode'] = self.gainMode_comboBox.currentText()
        self.config_transfer['freqMode'] = self.freqMode_comboBox.currentText()
        if self.ncoFTW_lineEdit.text().strip(" ") == "":
            self.config_transfer['ncoFTW'] = 400e6
        else:
            self.config_transfer['ncoFTW'] = float(self.ncoFTW_lineEdit.text())
        if self.Jesd204B_K_lineEdit.text().strip(" ") == "":
            self.config_transfer['Jesd204B_K'] = 32
        else:
            self.config_transfer['Jesd204B_K'] = int(self.Jesd204B_K_lineEdit.text())
        if self.Jesd204B_M_lineEdit.text().strip(" ") == "":
            self.config_transfer['Jesd204B_M'] = 2
        else:
            self.config_transfer['Jesd204B_M'] = int(self.Jesd204B_M_lineEdit.text())
        if self.Jesd204B_N_lineEdit.text().strip(" ") == "":
            self.config_transfer['Jesd204B_N'] = 16
        else:
            self.config_transfer['Jesd204B_N'] = int(self.Jesd204B_N_lineEdit.text())
        if self.Jesd204B_F_lineEdit.text().strip(" ") == "":
            self.config_transfer['Jesd204B_F'] = 2
        else:
            self.config_transfer['Jesd204B_F'] = int(self.Jesd204B_F_lineEdit.text())
        if self.Jesd204B_L_lineEdit.text().strip(" ") == "":
            self.config_transfer['Jesd204B_L'] = 4
        else:
            self.config_transfer['Jesd204B_L'] = int(self.Jesd204B_L_lineEdit.text())
        if self.Jesd204B_subclass_lineEdit.text().strip(" ") == "":
            self.config_transfer['Jesd204B_subclass'] = 1
        else:
            self.config_transfer['Jesd204B_subclass'] = int(self.Jesd204B_subclass_lineEdit.text())
        if self.tios_accnum_power2_lineEdit.text().strip(" ") == "":
            self.config_transfer['tios_accnum_power2'] = 0x14
        else:
            self.config_transfer['tios_accnum_power2'] = int(self.tios_accnum_power2_lineEdit.text(),16)
        if self.tiskew_accnum_power2_lineEdit.text().strip(" ") == "":
            self.config_transfer['tiskew_accnum_power2'] = 0x18
        else:
            self.config_transfer['tiskew_accnum_power2'] = int(self.tiskew_accnum_power2_lineEdit.text(),16)
        if self.tiskew_code_step_lineEdit.text().strip(" ") == "":
            self.config_transfer['tiskew_code_step'] = 1
        else:
            self.config_transfer['tiskew_code_step'] = int(self.tiskew_code_step_lineEdit.text())
        if self.high_th_dBFs_lineEdit.text().strip(" ") == "":
            self.config_transfer['high_th_dBFs'] = -0.9
        else:
            self.config_transfer['high_th_dBFs'] = float(self.high_th_dBFs_lineEdit.text())
        if self.low_th_dBFs_lineEdit.text().strip(" ") == "":
            self.config_transfer['low_th_dBFs'] = -20
        else:
            self.config_transfer['low_th_dBFs'] = float(self.low_th_dBFs_lineEdit.text())
        self.config_transfer['phy_lane0'] = int(self.phy_lane0_comboBox.currentText())
        self.config_transfer['phy_lane1'] = int(self.phy_lane1_comboBox.currentText())
        self.config_transfer['phy_lane2'] = int(self.phy_lane2_comboBox.currentText())
        self.config_transfer['phy_lane3'] = int(self.phy_lane3_comboBox.currentText())
        self.config_transfer['phy_lane4'] = int(self.phy_lane4_comboBox.currentText())
        self.config_transfer['phy_lane5'] = int(self.phy_lane5_comboBox.currentText())
        self.config_transfer['phy_lane6'] = int(self.phy_lane6_comboBox.currentText())
        self.config_transfer['phy_lane7'] = int(self.phy_lane7_comboBox.currentText())
        return self.config_transfer

    def run_btn_project(self):
        self.reg_struct = self.check_parm()
        self.spi_obj = spi_interface(self)
        self.running_case = TR9305_CFG.TR9305_CFG(self.spi_obj,**self.reg_struct)
        self.running_case.tr9305_top_config()

    def clear_log_content(self):
        self.log_textBrowser.clear()

    def get_log_content(self):
        file_name, file_type = QFileDialog.getSaveFileName(self, "文件保存", "./", "text file (*.txt)")
        if file_name.strip(" ") != "":
            with open(file_name, 'w') as fileOpen:
                fileOpen.write(self.log_textBrowser.toPlainText())

    def spi_update_command(self):
        self.reg_struct = self.check_parm()
        self.spi_obj = spi_interface(self)
        self.running_case = TR9305_CFG.TR9305_CFG(self.spi_obj,**self.reg_struct)
        self.running_case.tr9305_top_config(True)

    def spi_release_command(self):
        try:
            self.spi_obj.spi_release()
            self.reg_struct = None
            self.config_transfer = {}
        except Exception as e:
            self.textBrowser_error_log("%s"%e)

    def read_addr(self):
        now_addr = self.addr_textEdit.text()
        try:
            if re.match('^0x', now_addr):
                addr_read = int(now_addr, 16)
            else:
                addr_read = int(now_addr)
            read_value = self.running_case.read_atom(addr_read)
            if isinstance(read_value[0],int):
                self.textEdit.setText(hex(read_value[0]))
            if isinstance((read_value[0]),bytearray):
                self.textEdit.setText(hex(int(hexlify(read_value[0]).decode(), 16)))
            # read_value_bin = '{:0>8b}'.format(read_value[0])
        except Exception as e:
            self.textBrowser_error_log('read pushbutton pressed exists err:%s' % e)

    def write_addr(self):
        now_addr = self.addr_textEdit.text()
        try:
            if re.match('^0x', now_addr):
                addr_write = int(now_addr, 16)
            else:
                addr_write = int(now_addr)
            now_value = self.textEdit.text()
            if re.match('^0x', now_value):
                write_value = int(now_value, 16)
            else:
                write_value = int(now_value)
            # write_value_bin = '{:0>8b}'.format(write_value)
            self.running_case.write_atom(addr_write, write_value)
        except Exception as e:
            self.textBrowser_error_log('write pushbutton pressed err:%s' % e)

    def load_test_seq(self):
        test_seq_file, filetype = QFileDialog.getOpenFileName(self, "choose file", "./",
                                                              "All Files (*);;excel Files (*.xlsx);;excel Files (*.xls)")  # 设置文件扩展名过滤,注意用双分号间隔
        if test_seq_file == "":
            return
        else:
            self.textBrowser_normal_log("open a file:%s" % test_seq_file)
            self.parser_seq_file(test_seq_file)

    def parser_seq_file(self, fn):
        try:
            data = xlrd.open_workbook(fn)
            sheetsall = data.sheet_names()
            dialog = MainDialog1(sheetsall)
            dialog.Signal_parp.connect(self.deal_emit_sheet)
            dialog.show()
            dialog.exec_()
            if self.sheet_sel_lst != "":
                sheet_idx = sheetsall.index(self.sheet_sel_lst)
                self.textBrowser_normal_log('%s config begin!\n' % self.sheet_sel_lst)
                sheet_data = data.sheets()[sheet_idx]
                rows_num = sheet_data.nrows
                for x in range(0, rows_num):
                    if sheet_data.cell_value(x, 0) == 'sleep':
                        if sheet_data.cell_value(x, 1) == '':
                            self.textBrowser_normal_log('sleep 5\n')
                            time.sleep(5)
                        else:
                            try:
                                tmp_time = int(sheet_data.cell_value(x, 1))
                                self.textBrowser_normal_log('sleep %s \n' % str(tmp_time))
                                time.sleep(tmp_time)
                            except:
                                self.textBrowser_error_log('Error converting character to int')
                    elif sheet_data.cell_value(x, 0) == 'wait':
                        try:
                            temp_addr = int(sheet_data.cell_value(x, 1), 16)
                            temp_value = int(sheet_data.cell_value(x, 2), 16)
                            self.textBrowser_normal_log('start read_atom address : %s' % sheet_data.cell_value(x, 1))
                            read_flag = 0
                            for i in range(0, 300):
                                self.textBrowser_normal_log('sleep 1s')
                                time.sleep(1)
                                read_value = self.running_case.read_atom(temp_addr)
                                if read_value[0] == temp_value:
                                    read_flag = 1
                                    self.textBrowser_normal_log(
                                        'end read_atom address : %s real_value:%d is equal to temp_value:%d' % (
                                            sheet_data.cell_value(x, 1), read_value[0], temp_value))
                                    break
                                else:
                                    read_flag = 0
                            if read_flag != 1:
                                self.textBrowser_normal_log('loop 300 read_atom but real_value is not equal to '
                                                            'temp_value')
                        except Exception as e:
                            self.textBrowser_error_log('%s' % e)
                    elif sheet_data.cell_value(x, 0) == '':
                        pass
                    else:
                        try:
                            temp_addr = int(sheet_data.cell_value(x, 0), 16)
                            temp_data = int(sheet_data.cell_value(x, 1), 16)
                            info = 'write addr = ' + sheet_data.cell_value(x, 0) + ' data = ' + sheet_data.cell_value(x,
                                                                                                                      1)
                            self.textBrowser_normal_log(info)
                            self.running_case.write_atom(temp_addr, temp_data)
                        except Exception as e:
                            self.textBrowser_error_log('%s' % e)
            else:
                self.textBrowser_error_log("No sheet was selected")
        except Exception as e:
            info = 'error open file:%s,please input a excel file' % fn
            self.textBrowser_error_log(info)

    def deal_emit_sheet(self, select_sheet):
        self.sheet_sel_lst = select_sheet

    def mem_read(self):
        try:
            smp_lst = ['smp ddc output', 'smp tiskew corr', 'initial mem to 0', 'initial mem to 1', 'weight_rd']
            dialog = MainDialog1(smp_lst)
            dialog.Signal_parp.connect(self.deal_emit_sheet)
            dialog.show()
            dialog.exec_()
            if self.sheet_sel_lst in smp_lst:
                self.textBrowser_normal_log('choose %s' % self.sheet_sel_lst)
                sheet_idx = smp_lst.index(self.sheet_sel_lst)
                if sheet_idx == 0:
                    # self.textBrowser.insertPlainText('start sample ddc output!\n')
                    # ddc output
                    self.textBrowser_normal_log('start sample ddc output!')
                    try:
                        list_addr = [0xf18, 0xf16, 0xf1d, 0xf1c, 0xf16, 0xf17, 0xf19, 0xf1a, 0xf1b, 0xf1d, 0xf1c, 0xf18]
                        list_data = [0x00, 0x00, 0x1, 0x1, 0x08, 0x40, 0x3c, 0x00, 0x10, 0x0, 0x0, 0x02]
                        list_zip_addr_data = list(zip(list_addr, list_data))
                        target_write_idx1 = threading.Thread(target=self.write_thread(list_zip_addr_data))
                        target_write_idx1.start()
                    except Exception as e:
                        self.textBrowser_error_log('ddc output err:' + "%s" % e)
                elif sheet_idx == 1:
                    # self.textBrowser.insertPlainText('start sample tiskew_corr output!\n')
                    self.textBrowser_normal_log('start sample tiskew_corr output!')
                    pass
                elif sheet_idx == 2:
                    # self.textBrowser.insertPlainText('start initial mem to 0!\n')
                    self.textBrowser_normal_log('start initial mem to 0!')
                    list_addr_data = [(0xf10, 0x0), (0xf11, 0x0)]
                    self.write_thread(list_addr_data)
                    target_write_idx_mem0 = threading.Thread(target=self.pressure_idx_mem0())
                    target_write_idx_mem0.start()
                    self.textBrowser_normal_log('end initial mem to 0!')
                elif sheet_idx == 3:
                    # self.textBrowser.insertPlainText('start initial mem to 1!\n')
                    self.textBrowser_normal_log('start initial mem to 1!')
                    list_addr_data = [(0xf10, 0x0), (0xf11, 0x0)]
                    self.write_thread(list_addr_data)
                    target_write_idx_mem1 = threading.Thread(target=self.pressure_idx_mem1())
                    target_write_idx_mem1.start()
                    self.textBrowser_normal_log('end initial mem to 1!')
                elif sheet_idx == 4:
                    self.textBrowser_normal_log('start weight_rd!')
                    self.weight_rd()
                ##read mem
                if sheet_idx == 0 or sheet_idx == 1:
                    addr_data_list = [(0xf16, 0x10), (0xf10, 0x01), (0xf10, 0x0), (0xf11, 0x0)]
                    self.write_thread(addr_data_list)
                    time.sleep(5)
                    self.textBrowser_normal_log('write to memory_dump_data.txt')
                    self.memory_dump_data_write()
                    # target_memory_dump_data_write = threading.Thread(target=self.memory_dump_data_write())
                    # target_memory_dump_data_write.start()
                if sheet_idx == 1:
                    if os.path.exists('memory_dump_data.txt'):
                        target_read_memory_dump_data = threading.Thread(target=self.read_memory_dump_data())
                        target_read_memory_dump_data.start()
                    else:
                        return
        except Exception as e:
            self.textBrowser_error_log('%s' % e)

    def write_thread(self, list_addr_data):
        transfer_text = ''
        for item in list_addr_data:
            self.running_case.write_atom(item[0], item[1])
            addr_str = '{:0>4x}'.format(item[0])
            data_str = '{:0>4x}'.format(item[1])
            transfer_text += 'write addr: ' + addr_str + " data: " + data_str + "\n"
        self.textBrowser_normal_log(transfer_text)

    def weight_rd(self):
        try:
            os.remove('ana_weight.xls')
        except:
            pass
        try:
            wb = xlwt.Workbook()
            ws = wb.add_sheet('adc_weight')
            write_content_list = [(0, 0, 'ch_idx'), (0, 1, 'ch0'), (0, 2, 'ch1'), (0, 3, 'ch2'), (0, 4, 'ch3'),
                                  (1, 0, 'mdac0_weight1'), (2, 0, 'mdac1_weight1'), (3, 0, 'mdac2_weight1'),
                                  (4, 0, 'mdac3_weight1'), (5, 0, 'mdac4_weight1'), (6, 0, 'mdac5_weight1'),
                                  (7, 0, 'mdac6_weight1'), (8, 0, 'mdac7_weight1'), (9, 0, 'mdac0_weight2'),
                                  (10, 0, 'mdac1_weight2'), (11, 0, 'mdac2_weight2'), (12, 0, 'mdac3_weight2'),
                                  (13, 0, 'mdac4_weight2'), (14, 0, 'mdac5_weight2'), (15, 0, 'mdac6_weight2'),
                                  (16, 0, 'mdac7_weight2'), (17, 0, 'bkadc0_weight1'), (18, 0, 'bkadc1_weight1'),
                                  (19, 0, 'bkadc2_weight1'), (20, 0, 'bkadc3_weight1'), (21, 0, 'bkadc4_weight1'),
                                  (22, 0, 'bkadc5_weight1'), (23, 0, 'bkadc6_weight1'), (24, 0, 'bkadc7_weight1'),
                                  (25, 0, 'bkadc0_weight2'), (26, 0, 'bkadc1_weight2'), (27, 0, 'bkadc2_weight2'),
                                  (28, 0, 'bkadc3_weight2'), (29, 0, 'bkadc4_weight2'), (30, 0, 'bkadc5_weight2'),
                                  (31, 0, 'bkadc6_weight2'), (32, 0, 'bkadc7_weight2'), (33, 0, 'bkadc0_weight3'),
                                  (34, 0, 'bkadc1_weight3'), (35, 0, 'bkadc2_weight3'), (36, 0, 'bkadc3_weight3'),
                                  (37, 0, 'bkadc4_weight3'), (38, 0, 'bkadc5_weight3'), (39, 0, 'bkadc6_weight3'),
                                  (40, 0, 'bkadc7_weight3'), (41, 0, 'mdac_os0_weight'), (42, 0, 'mdac_os1_weight'),
                                  (43, 0, 'mdac_gec_weight'), (44, 0, 'mdac_dither_weight'), (45, 0, 'gec_coeff'),
                                  (46, 0, 'chopper_coeff'), (47, 0, 'tios_coeff'), (48, 0, 'tigain_coeff'),
                                  (49, 0, 'tiskew_code'), (50, 0, 'opgain_code')]
            for item in write_content_list:
                ws.write(item[0], item[1], item[2])
            for ch_idx in range(0, 4):
                for os_idx in range(0, 2):
                    read_data = self.running_case.read_atom(0x800 + 0x1d + ch_idx * 4 + os_idx * 2)
                    read_data1 = self.running_case.read_atom(0x800 + 0x1e + ch_idx * 4 + os_idx * 2)
                    weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                    ws.write(41 + os_idx, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x2d + ch_idx * 2)
                read_data1 = self.running_case.read_atom(0x800 + 0x2e + ch_idx * 2)
                weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                ws.write(43, 1 + ch_idx, weight)
                for mdac_idx in range(0, 8):
                    read_data = self.running_case.read_atom(0x800 + 0x3c + ch_idx * 24 + mdac_idx * 3)
                    read_data1 = self.running_case.read_atom(0x800 + 0x3d + ch_idx * 24 + mdac_idx * 3)
                    read_data2 = self.running_case.read_atom(0x800 + 0x3e + ch_idx * 24 + mdac_idx * 3)
                    weight = int(hexlify(read_data2[0]).decode(), 16) * 65536 + int(hexlify(read_data1[0]).decode(),
                                                                                    16) * 256 + int(
                        hexlify(read_data[0]).decode(), 16)
                    ws.write(1 + mdac_idx, 1 + ch_idx, weight)
                    read_data = self.running_case.read_atom(0x800 + 0x9c + ch_idx * 16 + mdac_idx * 2)
                    read_data1 = self.running_case.read_atom(0x800 + 0x9d + ch_idx * 16 + mdac_idx * 2)
                    weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                    ws.write(9 + mdac_idx, 1 + ch_idx, weight)
                    read_data = self.running_case.read_atom(0x800 + 0xdc + ch_idx * 16 + mdac_idx * 2)
                    read_data1 = self.running_case.read_atom(0x800 + 0xdd + ch_idx * 16 + mdac_idx * 2)
                    weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                    ws.write(17 + mdac_idx, 1 + ch_idx, weight)
                    read_data = self.running_case.read_atom(0x800 + 0x11c + ch_idx * 16 + mdac_idx * 2)
                    read_data1 = self.running_case.read_atom(0x800 + 0x11d + ch_idx * 16 + mdac_idx * 2)
                    weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                    ws.write(25 + mdac_idx, 1 + ch_idx, weight)
                    read_data = self.running_case.read_atom(0x800 + 0x15c + ch_idx * 16 + mdac_idx * 2)
                    read_data1 = self.running_case.read_atom(0x800 + 0x15d + ch_idx * 16 + mdac_idx * 2)
                    weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                    ws.write(33 + mdac_idx, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x19c + ch_idx * 3)
                read_data1 = self.running_case.read_atom(0x800 + 0x19d + ch_idx * 3)
                read_data2 = self.running_case.read_atom(0x800 + 0x19e + ch_idx * 3)
                weight = int(hexlify(read_data2[0]).decode(), 16) * 65536 + int(hexlify(read_data1[0]).decode(),
                                                                                16) * 256 + int(
                    hexlify(read_data[0]).decode(), 16)
                ws.write(44, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x355 + ch_idx * 2)
                read_data1 = self.running_case.read_atom(0x800 + 0x356 + ch_idx * 2)
                weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                ws.write(45, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x383 + ch_idx * 2)
                read_data1 = self.running_case.read_atom(0x800 + 0x384 + ch_idx * 2)
                weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                ws.write(46, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x3a6 + ch_idx * 2)
                read_data1 = self.running_case.read_atom(0x800 + 0x3a7 + ch_idx * 2)
                weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                ws.write(47, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x3c8 + ch_idx * 2)
                read_data1 = self.running_case.read_atom(0x800 + 0x3c9 + ch_idx * 2)
                weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                ws.write(48, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x3fd + ch_idx * 2)
                read_data1 = self.running_case.read_atom(0x800 + 0x3fe + ch_idx * 2)
                weight = int(hexlify(read_data1[0]).decode(), 16) * 256 + int(hexlify(read_data[0]).decode(), 16)
                ws.write(49, 1 + ch_idx, weight)
                read_data = self.running_case.read_atom(0x800 + 0x38 + ch_idx)
                weight = int(hexlify(read_data[0]).decode(), 16)
                ws.write(50, 1 + ch_idx, weight)
            wb.save('ana_weight.xls')
            self.textBrowser_normal_log('weight save done!')
        except Exception as e:
            self.textBrowser_error_log('%s + please close excel first' % e)

    def pressure_idx_mem0(self):
        for i in range(0, 131072):
            self.running_case.write_atom(0xf24, 0x0)

    def pressure_idx_mem1(self):
        for i in range(0, 131072):
            self.running_case.write_atom(0xf24, 0xff)

    def memory_dump_data_write(self):
        offset = 0x00
        data_old = 0x55
        with open('memory_dump_data.txt', 'w') as fp:
            for i in range(0, 16):
                data_new = i * 4 + offset
                self.running_case.write_atom(0xf11, data_old)
                self.running_case.write_atom(0xf11, data_new)
                read_buffer = self.read_mem_reg(0x8f, 0x24)
                for k in range(0, len(read_buffer)):
                    fp.write("%02x\n" % (read_buffer[k]))

    def read_mem_reg(self, addr0, addr1):
        read_data = self.spi_a.exchange([addr0, addr1], 4096)
        return read_data

    def dft_wei_test(self):
        try:
            self.running_case.printDumpInfo()
        except Exception as e:
            self.textBrowser_error_log("%s"%e+' ,please connect device first!')