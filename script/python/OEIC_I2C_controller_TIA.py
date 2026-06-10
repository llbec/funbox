# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 14:49:46 2023

@author: NtRdeMtrX
"""
# In[] Check USB Linking
# import usb.core
# dev = usb.core.find()
# print(dev)
# sn = usb.util.get_string(dev, dev.iSerialNumber)
# print(sn)


# In[] Check FTDI control linking
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController
Ftdi.show_devices()


# Instantiate an I2C controller

i2c = I2cController()
i2c.ftdi.list_devices()

# In[] simple example
i2c.configure('ftdi://ftdi:2232h/1', frequency=1e5)
slave = i2c.get_port(0x0C)
slave.read_from(0x1E, 1)

# In[] simple example
# In[]  Optaway QSFP28 SFF8636 Control
port =  80
slave = i2c.get_port(port)
word =  0x62 # 0x94
write_byte = b'\xef'
write_in = True # False True

try:
    if write_in:
        print(f"Write byte with {write_byte}.")
        i2c_write = slave.write_to(word, write_byte)
    i2c_read = slave.read_from(word, 1)[0]
except Exception as e:
    print(f"Chip [{port:3d}]: {e}")
else:
    print(f"Chip [{port:3d}]: Worked. Read [0x{word:02x}]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
    # break

# In[] find device address
# Configure the first interface (IF/1) of the FTDI device as an I2C master
i2c.configure('ftdi://ftdi:2232h/1', frequency=1e5)

for port in range(0, 0x80):
# Get a port to an I2C slave device
    slave = i2c.get_port(port)
    try:
        # if port == 39: 
        #     continue
        slave.read_from(0x00, 1)
        # slave.write_to(0x00, b'\x00')
    except Exception as e:
        print(f"{port:3d}: {e}")
    else:
        print(f"{port:3d}: Worked.")
        # break

# In[] Wave Scoping
port = 11 # TX 0b0001100 0x0c, RX 0b0001011 0x0b, Sweep out 0b0100001 0x21 (32, 33, 35, 40)
slave = i2c.get_port(port)
word = 0x00  # 0x94
write_in = True

while True:
    try:
        if write_in:
            i2c_write = slave.write_to(word, b'\x00\x00')
        i2c_read = slave.read_from(word, 1)[0]
    except Exception as e:
        print(f"Chip [{port:3d}]: {e}")
    else:
        print(f"Chip [{port:3d}]: Worked. Read [0x{word:02x}]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
        # break
    
# In[]  Read Test
port =  29
slave = i2c.get_port(port)
word =  0x09 # 0x94
write_in = False # False True
while True:
    try:
        if write_in:
            i2c_write = slave.write_to(word, b'\x03')
        i2c_read = slave.read_from(word, 1)[0]
    except Exception as e:
        print(f"Chip [{port:3d}]: {e}")
    else:
        print(f"Chip [{port:3d}]: Worked. Read [0x{word:02x}]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
        # break
        
# In[]
i2c.configure('ftdi://ftdi:2232h/1', frequency=1e5)
port = 11  # 0x0c 0x1d
# write_byte = b'\x00' # x00 x01 x7f
write_in = True # True False
# write_dict = {0x00:b'\x01', 0x91:b'\x00', 0x92:b'\x00', 0x93:b'\x00'}
write_dict = {0x10:b'\x01', 0x30:b'\x01', 0x50:b'\x01', 0x70:b'\x01'}
write_temp = {0x8d:b'\x00', 0x8f:b'\x08', 0x91:b'\x08', 0x93:b'\x08'}
write_dict.update(write_temp)

slave = i2c.get_port(port)
for word, write_byte in write_dict.items():
    try:
        if write_in:
            i2c_write = slave.write_to(word, write_byte)
        i2c_read = slave.read_from(word, 1)[0]
        # slave.write_to(0x00, b'\x00')
    except Exception as e:
        print(f"Chip [{port:3d}]: {e}")
    else:
        print(f"Chip [{port:3d}]: Worked. Read [0x{word:02x}]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
        # break

print()
# i2c_read = slave.read_from(0x94, 1)[0]
    # slave.write_to(0x00, b'\x00')
print(f"Chip [{port:3d}]: Worked. Read [0x94]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
 
# In[] Sweep Word
i2c.configure('ftdi://ftdi:2232h/1', frequency=1e5)
port = 0x0b  # 0x0c 0x1d
write_byte = b'\x00' # x00 x01 x7f
write_in = True # True False
reset_all_word = False # True False
write_dict = {}

#### RSSI
# write_dict = {0x8d:b'\x00', 0x8f:b'\08', 0x91:b'\08', 0x93:b'\08'}
write_dict = {0x8d:b'\x02', 0x8f:b'\08', 0x91:b'\08', 0x93:b'\08'}

#### Bypass_or_CDR Mode, C_SEL_VCO, DMUX_RSTB, FDPD_RSTB, CNTR_RSTB
ctrl_title = {"print1": ">>> CDR Control <<<"}
# write_dict.update(ctrl_title)
# for write_word_i in [0x00, 0x20, 0x40, 0x60]:
for write_word_i in [0x00]:
    write_word_list = [0x10, 0x13, 0x16, 0x17, 0x18]
    # write_byte_list = [b'\x00', b'\x03'] + [b'\x01']*3
    # write_byte_list = [b'\x01', b'\x00', b'\x00', b'\x00', b'\x00']
    write_byte_list = [b'\x00', b'\x03', b'\x00', b'\x01', b'\x01']
    for write_word_j, write_byte in zip(write_word_list, write_byte_list):
        write_word = write_word_i+write_word_j
        write_dict.update({write_word: write_byte})

# #### TX_QUOTA<0,16,32,48>(PRBS_SEL lane)
# ctrl_title = {"print2": ">>> PRBS Lane Control <<<"}
# ### TX_QUOTA Word 0xb8<5:4> 0xbc<5:4> -> PI_S1 PI_S0 = 0x00 0x10 0x20 0x30
# ctrl_title = {"print7": ">>> PRBS MUX PI Control <<<"}
# write_dict.update(ctrl_title)
# for write_word_i in [0xb8, 0xba, 0xbc, 0xbe]:
# # for write_word_i in [0xb8]:
# # for write_word_i in [0xbe]:
#     write_byte = b'\02'
#     write_dict.update({write_word_i: write_byte})
# # dict_temp = { 0xbc: b'\x00', 0xbe: b'\x01', 0xbf: b'\x00'
# #                 }
# # write_dict.update(dict_temp)

    
#### LOL_RSTB, DECI_CTRL
# ctrl_title = {"print3": ">>> LOL Control <<<"}
# write_dict.update(ctrl_title)
# for write_word_i in [0x00, 0x30, 0x60, 0x90]:
#     write_word_list = [0x13, 0x14]
#     write_byte_list = [b'\x00', b'\x00']
#     for write_word_j, write_byte in zip(write_word_list, write_byte_list):
#         write_word = write_word_i+write_word_j
#         write_dict.update({write_word: write_byte})

#### BIST_EN, PLL_F_SEL, PLL_C_SEL, PLL_DIV
# ctrl_title = {"print4": ">>> BIST PLL Control <<<"}
# write_dict.update(ctrl_title)
# # dict_temp = { 0x00: b'\x00', 0x91: b'\x01', 0x92: b'\x00', 0x93: b'\x06'} # 22G Locked
# dict_temp = { 0x00: b'\x00', 0x91: b'\x15', 0x92: b'\x02', 0x93: b'\x09'} # 25G Locked
# # dict_temp = { 0x00: b'\x01', 0x91: b'\x1e', 0x92: b'\x03', 0x93: b'\x11'} # 27G Locked
# write_dict.update(dict_temp)

# ### PRBS_SEL, PRBS_TX_RSTN, PRBS_TX_EN
# ctrl_title = {"print5": ">>> PRBS Generator Control <<<"}
# write_dict.update(ctrl_title)
# """
# 0x0a: TX1_prbs_sel, use by PRBS_GEN_1 and PRBS_CHECKER_1
# 0x3a: TX2_prbs_sel, use by PRBS_CHECKER_2 only
# 0x6a: TX3_prbs_sel, use by PRBS_GEN_3 and PRBS_CHECKER_3
# 0x9a: TX4_prbs_sel, use by PRBS_CHECKER_4 only
# """
# dict_temp = { 0x0a: b'\x00', 0x26: b'\x01', 0x27: b'\x01',
#               0x3a: b'\x00',
#               0x6a: b'\x00', 0x86: b'\x00', 0x87: b'\x00',
#               0x9a: b'\x00'
#             }
# write_dict.update(dict_temp)

