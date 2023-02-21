# -*- coding: utf-8 -*-
import math

def func_calib_log10(para):
    return math.log10(para[0] / 4096) * 20
def func_jesd204b_ex(para):
    return 8 * para[0] * para[1] // para[2] // para[3]
def func_jesd204bframe_len(para):
    return para[0] * para[1]