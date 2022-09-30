# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 17:57:53 2022

@author: xyLucas
"""

# import TR9305_CFG

## fullband
##case0 = TR9305_CFG.TR9305_CFG(fs=3e9,
##                              lanerate=15e9,
##                              Jesd204B_M=2,
##                              Jesd204B_N=16,
##                              Jesd204B_F=2,
##                              Jesd204B_L=8)
##case0.tr9305_top_config()

## FourDDCmode dcm=48
# case1 = TR9305_CFG.TR9305_CFG(communicate_mode='log',    # 'log' 'box' 'usb'
#                               fs=3e9,
#                               lanerate=15e9,
#                               chip_mode='OneDDCmode',   #OneDDCmode TwoDDCmode FourDDCmode fullband
#                               mixerMode='complex',      # real complex
#                               ddc_dcm=2,
#                               inputMode='Complex',      # real complex
#                               outputMode='complex',     # real complex
#                               ffetap='5dB',             # 0dB 1p1dB 2p9dB 5dB 8dB
#                               gainMode='6dB',           # 0dB 6dB
#                               freqMode='0 Hz IF mode',  # Variable IF mode    0 Hz IF mode    fs Hz IF mode    Test mode
#                               ncoFTW=400e6,
#                               Jesd204B_K=32,
#                               Jesd204B_M=2,
#                               Jesd204B_N=16,
#                               Jesd204B_F=2,
#                               Jesd204B_L=4,
#                               Jesd204B_subclass=1,
#                               tios_accnum_power2=0x14,
#                               tiskew_accnum_power2=0x18,
#                               tiskew_code_step=1,
#                               high_th_dBFs=-0.9,
#                               low_th_dBFs=-20,
#                               phy_lane0=5,
#                               phy_lane1=4,
#                               phy_lane2=6,
#                               phy_lane3=7,
#                               phy_lane4=3,
#                               phy_lane5=0,
#                               phy_lane6=2,
#                               phy_lane7=1)
# case1.tr9305_top_config()
class spi_attribute:
    # freq = 30000000
    freq = 1250000
    cs = 0
    mode = 0
    cpol = 0
    cpha = 0
    tranbits = 8
    chn = 0