#### NEAR_END, PRBS_RX_RSTN, PRBS_RX_EN
# ctrl_title = {"print6": ">>> PRBS Checker Control <<<"}
# write_dict.update(ctrl_title)
# for write_word_i in [0x00, 0x30, 0x60, 0x90]:
#     write_word_list = [0x16,    0x17,    0x18]
#     write_byte_list = [b'\x00', b'\x01', b'\x01']
#     # write_byte_list = [b'\x01'] + [b'\x01']*2
#     for write_word_j, write_byte in zip(write_word_list, write_byte_list):
#         write_word = write_word_i+write_word_j
#         write_dict.update({write_word: write_byte})
# #### STOP_AT_CNT<39:0>
# for write_word_i in [0x00, 0x30, 0x60, 0x90]:
#     write_word_list = list(range(0x19, 0x1e))
#     # write_byte_list = [b'\x00', b'\x03'] + [b'\x01']*3
#     write_byte_list = [b'\x03', b'\x00', b'\x00', b'\x00', b'\x00']
#     # write_byte_list = [b'\xff', b'\xff', b'\xff', b'\xff', b'\xff']
#     for write_word_j, write_byte in zip(write_word_list, write_byte_list):
#         write_word = write_word_i+write_word_j
#         write_dict.update({write_word: write_byte})

### 0xb8<5:4> 0xbc<5:4> -> PI_S1 PI_S0 = 0x00 0x10 0x20 0x30
# ctrl_title = {"print7": ">>> PRBS MUX PI Control <<<"}
# write_dict.update(ctrl_title)
# dict_temp = {0xb8: b'\x00', 0xbc: b'\x00'}
# write_dict.update(dict_temp)

### TX#_CTLE_CTRL_B
ctrl_title = {"print8": ">>> CTLE Control <<<"}
write_dict.update(ctrl_title)
for write_word_i in [0x12, 0x32, 0x52, 0x72]:
    write_byte = b'\x0f'
    write_dict.update({write_word_i: write_byte})
    
### TX#_AEQ_IRISE, AEQ_IFALL, AEQ_DELAY
# ctrl_title = {"print9": ">>> AEQ Control <<<"}
# write_dict.update(ctrl_title)
# for write_word_i in [0x00, 0x30, 0x60, 0x90]:
#     write_word_list = [0x07, 0x08, 0x09]
#     # write_byte_list = [b'\x00', b'\x03'] + [b'\x01']*3
#     write_byte_list = [b'\x0f', b'\x0f', b'\x0f']
#     for write_word_j, write_byte in zip(write_word_list, write_byte_list):
#         write_word = write_word_i+write_word_j
#         write_dict.update({write_word: write_byte})

# write_dict.update(ctrl_title)
# for write_word_i in [0x07, 0x37, 0x67, 0x97]:
#     write_byte = b'\x0a'
#     write_dict.update({write_word_i: write_byte})
# write_dict.update(ctrl_title)
# for write_word_i in [0x08, 0x38, 0x68, 0x98]:
#     write_byte = b'\x0a'
#     write_dict.update({write_word_i: write_byte})
# write_dict.update(ctrl_title)
# for write_word_i in [0x09, 0x39, 0x69, 0x99]:
#     write_byte = b'\x0a'
#     write_dict.update({write_word_i: write_byte})

### TX_VCTRL_LDO1
# ctrl_title = {"print10": ">>> LDO 1V Force <<<"}
# write_dict.update(ctrl_title)
# dict_temp = {0xbe: b'\x00'}
# write_dict.update(dict_temp)

#### !!!! DANGER !!!!
#### TX_QUOTA<1~3, 17~19, 33~35, 49~51>(TX#_vctrl_BG, TX#_vctrl_LDO12 TX#_vctrl_LDO1)
# dict_temp = {0xb8: b'\x0e', 0xba: b'\x0e', 0xbc: b'\x0e', 0xbe: b'\x0e'
#             }
# write_dict.update(dict_temp)


#### !!!! DANGER !!!! TX_QUOTA<62>(Digi_vctrl_BG), TX_QUOTA<63>(Digi_vctrl_LDO1)
# dict_temp = {0xbf: b'\xc0'}
# dict_temp = {0xbf: b'\x00'}
# write_dict.update(dict_temp)

if reset_all_word:
    for word in range(0x100):
        write_dict.update({word: b'\x00'})

#### Get a port to an I2C slave device
slave = i2c.get_port(port)
for word, write_byte in write_dict.items():
# for word in [0x0b, 0x3b, 0x6b, 0x9b]:
# for word in [0x0b, 0x3b, 0x6b, 0x9b]:
# for word in [0x0d, 0x3d, 0x6d, 0x9d]:
# for word in [0x06, 0x36, 0x66, 0x96]:
# for word in range(0x100):
# for word in range(1):
    if type(word) == str:
        print(write_byte)
    elif type(word) == int:
        try:
            if write_in:
                i2c_write = slave.write_to(word, write_byte)
            i2c_read = slave.read_from(word, 1)[0]
            # slave.write_to(0x00, b'\x00')
        except Exception as e:
            print(f"Chip [{port:3d}]: {e}")
        else:
            print(f"Chip [{port:3d}]: Worked. Read [0x{word:02x}]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
            # break


# ##### 讀取
print()
print("=== PLL UP/DN ===")
i2c_read = slave.read_from(0x04, 1)[0]
    # slave.write_to(0x00, b'\x00')
print(f"Chip [{port:3d}]: Worked. Read [0x04]: {i2c_read:3d} -> 0x{i2c_read:2x} -> 0b{i2c_read:8b}")
      
# print()
# for read_word_i in [0x00, 0x30, 0x60, 0x90]:
#     print(f"=== LANE {read_word_i//0x30+1} ===")
#     Total_cnt = 0
#     Error_cnt = 0
#     for read_word_j in range(0x1e, 0x26):
#         read_word = read_word_i+read_word_j
#         i2c_read = slave.read_from(read_word, 1)[0]
#             # slave.write_to(0x00, b'\x00')
#         print(f"Chip [{port:3d}]: Worked. Read [0x{read_word:2x}]: {i2c_read:3d} -> 0x{i2c_read:2x} -> 0b{i2c_read:8b}")
#         if read_word_j in range(0x1e, 0x24):
#             Total_cnt += i2c_read * 256**(read_word_j-0x1e)
#             # print(Total_cnt, read_word_j-0x1e, i2c_read)
#         elif read_word_j == 0x24:
#             Error_cnt = i2c_read
            
#     print(f"Total Count (hex): {Total_cnt:11x}")
#     print(f"Error Count (hex): {Error_cnt:11x}")

# In[] PLL test
i2c.configure('ftdi://ftdi:2232h/1', frequency=1e5)
port = 11  # 0x0c 0x1d
# write_byte = b'\x00' # x00 x01 x7f
write_in = True # True False

###### BIST_EN, F_SEL, C_SEL(b00, b10, b11), DIV
# for DIV in range(16):
write_dict = {0x00:b'\x00', 0x01:b'\x00', 0x02:b'\x03', 0x03:b'\x08'}

slave = i2c.get_port(port)
for word, write_byte in write_dict.items():
    try:
        if write_in:
            i2c_write = slave.write_to(word, write_byte)
        i2c_read = slave.read_from(word, 1)[0]
        # slave.write_to(0x00, b'\x00')
    except Exception as e:
        print(f"Chip [{port:3d}]: {e}")
    else:
        print(f"Chip [{port:3d}]: Worked. Read [0x{word:02x}]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
        # break

print()
i2c_read = slave.read_from(0x04, 1)[0]
    # slave.write_to(0x00, b'\x00')
print(f"Chip [{port:3d}]: Worked. Read [0x04]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
 

# In[]
write_in = True # True False
Total_cnt_accu = [0]*4
Error_cnt_accu = [0]*4
PLL_freq = 22 # GHz
stop_cnt = 3+1+1
write_dict = {}
for i in range(100):    
    ctrl_title = {"print6": ">>> PRBS Checker Control <<<"}
    write_dict.update(ctrl_title)
    for write_word_i in [0x00, 0x30, 0x60, 0x90]:
        write_word_list = [0x16,    0x17,    0x18]
        if i % 2 == 0:
            write_byte_list = [b'\x00', b'\x00', b'\x00']
        else:
            write_byte_list = [b'\x00', b'\x01', b'\x01']
        # write_byte_list = [b'\x01'] + [b'\x01']*2
        # write_byte_list = [b'\x01', b'\x01\x00', b'\x01']
        for write_word_j, write_byte in zip(write_word_list, write_byte_list):
            write_word = write_word_i+write_word_j
            write_dict.update({write_word: write_byte})
    #### Get a port to an I2C slave device
    slave = i2c.get_port(port)
    for word, write_byte in write_dict.items():
        if type(word) == str:
            print(write_byte)
        elif type(word) == int:
            try:
                if write_in:
                    i2c_write = slave.write_to(word, write_byte)
                i2c_read = slave.read_from(word, 1)[0]
                # slave.write_to(0x00, b'\x00')
            except Exception as e:
                # print(f"Chip [{port:3d}]: {e}")
                pass
            else:
                # print(f"Chip [{port:3d}]: Worked. Read [0x{word:02x}]: {i2c_read:3d} -> 0x{i2c_read:02x} -> 0b{i2c_read:08b}")
                # break
                pass
    if True:
        for read_word_i in [0x00, 0x30, 0x60, 0x90]:
            print(f"=== LANE {read_word_i//0x30+1} ===")
            Total_cnt = 0
            Error_cnt = 0
            for read_word_j in range(0x1e, 0x26):
                read_word = read_word_i+read_word_j
                i2c_read = slave.read_from(read_word, 1)[0]
                    # slave.write_to(0x00, b'\x00')
                print(f"Chip [{port:3d}]: Worked. Read [0x{read_word:2x}]: {i2c_read:3d} -> 0x{i2c_read:2x} -> 0b{i2c_read:8b}")
                if read_word_j in range(0x1e, 0x1f):
                    Total_cnt += i2c_read * 256**(read_word_j-0x1e)
                    # print(Total_cnt, read_word_j-0x1e, i2c_read)
                elif read_word_j == 0x24:
                    Error_cnt = i2c_read
                
            print(f"Total Count (hex): {Total_cnt:11x}")
            print(f"Error Count (hex): {Error_cnt:11x}")
            lane_index = read_word_i//0x30
            Total_cnt_accu[lane_index] += Total_cnt%stop_cnt
            Error_cnt_accu[lane_index] += Error_cnt
        
        print("_____________________________________")
        for j in range(4):
            print(f"lane{j+1}--")
            print(f"\tTotal Count (hex): {Total_cnt_accu[j]:11x}")
            print(f"\tError Count (hex): {Error_cnt_accu[j]:11x}")
            if Total_cnt_accu[j] == 0:
                print(f"\tBER: N/A")
            else:
                BER = Error_cnt_accu[j]/Total_cnt_accu[j] *0.125*16/PLL_freq
                print(f"\tBER: {BER:.10f}")
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    
# In[]
import time
port = 0x0c
write_byte = b'\x00' # x00 x01 x7f
write_in = True
slave = i2c.get_port(port)


i = 0
while True:
    if i%2 == 0:
        write_byte = b'\x7f'
    else:
        write_byte = b'\x00'
        
    # words = [0x06, 0x36, 0x66, 0x96]
    words = [0x96]
    # if i%8 in [0,1]:
    #     words = [0x06]
    # elif i%8 in [2,3]:
    #     words = [0x36]
    # elif i%8 in [4,5]:
    #     words = [0x66]
    # elif i%8 in [6,7]:
    #     words = [0x96]
# Get a port to an I2C slave device
# for word, write_byte in write_dict.items():
# for word in [0x0b, 0x3b, 0x6b, 0x9b]:
# for word in [0x0b, 0x3b, 0x6b, 0x9b]:
# for word in [0x0d, 0x3d, 0x6d, 0x9d]:
    # for word in [0x06, 0x36, 0x66, 0x96]:
    for word in words:
    # for word in range(0x100):
    # for word in range(1):
        try:
            if write_in:
                i2c_write = slave.write_to(word, write_byte)
            i2c_read = slave.read_from(word, 1)[0]
            # slave.write_to(0x00, b'\x00')
        except Exception as e:
            print(f"Chip [{port:3d}]: {e}")
        else:
            print(f"Chip [{port:3d}]: Worked. Read word[{word:02x}]: {i2c_read}")
            # break
    # Send one byte, then receive one byte
    # slave.exchange([0x04], 1)
    
    # # Write a register to the I2C slave
    # slave.write_to(0x06, b'\x00')
    
    # # Read a register from the I2C slave
    # slave.read_from(0x00, 1)
    time.sleep(1)
    i += 1

# In[]
port = 0x0c # TX 0b0001100 0x0c, RX 0b0001011 0x0b, Sweep out 0b0100001 0x21 (32, 33, 35, 40)

word_address = 0x00
"""
TX1_BYPASS_OR_CDR   0x0b 3b 6b 9b
TX1_C_SEL_VCO       0x0d 3d 6d 9d
"""
write_byte = b'\x00'
write_in = True # False True

slave = i2c.get_port(port)
try:
    if write_in:
        i2c_write = slave.write_to(word_address, write_byte)
    i2c_read = slave.read_from(word_address, 1)
except Exception as e:
    print(f"Chip [{port:3d}]: {e}")
else:
    print(f"Chip [{port:3d}]: Worked. Read word[{word_address:02x}]: {i2c_read}")
    # print(f"{port}: Worked. Read: {i2c_write}")
    # break