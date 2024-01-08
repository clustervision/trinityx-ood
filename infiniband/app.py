import subprocess
from flask import Flask, jsonify
from flask import render_template
import networkx as nx
import re

from base.config import settings
import networkx as nx


text = \
"""
#
# Topology file: generated on Mon Dec 18 12:34:08 2023
#
# Initiated from node 506b4b030043f9e2 port 506b4b030043f9e2
vendid=0x2c9
devid=0xcb20
sysimgguid=0xec0d9a0300ec8240
switchguid=0xec0d9a0300ec8240(ec0d9a0300ec8240)
Switch	36 "S-ec0d9a0300ec8240"		# "SwitchIB Mellanox Technologies" base port 0 lid 48 lmc 0
[1]	"H-506b4b03003fa9b6"[1](506b4b03003fa9b6) 		# "node018 HCA-1" lid 67 4xEDR
[2]	"H-506b4b03003fa9aa"[1](506b4b03003fa9aa) 		# "node020 HCA-1" lid 89 4xEDR
[3]	"H-506b4b030043f9c6"[1](506b4b030043f9c6) 		# "node014 HCA-1" lid 86 4xEDR
[4]	"H-506b4b030043f9ba"[1](506b4b030043f9ba) 		# "node016 HCA-1" lid 76 4xEDR
[5]	"H-506b4b03003fa99a"[1](506b4b03003fa99a) 		# "node010 HCA-1" lid 69 4xEDR
[6]	"H-506b4b030043fa5e"[1](506b4b030043fa5e) 		# "node012 HCA-1" lid 51 4xEDR
[7]	"H-506b4b030043f9da"[1](506b4b030043f9da) 		# "node006 HCA-1" lid 61 4xEDR
[8]	"H-506b4b030043fa66"[1](506b4b030043fa66) 		# "node008 HCA-1" lid 78 4xEDR
[9]	"H-506b4b030043f9b6"[1](506b4b030043f9b6) 		# "node002 HCA-1" lid 75 4xEDR
[10]	"H-506b4b030043f9de"[1](506b4b030043f9de) 		# "node004 HCA-1" lid 55 4xEDR
[11]	"H-506b4b030043f9f6"[1](506b4b030043f9f6) 		# "gpu001 HCA-1" lid 2 4xEDR
[12]	"H-08c0eb0300ddc0f6"[1](8c0eb0300ddc0f6) 		# "node046 HCA-1" lid 103 4xEDR
[13]	"S-ec0d9a0300ec81e0"[19]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[14]	"S-ec0d9a0300ec81e0"[20]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[15]	"S-ec0d9a0300ec81e0"[21]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[16]	"S-ec0d9a0300ec81e0"[22]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[17]	"S-ec0d9a0300ec81e0"[23]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[18]	"S-ec0d9a0300ec81e0"[24]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[19]	"S-ec0d9a0300ec8200"[19]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[20]	"S-ec0d9a0300ec8200"[20]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[21]	"S-ec0d9a0300ec8200"[21]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[22]	"S-ec0d9a0300ec8200"[22]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[23]	"S-ec0d9a0300ec8200"[23]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[24]	"S-ec0d9a0300ec8200"[24]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[25]	"H-506b4b030043fa3e"[1](506b4b030043fa3e) 		# "gpu002 HCA-1" lid 7 4xEDR
[26]	"H-506b4b030043fa86"[1](506b4b030043fa86) 		# "gpu003 HCA-1" lid 26 4xEDR
[27]	"H-506b4b03003fa962"[1](506b4b03003fa962) 		# "node001 HCA-1" lid 72 4xEDR
[28]	"H-506b4b030043fa6e"[1](506b4b030043fa6e) 		# "node003 HCA-1" lid 62 4xEDR
[29]	"H-506b4b03003fa9a6"[1](506b4b03003fa9a6) 		# "node005 HCA-1" lid 63 4xEDR
[30]	"H-506b4b030041d02a"[1](506b4b030041d02a) 		# "node007 HCA-1" lid 66 4xEDR
[31]	"H-506b4b03003fa952"[1](506b4b03003fa952) 		# "node009 HCA-1" lid 60 4xEDR
[32]	"H-506b4b030043fa72"[1](506b4b030043fa72) 		# "node011 HCA-1" lid 65 4xEDR
[33]	"H-506b4b030043f9aa"[1](506b4b030043f9aa) 		# "node013 HCA-1" lid 70 4xEDR
[34]	"H-506b4b030043f9b2"[1](506b4b030043f9b2) 		# "node015 HCA-1" lid 57 4xEDR
[35]	"H-506b4b03003fa9a2"[1](506b4b03003fa9a2) 		# "node017 HCA-1" lid 74 4xEDR
[36]	"H-506b4b03003fa98a"[1](506b4b03003fa98a) 		# "node019 HCA-1" lid 83 4xEDR
vendid=0x2c9
devid=0xcb20
sysimgguid=0xec0d9a0300ec8480
switchguid=0xec0d9a0300ec8480(ec0d9a0300ec8480)
Switch	36 "S-ec0d9a0300ec8480"		# "SwitchIB Mellanox Technologies" base port 0 lid 23 lmc 0
[1]	"S-ec0d9a0300ec81e0"[7]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[2]	"S-ec0d9a0300ec81e0"[8]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[3]	"S-ec0d9a0300ec81e0"[9]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[4]	"S-ec0d9a0300ec81e0"[10]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[5]	"S-ec0d9a0300ec81e0"[11]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[6]	"S-ec0d9a0300ec81e0"[12]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[7]	"S-ec0d9a0300ec8200"[7]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[8]	"S-ec0d9a0300ec8200"[8]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[9]	"S-ec0d9a0300ec8200"[9]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[10]	"S-ec0d9a0300ec8200"[10]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[11]	"S-ec0d9a0300ec8200"[11]		# "SwitchIB Mellanox Technologies" lid 25 4xDDR
[12]	"S-ec0d9a0300ec8200"[12]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[13]	"H-08c0eb0300ddbf02"[1](8c0eb0300ddbf02) 		# "gpu045 HCA-1" lid 100 4xEDR
[14]	"H-08c0eb0300ddbf0a"[1](8c0eb0300ddbf0a) 		# "node047 HCA-1" lid 101 4xEDR
[15]	"H-08c0eb0300ddc1aa"[1](8c0eb0300ddc1aa) 		# "node045 HCA-1" lid 102 4xEDR
[16]	"H-b8599f0300e95b44"[1](b8599f0300e95b44) 		# "node041 HCA-1" lid 91 4xEDR
[17]	"H-b8599f0300e963f4"[1](b8599f0300e963f4) 		# "node042 HCA-1" lid 92 4xEDR
[18]	"H-b8599f0300e95dd8"[1](b8599f0300e95dd8) 		# "node043 HCA-1" lid 93 4xEDR
[19]	"H-b8599f0300e96494"[1](b8599f0300e96494) 		# "node044 HCA-1" lid 94 4xEDR
[20]	"H-506b4b03003fa9b2"[1](506b4b03003fa9b2) 		# "gpu004 HCA-1" lid 8 4xEDR
[21]	"H-506b4b030043fa32"[1](506b4b030043fa32) 		# "gpu005 HCA-1" lid 33 4xEDR
[22]	"H-506b4b030043fa36"[1](506b4b030043fa36) 		# "gpu006 HCA-1" lid 45 4xEDR
[23]	"H-506b4b030043fa1a"[1](506b4b030043fa1a) 		# "gpu007 HCA-1" lid 28 4xEDR
[24]	"H-506b4b030043fa2e"[1](506b4b030043fa2e) 		# "gpu008 HCA-1" lid 32 4xEDR
[25]	"H-506b4b030043fa1e"[1](506b4b030043fa1e) 		# "gpu009 HCA-1" lid 41 4xEDR
[26]	"H-506b4b030043f9ae"[1](506b4b030043f9ae) 		# "gpu010 HCA-1" lid 11 4xEDR
[27]	"H-506b4b030043fa26"[1](506b4b030043fa26) 		# "gpu011 HCA-1" lid 1 4xEDR
[28]	"H-506b4b030043f9fe"[1](506b4b030043f9fe) 		# "gpu012 HCA-1" lid 4 4xEDR
[29]	"H-506b4b030043f9be"[1](506b4b030043f9be) 		# "gpu013 HCA-1" lid 40 4xEDR
[30]	"H-506b4b030043fa92"[1](506b4b030043fa92) 		# "gpu014 HCA-1" lid 6 4xEDR
[31]	"H-506b4b030043fa12"[1](506b4b030043fa12) 		# "gpu015 HCA-1" lid 3 4xEDR
[32]	"H-506b4b030043fa22"[1](506b4b030043fa22) 		# "gpu016 HCA-1" lid 31 4xEDR
[33]	"H-506b4b030043fa6a"[1](506b4b030043fa6a) 		# "gpu017 HCA-1" lid 15 4xEDR
[34]	"H-506b4b030043f9f2"[1](506b4b030043f9f2) 		# "gpu018 HCA-1" lid 17 4xEDR
[35]	"H-506b4b030043f9e6"[1](506b4b030043f9e6) 		# "gpu019 HCA-1" lid 49 4xEDR
[36]	"H-506b4b030043f9ee"[1](506b4b030043f9ee) 		# "gpu020 HCA-1" lid 24 4xEDR
vendid=0x2c9
devid=0xcb20
sysimgguid=0xec0d9a0300f548e0
switchguid=0xec0d9a0300f548e0(ec0d9a0300f548e0)
Switch	36 "S-ec0d9a0300f548e0"		# "SwitchIB Mellanox Technologies" base port 0 lid 19 lmc 0
[1]	"S-ec0d9a0300ec81e0"[1]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[2]	"S-ec0d9a0300ec81e0"[2]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[3]	"S-ec0d9a0300ec81e0"[3]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[4]	"S-ec0d9a0300ec81e0"[4]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[5]	"S-ec0d9a0300ec81e0"[5]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[6]	"S-ec0d9a0300ec81e0"[6]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[7]	"S-ec0d9a0300ec8200"[1]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[8]	"S-ec0d9a0300ec8200"[2]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[9]	"S-ec0d9a0300ec8200"[3]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[10]	"S-ec0d9a0300ec8200"[4]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[11]	"S-ec0d9a0300ec8200"[5]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[12]	"S-ec0d9a0300ec8200"[6]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[13]	"H-043f720300da2714"[1](43f720300da2714) 		# "gpu041 HCA-1" lid 95 4xEDR
[14]	"H-043f720300da2370"[1](43f720300da2370) 		# "gpu042 HCA-1" lid 96 4xEDR
[15]	"H-043f720300da0bd0"[1](43f720300da0bd0) 		# "gpu043 HCA-1" lid 97 4xEDR
[16]	"H-043f720300da0d80"[1](43f720300da0d80) 		# "gpu044 HCA-1" lid 98 4xEDR
[17]	"H-506b4b030043f9fa"[1](506b4b030043f9fa) 		# "gpu021 HCA-1" lid 27 4xEDR
[18]	"H-506b4b030043fa0a"[1](506b4b030043fa0a) 		# "gpu022 HCA-1" lid 43 4xEDR
[19]	"H-506b4b030043fa06"[1](506b4b030043fa06) 		# "gpu023 HCA-1" lid 30 4xEDR
[20]	"H-506b4b030043fa4e"[1](506b4b030043fa4e) 		# "gpu024 HCA-1" lid 13 4xEDR
[21]	"H-506b4b030043fa02"[1](506b4b030043fa02) 		# "gpu025 HCA-1" lid 9 4xEDR
[22]	"H-506b4b030043fa2a"[1](506b4b030043fa2a) 		# "gpu026 HCA-1" lid 18 4xEDR
[23]	"H-506b4b030043fa7e"[1](506b4b030043fa7e) 		# "gpu027 HCA-1" lid 16 4xEDR
[24]	"H-506b4b030043fa3a"[1](506b4b030043fa3a) 		# "gpu028 HCA-1" lid 20 4xEDR
[25]	"H-506b4b030043fa0e"[1](506b4b030043fa0e) 		# "gpu029 HCA-1" lid 44 4xEDR
[26]	"H-506b4b03003fa9ba"[1](506b4b03003fa9ba) 		# "gpu030 HCA-1" lid 22 4xEDR
[27]	"H-506b4b030043fa62"[1](506b4b030043fa62) 		# "gpu031 HCA-1" lid 14 4xEDR
[28]	"H-506b4b030043fa42"[1](506b4b030043fa42) 		# "gpu032 HCA-1" lid 12 4xEDR
[29]	"H-506b4b030041cf72"[1](506b4b030041cf72) 		# "gpu033 HCA-1" lid 10 4xEDR
[30]	"H-506b4b030043f9ea"[1](506b4b030043f9ea) 		# "gpu034 HCA-1" lid 50 4xEDR
[31]	"H-506b4b030043fa9a"[1](506b4b030043fa9a) 		# "gpu035 HCA-1" lid 47 4xEDR
[32]	"H-506b4b030043fa4a"[1](506b4b030043fa4a) 		# "gpu036 HCA-1" lid 36 4xEDR
[33]	"H-506b4b030043fa46"[1](506b4b030043fa46) 		# "gpu037 HCA-1" lid 35 4xEDR
[34]	"H-506b4b030043fa7a"[1](506b4b030043fa7a) 		# "gpu038 HCA-1" lid 37 4xEDR
[35]	"H-506b4b030043fa52"[1](506b4b030043fa52) 		# "gpu039 HCA-1" lid 46 4xEDR
[36]	"H-506b4b030043fa8e"[1](506b4b030043fa8e) 		# "gpu040 HCA-1" lid 5 4xEDR
vendid=0x2c9
devid=0xcb20
sysimgguid=0xec0d9a0300ec8200
switchguid=0xec0d9a0300ec8200(ec0d9a0300ec8200)
Switch	36 "S-ec0d9a0300ec8200"		# "SwitchIB Mellanox Technologies" base port 0 lid 25 lmc 0
[1]	"S-ec0d9a0300f548e0"[7]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[2]	"S-ec0d9a0300f548e0"[8]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[3]	"S-ec0d9a0300f548e0"[9]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[4]	"S-ec0d9a0300f548e0"[10]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[5]	"S-ec0d9a0300f548e0"[11]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[6]	"S-ec0d9a0300f548e0"[12]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[7]	"S-ec0d9a0300ec8480"[7]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[8]	"S-ec0d9a0300ec8480"[8]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[9]	"S-ec0d9a0300ec8480"[9]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[10]	"S-ec0d9a0300ec8480"[10]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[11]	"S-ec0d9a0300ec8480"[11]		# "SwitchIB Mellanox Technologies" lid 23 4xDDR
[12]	"S-ec0d9a0300ec8480"[12]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[13]	"S-ec0d9a0300f548c0"[19]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[14]	"S-ec0d9a0300f548c0"[20]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[15]	"S-ec0d9a0300f548c0"[21]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[16]	"S-ec0d9a0300f548c0"[22]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[17]	"S-ec0d9a0300f548c0"[23]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[18]	"S-ec0d9a0300f548c0"[24]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[19]	"S-ec0d9a0300ec8240"[19]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[20]	"S-ec0d9a0300ec8240"[20]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[21]	"S-ec0d9a0300ec8240"[21]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[22]	"S-ec0d9a0300ec8240"[22]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[23]	"S-ec0d9a0300ec8240"[23]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[24]	"S-ec0d9a0300ec8240"[24]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0xcb20
sysimgguid=0xec0d9a0300ec81e0
switchguid=0xec0d9a0300ec81e0(ec0d9a0300ec81e0)
Switch	36 "S-ec0d9a0300ec81e0"		# "SwitchIB Mellanox Technologies" base port 0 lid 21 lmc 0
[1]	"S-ec0d9a0300f548e0"[1]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[2]	"S-ec0d9a0300f548e0"[2]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[3]	"S-ec0d9a0300f548e0"[3]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[4]	"S-ec0d9a0300f548e0"[4]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[5]	"S-ec0d9a0300f548e0"[5]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[6]	"S-ec0d9a0300f548e0"[6]		# "SwitchIB Mellanox Technologies" lid 19 4xEDR
[7]	"S-ec0d9a0300ec8480"[1]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[8]	"S-ec0d9a0300ec8480"[2]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[9]	"S-ec0d9a0300ec8480"[3]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[10]	"S-ec0d9a0300ec8480"[4]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[11]	"S-ec0d9a0300ec8480"[5]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[12]	"S-ec0d9a0300ec8480"[6]		# "SwitchIB Mellanox Technologies" lid 23 4xEDR
[13]	"S-ec0d9a0300f548c0"[13]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[14]	"S-ec0d9a0300f548c0"[14]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[15]	"S-ec0d9a0300f548c0"[15]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[16]	"S-ec0d9a0300f548c0"[16]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[17]	"S-ec0d9a0300f548c0"[17]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[18]	"S-ec0d9a0300f548c0"[18]		# "SwitchIB Mellanox Technologies" lid 29 4xEDR
[19]	"S-ec0d9a0300ec8240"[13]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[20]	"S-ec0d9a0300ec8240"[14]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[21]	"S-ec0d9a0300ec8240"[15]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[22]	"S-ec0d9a0300ec8240"[16]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[23]	"S-ec0d9a0300ec8240"[17]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
[24]	"S-ec0d9a0300ec8240"[18]		# "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0xcb20
sysimgguid=0xec0d9a0300f548c0
switchguid=0xec0d9a0300f548c0(ec0d9a0300f548c0)
Switch	36 "S-ec0d9a0300f548c0"		# "SwitchIB Mellanox Technologies" base port 0 lid 29 lmc 0
[1]	"H-506b4b030043fa5a"[1](506b4b030043fa5a) 		# "node038 HCA-1" lid 81 4xEDR
[2]	"H-506b4b030041d032"[1](506b4b030041d032) 		# "node040 HCA-1" lid 64 4xEDR
[3]	"H-506b4b030041d026"[1](506b4b030041d026) 		# "node034 HCA-1" lid 59 4xEDR
[4]	"H-506b4b030043f9a6"[1](506b4b030043f9a6) 		# "node036 HCA-1" lid 53 4xEDR
[5]	"H-506b4b030043f9d2"[1](506b4b030043f9d2) 		# "node030 HCA-1" lid 87 4xEDR
[6]	"H-506b4b030043f9d6"[1](506b4b030043f9d6) 		# "node032 HCA-1" lid 54 4xEDR
[7]	"H-506b4b03003fa992"[1](506b4b03003fa992) 		# "node026 HCA-1" lid 79 4xEDR
[8]	"H-506b4b03003fa966"[1](506b4b03003fa966) 		# "node028 HCA-1" lid 52 4xEDR
[9]	"H-506b4b030041cfd2"[1](506b4b030041cfd2) 		# "node022 HCA-1" lid 77 4xEDR
[10]	"H-506b4b030043fa16"[1](506b4b030043fa16) 		# "node024 HCA-1" lid 90 4xEDR
[11]	"H-506b4b030043fa8a"[1](506b4b030043fa8a) 		# "bee01 HCA-1" lid 39 4xEDR
[12]	"H-506b4b030043fa82"[1](506b4b030043fa82) 		# "bee02 HCA-1" lid 38 4xEDR
[13]	"S-ec0d9a0300ec81e0"[13]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[14]	"S-ec0d9a0300ec81e0"[14]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[15]	"S-ec0d9a0300ec81e0"[15]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[16]	"S-ec0d9a0300ec81e0"[16]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[17]	"S-ec0d9a0300ec81e0"[17]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[18]	"S-ec0d9a0300ec81e0"[18]		# "SwitchIB Mellanox Technologies" lid 21 4xEDR
[19]	"S-ec0d9a0300ec8200"[13]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[20]	"S-ec0d9a0300ec8200"[14]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[21]	"S-ec0d9a0300ec8200"[15]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[22]	"S-ec0d9a0300ec8200"[16]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[23]	"S-ec0d9a0300ec8200"[17]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[24]	"S-ec0d9a0300ec8200"[18]		# "SwitchIB Mellanox Technologies" lid 25 4xEDR
[25]	"H-506b4b030043f9e2"[1](506b4b030043f9e2) 		# "controller mlx5_0" lid 34 4xEDR
[26]	"H-506b4b030043fa96"[1](506b4b030043fa96) 		# "login01 HCA-1" lid 42 4xEDR
[27]	"H-506b4b030043f9ca"[1](506b4b030043f9ca) 		# "node021 HCA-1" lid 58 4xEDR
[28]	"H-506b4b030043f9ce"[1](506b4b030043f9ce) 		# "node023 HCA-1" lid 56 4xEDR
[29]	"H-506b4b03003fa9be"[1](506b4b03003fa9be) 		# "node025 HCA-1" lid 84 4xEDR
[30]	"H-506b4b03003fa996"[1](506b4b03003fa996) 		# "node027 HCA-1" lid 73 4xEDR
[31]	"H-506b4b030041d01e"[1](506b4b030041d01e) 		# "node029 HCA-1" lid 80 4xEDR
[32]	"H-506b4b030043f9c2"[1](506b4b030043f9c2) 		# "node031 HCA-1" lid 85 4xEDR
[33]	"H-506b4b030043fa76"[1](506b4b030043fa76) 		# "node033 HCA-1" lid 82 4xEDR
[34]	"H-506b4b030041d0d6"[1](506b4b030041d0d6) 		# "node035 HCA-1" lid 88 4xEDR
[35]	"H-506b4b0300167328"[1](506b4b0300167328) 		# "node037 HCA-1" lid 68 4xEDR
[36]	"H-506b4b030041d022"[1](506b4b030041d022) 		# "node039 HCA-1" lid 71 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa98a
caguid=0x506b4b03003fa98a
Ca	1 "H-506b4b03003fa98a"		# "node019 HCA-1"
[1](506b4b03003fa98a) 	"S-ec0d9a0300ec8240"[36]		# lid 83 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa9a2
caguid=0x506b4b03003fa9a2
Ca	1 "H-506b4b03003fa9a2"		# "node017 HCA-1"
[1](506b4b03003fa9a2) 	"S-ec0d9a0300ec8240"[35]		# lid 74 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9b2
caguid=0x506b4b030043f9b2
Ca	1 "H-506b4b030043f9b2"		# "node015 HCA-1"
[1](506b4b030043f9b2) 	"S-ec0d9a0300ec8240"[34]		# lid 57 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9aa
caguid=0x506b4b030043f9aa
Ca	1 "H-506b4b030043f9aa"		# "node013 HCA-1"
[1](506b4b030043f9aa) 	"S-ec0d9a0300ec8240"[33]		# lid 70 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa72
caguid=0x506b4b030043fa72
Ca	1 "H-506b4b030043fa72"		# "node011 HCA-1"
[1](506b4b030043fa72) 	"S-ec0d9a0300ec8240"[32]		# lid 65 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa952
caguid=0x506b4b03003fa952
Ca	1 "H-506b4b03003fa952"		# "node009 HCA-1"
[1](506b4b03003fa952) 	"S-ec0d9a0300ec8240"[31]		# lid 60 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041d02a
caguid=0x506b4b030041d02a
Ca	1 "H-506b4b030041d02a"		# "node007 HCA-1"
[1](506b4b030041d02a) 	"S-ec0d9a0300ec8240"[30]		# lid 66 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa9a6
caguid=0x506b4b03003fa9a6
Ca	1 "H-506b4b03003fa9a6"		# "node005 HCA-1"
[1](506b4b03003fa9a6) 	"S-ec0d9a0300ec8240"[29]		# lid 63 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa6e
caguid=0x506b4b030043fa6e
Ca	1 "H-506b4b030043fa6e"		# "node003 HCA-1"
[1](506b4b030043fa6e) 	"S-ec0d9a0300ec8240"[28]		# lid 62 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa962
caguid=0x506b4b03003fa962
Ca	1 "H-506b4b03003fa962"		# "node001 HCA-1"
[1](506b4b03003fa962) 	"S-ec0d9a0300ec8240"[27]		# lid 72 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa3e
caguid=0x506b4b030043fa3e
Ca	1 "H-506b4b030043fa3e"		# "gpu002 HCA-1"
[1](506b4b030043fa3e) 	"S-ec0d9a0300ec8240"[25]		# lid 7 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa86
caguid=0x506b4b030043fa86
Ca	1 "H-506b4b030043fa86"		# "gpu003 HCA-1"
[1](506b4b030043fa86) 	"S-ec0d9a0300ec8240"[26]		# lid 26 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x8c0eb0300ddc0f6
caguid=0x8c0eb0300ddc0f6
Ca	1 "H-08c0eb0300ddc0f6"		# "node046 HCA-1"
[1](8c0eb0300ddc0f6) 	"S-ec0d9a0300ec8240"[12]		# lid 103 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9f6
caguid=0x506b4b030043f9f6
Ca	1 "H-506b4b030043f9f6"		# "gpu001 HCA-1"
[1](506b4b030043f9f6) 	"S-ec0d9a0300ec8240"[11]		# lid 2 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9de
caguid=0x506b4b030043f9de
Ca	1 "H-506b4b030043f9de"		# "node004 HCA-1"
[1](506b4b030043f9de) 	"S-ec0d9a0300ec8240"[10]		# lid 55 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9b6
caguid=0x506b4b030043f9b6
Ca	1 "H-506b4b030043f9b6"		# "node002 HCA-1"
[1](506b4b030043f9b6) 	"S-ec0d9a0300ec8240"[9]		# lid 75 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa66
caguid=0x506b4b030043fa66
Ca	1 "H-506b4b030043fa66"		# "node008 HCA-1"
[1](506b4b030043fa66) 	"S-ec0d9a0300ec8240"[8]		# lid 78 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9da
caguid=0x506b4b030043f9da
Ca	1 "H-506b4b030043f9da"		# "node006 HCA-1"
[1](506b4b030043f9da) 	"S-ec0d9a0300ec8240"[7]		# lid 61 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa5e
caguid=0x506b4b030043fa5e
Ca	1 "H-506b4b030043fa5e"		# "node012 HCA-1"
[1](506b4b030043fa5e) 	"S-ec0d9a0300ec8240"[6]		# lid 51 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa99a
caguid=0x506b4b03003fa99a
Ca	1 "H-506b4b03003fa99a"		# "node010 HCA-1"
[1](506b4b03003fa99a) 	"S-ec0d9a0300ec8240"[5]		# lid 69 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9ba
caguid=0x506b4b030043f9ba
Ca	1 "H-506b4b030043f9ba"		# "node016 HCA-1"
[1](506b4b030043f9ba) 	"S-ec0d9a0300ec8240"[4]		# lid 76 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9c6
caguid=0x506b4b030043f9c6
Ca	1 "H-506b4b030043f9c6"		# "node014 HCA-1"
[1](506b4b030043f9c6) 	"S-ec0d9a0300ec8240"[3]		# lid 86 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa9aa
caguid=0x506b4b03003fa9aa
Ca	1 "H-506b4b03003fa9aa"		# "node020 HCA-1"
[1](506b4b03003fa9aa) 	"S-ec0d9a0300ec8240"[2]		# lid 89 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9e6
caguid=0x506b4b030043f9e6
Ca	1 "H-506b4b030043f9e6"		# "gpu019 HCA-1"
[1](506b4b030043f9e6) 	"S-ec0d9a0300ec8480"[35]		# lid 49 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa9b6
caguid=0x506b4b03003fa9b6
Ca	1 "H-506b4b03003fa9b6"		# "node018 HCA-1"
[1](506b4b03003fa9b6) 	"S-ec0d9a0300ec8240"[1]		# lid 67 lmc 0 "SwitchIB Mellanox Technologies" lid 48 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9ee
caguid=0x506b4b030043f9ee
Ca	1 "H-506b4b030043f9ee"		# "gpu020 HCA-1"
[1](506b4b030043f9ee) 	"S-ec0d9a0300ec8480"[36]		# lid 24 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9f2
caguid=0x506b4b030043f9f2
Ca	1 "H-506b4b030043f9f2"		# "gpu018 HCA-1"
[1](506b4b030043f9f2) 	"S-ec0d9a0300ec8480"[34]		# lid 17 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa6a
caguid=0x506b4b030043fa6a
Ca	1 "H-506b4b030043fa6a"		# "gpu017 HCA-1"
[1](506b4b030043fa6a) 	"S-ec0d9a0300ec8480"[33]		# lid 15 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa22
caguid=0x506b4b030043fa22
Ca	1 "H-506b4b030043fa22"		# "gpu016 HCA-1"
[1](506b4b030043fa22) 	"S-ec0d9a0300ec8480"[32]		# lid 31 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9be
caguid=0x506b4b030043f9be
Ca	1 "H-506b4b030043f9be"		# "gpu013 HCA-1"
[1](506b4b030043f9be) 	"S-ec0d9a0300ec8480"[29]		# lid 40 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa12
caguid=0x506b4b030043fa12
Ca	1 "H-506b4b030043fa12"		# "gpu015 HCA-1"
[1](506b4b030043fa12) 	"S-ec0d9a0300ec8480"[31]		# lid 3 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa92
caguid=0x506b4b030043fa92
Ca	1 "H-506b4b030043fa92"		# "gpu014 HCA-1"
[1](506b4b030043fa92) 	"S-ec0d9a0300ec8480"[30]		# lid 6 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9fe
caguid=0x506b4b030043f9fe
Ca	1 "H-506b4b030043f9fe"		# "gpu012 HCA-1"
[1](506b4b030043f9fe) 	"S-ec0d9a0300ec8480"[28]		# lid 4 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa26
caguid=0x506b4b030043fa26
Ca	1 "H-506b4b030043fa26"		# "gpu011 HCA-1"
[1](506b4b030043fa26) 	"S-ec0d9a0300ec8480"[27]		# lid 1 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9ae
caguid=0x506b4b030043f9ae
Ca	1 "H-506b4b030043f9ae"		# "gpu010 HCA-1"
[1](506b4b030043f9ae) 	"S-ec0d9a0300ec8480"[26]		# lid 11 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa1e
caguid=0x506b4b030043fa1e
Ca	1 "H-506b4b030043fa1e"		# "gpu009 HCA-1"
[1](506b4b030043fa1e) 	"S-ec0d9a0300ec8480"[25]		# lid 41 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa2e
caguid=0x506b4b030043fa2e
Ca	1 "H-506b4b030043fa2e"		# "gpu008 HCA-1"
[1](506b4b030043fa2e) 	"S-ec0d9a0300ec8480"[24]		# lid 32 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa36
caguid=0x506b4b030043fa36
Ca	1 "H-506b4b030043fa36"		# "gpu006 HCA-1"
[1](506b4b030043fa36) 	"S-ec0d9a0300ec8480"[22]		# lid 45 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa1a
caguid=0x506b4b030043fa1a
Ca	1 "H-506b4b030043fa1a"		# "gpu007 HCA-1"
[1](506b4b030043fa1a) 	"S-ec0d9a0300ec8480"[23]		# lid 28 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa32
caguid=0x506b4b030043fa32
Ca	1 "H-506b4b030043fa32"		# "gpu005 HCA-1"
[1](506b4b030043fa32) 	"S-ec0d9a0300ec8480"[21]		# lid 33 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa9b2
caguid=0x506b4b03003fa9b2
Ca	1 "H-506b4b03003fa9b2"		# "gpu004 HCA-1"
[1](506b4b03003fa9b2) 	"S-ec0d9a0300ec8480"[20]		# lid 8 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0xb8599f0300e96494
caguid=0xb8599f0300e96494
Ca	1 "H-b8599f0300e96494"		# "node044 HCA-1"
[1](b8599f0300e96494) 	"S-ec0d9a0300ec8480"[19]		# lid 94 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0xb8599f0300e95dd8
caguid=0xb8599f0300e95dd8
Ca	1 "H-b8599f0300e95dd8"		# "node043 HCA-1"
[1](b8599f0300e95dd8) 	"S-ec0d9a0300ec8480"[18]		# lid 93 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0xb8599f0300e963f4
caguid=0xb8599f0300e963f4
Ca	1 "H-b8599f0300e963f4"		# "node042 HCA-1"
[1](b8599f0300e963f4) 	"S-ec0d9a0300ec8480"[17]		# lid 92 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x8c0eb0300ddc1aa
caguid=0x8c0eb0300ddc1aa
Ca	1 "H-08c0eb0300ddc1aa"		# "node045 HCA-1"
[1](8c0eb0300ddc1aa) 	"S-ec0d9a0300ec8480"[15]		# lid 102 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0xb8599f0300e95b44
caguid=0xb8599f0300e95b44
Ca	1 "H-b8599f0300e95b44"		# "node041 HCA-1"
[1](b8599f0300e95b44) 	"S-ec0d9a0300ec8480"[16]		# lid 91 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x8c0eb0300ddbf0a
caguid=0x8c0eb0300ddbf0a
Ca	1 "H-08c0eb0300ddbf0a"		# "node047 HCA-1"
[1](8c0eb0300ddbf0a) 	"S-ec0d9a0300ec8480"[14]		# lid 101 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x8c0eb0300ddbf02
caguid=0x8c0eb0300ddbf02
Ca	1 "H-08c0eb0300ddbf02"		# "gpu045 HCA-1"
[1](8c0eb0300ddbf02) 	"S-ec0d9a0300ec8480"[13]		# lid 100 lmc 0 "SwitchIB Mellanox Technologies" lid 23 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa8e
caguid=0x506b4b030043fa8e
Ca	1 "H-506b4b030043fa8e"		# "gpu040 HCA-1"
[1](506b4b030043fa8e) 	"S-ec0d9a0300f548e0"[36]		# lid 5 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa52
caguid=0x506b4b030043fa52
Ca	1 "H-506b4b030043fa52"		# "gpu039 HCA-1"
[1](506b4b030043fa52) 	"S-ec0d9a0300f548e0"[35]		# lid 46 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa7a
caguid=0x506b4b030043fa7a
Ca	1 "H-506b4b030043fa7a"		# "gpu038 HCA-1"
[1](506b4b030043fa7a) 	"S-ec0d9a0300f548e0"[34]		# lid 37 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa46
caguid=0x506b4b030043fa46
Ca	1 "H-506b4b030043fa46"		# "gpu037 HCA-1"
[1](506b4b030043fa46) 	"S-ec0d9a0300f548e0"[33]		# lid 35 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9ea
caguid=0x506b4b030043f9ea
Ca	1 "H-506b4b030043f9ea"		# "gpu034 HCA-1"
[1](506b4b030043f9ea) 	"S-ec0d9a0300f548e0"[30]		# lid 50 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa4a
caguid=0x506b4b030043fa4a
Ca	1 "H-506b4b030043fa4a"		# "gpu036 HCA-1"
[1](506b4b030043fa4a) 	"S-ec0d9a0300f548e0"[32]		# lid 36 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa9a
caguid=0x506b4b030043fa9a
Ca	1 "H-506b4b030043fa9a"		# "gpu035 HCA-1"
[1](506b4b030043fa9a) 	"S-ec0d9a0300f548e0"[31]		# lid 47 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa62
caguid=0x506b4b030043fa62
Ca	1 "H-506b4b030043fa62"		# "gpu031 HCA-1"
[1](506b4b030043fa62) 	"S-ec0d9a0300f548e0"[27]		# lid 14 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041cf72
caguid=0x506b4b030041cf72
Ca	1 "H-506b4b030041cf72"		# "gpu033 HCA-1"
[1](506b4b030041cf72) 	"S-ec0d9a0300f548e0"[29]		# lid 10 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa42
caguid=0x506b4b030043fa42
Ca	1 "H-506b4b030043fa42"		# "gpu032 HCA-1"
[1](506b4b030043fa42) 	"S-ec0d9a0300f548e0"[28]		# lid 12 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa9ba
caguid=0x506b4b03003fa9ba
Ca	1 "H-506b4b03003fa9ba"		# "gpu030 HCA-1"
[1](506b4b03003fa9ba) 	"S-ec0d9a0300f548e0"[26]		# lid 22 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa0e
caguid=0x506b4b030043fa0e
Ca	1 "H-506b4b030043fa0e"		# "gpu029 HCA-1"
[1](506b4b030043fa0e) 	"S-ec0d9a0300f548e0"[25]		# lid 44 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa2a
caguid=0x506b4b030043fa2a
Ca	1 "H-506b4b030043fa2a"		# "gpu026 HCA-1"
[1](506b4b030043fa2a) 	"S-ec0d9a0300f548e0"[22]		# lid 18 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa3a
caguid=0x506b4b030043fa3a
Ca	1 "H-506b4b030043fa3a"		# "gpu028 HCA-1"
[1](506b4b030043fa3a) 	"S-ec0d9a0300f548e0"[24]		# lid 20 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa7e
caguid=0x506b4b030043fa7e
Ca	1 "H-506b4b030043fa7e"		# "gpu027 HCA-1"
[1](506b4b030043fa7e) 	"S-ec0d9a0300f548e0"[23]		# lid 16 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa02
caguid=0x506b4b030043fa02
Ca	1 "H-506b4b030043fa02"		# "gpu025 HCA-1"
[1](506b4b030043fa02) 	"S-ec0d9a0300f548e0"[21]		# lid 9 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa4e
caguid=0x506b4b030043fa4e
Ca	1 "H-506b4b030043fa4e"		# "gpu024 HCA-1"
[1](506b4b030043fa4e) 	"S-ec0d9a0300f548e0"[20]		# lid 13 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa06
caguid=0x506b4b030043fa06
Ca	1 "H-506b4b030043fa06"		# "gpu023 HCA-1"
[1](506b4b030043fa06) 	"S-ec0d9a0300f548e0"[19]		# lid 30 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9fa
caguid=0x506b4b030043f9fa
Ca	1 "H-506b4b030043f9fa"		# "gpu021 HCA-1"
[1](506b4b030043f9fa) 	"S-ec0d9a0300f548e0"[17]		# lid 27 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa0a
caguid=0x506b4b030043fa0a
Ca	1 "H-506b4b030043fa0a"		# "gpu022 HCA-1"
[1](506b4b030043fa0a) 	"S-ec0d9a0300f548e0"[18]		# lid 43 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x43f720300da0d80
caguid=0x43f720300da0d80
Ca	1 "H-043f720300da0d80"		# "gpu044 HCA-1"
[1](43f720300da0d80) 	"S-ec0d9a0300f548e0"[16]		# lid 98 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x43f720300da0bd0
caguid=0x43f720300da0bd0
Ca	1 "H-043f720300da0bd0"		# "gpu043 HCA-1"
[1](43f720300da0bd0) 	"S-ec0d9a0300f548e0"[15]		# lid 97 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x43f720300da2714
caguid=0x43f720300da2714
Ca	1 "H-043f720300da2714"		# "gpu041 HCA-1"
[1](43f720300da2714) 	"S-ec0d9a0300f548e0"[13]		# lid 95 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x43f720300da2370
caguid=0x43f720300da2370
Ca	1 "H-043f720300da2370"		# "gpu042 HCA-1"
[1](43f720300da2370) 	"S-ec0d9a0300f548e0"[14]		# lid 96 lmc 0 "SwitchIB Mellanox Technologies" lid 19 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041d022
caguid=0x506b4b030041d022
Ca	1 "H-506b4b030041d022"		# "node039 HCA-1"
[1](506b4b030041d022) 	"S-ec0d9a0300f548c0"[36]		# lid 71 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b0300167328
caguid=0x506b4b0300167328
Ca	1 "H-506b4b0300167328"		# "node037 HCA-1"
[1](506b4b0300167328) 	"S-ec0d9a0300f548c0"[35]		# lid 68 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041d0d6
caguid=0x506b4b030041d0d6
Ca	1 "H-506b4b030041d0d6"		# "node035 HCA-1"
[1](506b4b030041d0d6) 	"S-ec0d9a0300f548c0"[34]		# lid 88 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa76
caguid=0x506b4b030043fa76
Ca	1 "H-506b4b030043fa76"		# "node033 HCA-1"
[1](506b4b030043fa76) 	"S-ec0d9a0300f548c0"[33]		# lid 82 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9c2
caguid=0x506b4b030043f9c2
Ca	1 "H-506b4b030043f9c2"		# "node031 HCA-1"
[1](506b4b030043f9c2) 	"S-ec0d9a0300f548c0"[32]		# lid 85 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa996
caguid=0x506b4b03003fa996
Ca	1 "H-506b4b03003fa996"		# "node027 HCA-1"
[1](506b4b03003fa996) 	"S-ec0d9a0300f548c0"[30]		# lid 73 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041d01e
caguid=0x506b4b030041d01e
Ca	1 "H-506b4b030041d01e"		# "node029 HCA-1"
[1](506b4b030041d01e) 	"S-ec0d9a0300f548c0"[31]		# lid 80 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa9be
caguid=0x506b4b03003fa9be
Ca	1 "H-506b4b03003fa9be"		# "node025 HCA-1"
[1](506b4b03003fa9be) 	"S-ec0d9a0300f548c0"[29]		# lid 84 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9ce
caguid=0x506b4b030043f9ce
Ca	1 "H-506b4b030043f9ce"		# "node023 HCA-1"
[1](506b4b030043f9ce) 	"S-ec0d9a0300f548c0"[28]		# lid 56 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9ca
caguid=0x506b4b030043f9ca
Ca	1 "H-506b4b030043f9ca"		# "node021 HCA-1"
[1](506b4b030043f9ca) 	"S-ec0d9a0300f548c0"[27]		# lid 58 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa96
caguid=0x506b4b030043fa96
Ca	1 "H-506b4b030043fa96"		# "login01 HCA-1"
[1](506b4b030043fa96) 	"S-ec0d9a0300f548c0"[26]		# lid 42 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa82
caguid=0x506b4b030043fa82
Ca	1 "H-506b4b030043fa82"		# "bee02 HCA-1"
[1](506b4b030043fa82) 	"S-ec0d9a0300f548c0"[12]		# lid 38 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa8a
caguid=0x506b4b030043fa8a
Ca	1 "H-506b4b030043fa8a"		# "bee01 HCA-1"
[1](506b4b030043fa8a) 	"S-ec0d9a0300f548c0"[11]		# lid 39 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041cfd2
caguid=0x506b4b030041cfd2
Ca	1 "H-506b4b030041cfd2"		# "node022 HCA-1"
[1](506b4b030041cfd2) 	"S-ec0d9a0300f548c0"[9]		# lid 77 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa16
caguid=0x506b4b030043fa16
Ca	1 "H-506b4b030043fa16"		# "node024 HCA-1"
[1](506b4b030043fa16) 	"S-ec0d9a0300f548c0"[10]		# lid 90 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa992
caguid=0x506b4b03003fa992
Ca	1 "H-506b4b03003fa992"		# "node026 HCA-1"
[1](506b4b03003fa992) 	"S-ec0d9a0300f548c0"[7]		# lid 79 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b03003fa966
caguid=0x506b4b03003fa966
Ca	1 "H-506b4b03003fa966"		# "node028 HCA-1"
[1](506b4b03003fa966) 	"S-ec0d9a0300f548c0"[8]		# lid 52 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9d6
caguid=0x506b4b030043f9d6
Ca	1 "H-506b4b030043f9d6"		# "node032 HCA-1"
[1](506b4b030043f9d6) 	"S-ec0d9a0300f548c0"[6]		# lid 54 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9d2
caguid=0x506b4b030043f9d2
Ca	1 "H-506b4b030043f9d2"		# "node030 HCA-1"
[1](506b4b030043f9d2) 	"S-ec0d9a0300f548c0"[5]		# lid 87 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9a6
caguid=0x506b4b030043f9a6
Ca	1 "H-506b4b030043f9a6"		# "node036 HCA-1"
[1](506b4b030043f9a6) 	"S-ec0d9a0300f548c0"[4]		# lid 53 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041d026
caguid=0x506b4b030041d026
Ca	1 "H-506b4b030041d026"		# "node034 HCA-1"
[1](506b4b030041d026) 	"S-ec0d9a0300f548c0"[3]		# lid 59 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030041d032
caguid=0x506b4b030041d032
Ca	1 "H-506b4b030041d032"		# "node040 HCA-1"
[1](506b4b030041d032) 	"S-ec0d9a0300f548c0"[2]		# lid 64 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043fa5a
caguid=0x506b4b030043fa5a
Ca	1 "H-506b4b030043fa5a"		# "node038 HCA-1"
[1](506b4b030043fa5a) 	"S-ec0d9a0300f548c0"[1]		# lid 81 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
vendid=0x2c9
devid=0x1017
sysimgguid=0x506b4b030043f9e2
caguid=0x506b4b030043f9e2
Ca	1 "H-506b4b030043f9e2"		# "controller mlx5_0"
[1](506b4b030043f9e2) 	"S-ec0d9a0300f548c0"[25]		# lid 34 lmc 0 "SwitchIB Mellanox Technologies" lid 29 4xEDR
"""


app = Flask(
    __name__, template_folder="templates", static_folder="static", static_url_path="/"
)

def plot_graph(text):
    """
    This method will plot a graph.
    """

    switch_regex = r"(Switch|Ca)\s+([0-9]+)\s+\"([SH]-[0-9a-z]+)\"\s+#\s*\"(.*)\".*\n?(\[[0-9]+\].*\n)*"
    link_regex = r"\[([0-9]+)\].*\"([SH]-[0-9a-z]+)\".*\[([0-9]+)\].*#\s*\"(.*)\""
    matches = re.finditer(switch_regex, text, re.MULTILINE)

    nodes = {}
    edges = {}
    
    for switch_match in matches:
        ports = switch_match.group(2)
        uid = switch_match.group(3)
        name = switch_match.group(4)
        nodes[uid] = {"name": name, "ports": ports, "type": uid[0]}

        for link_match in re.finditer(link_regex, switch_match.group(0)):
            interface = link_match.group(1)
            target_uid = link_match.group(2)
            target_interface = link_match.group(3)
            target_name = link_match.group(4)

            edge_uid = tuple(sorted([uid, target_uid]))
            edge_count = edges.get(edge_uid, 0)
            edges[edge_uid] = edge_count + 1

    nodes = [{"id": uid, **data} for uid, data in nodes.items()]
    links = [{"source": source, "target": target, "count": count // 2} for (source, target), count in edges.items()]

    graph = {"nodes": nodes, "links": links}
    return jsonify(graph)



@app.errorhandler(Exception)
def wrap_errors(error):
    """Decorator to wrap errors in a JSON response."""
    if app.debug:
        raise error
    return jsonify({"message": str(error)}), 500

@app.route('/')
def index_route():
    # Display the graph
    return render_template("index.html", content="", settings=settings)

@app.route('/graph')
def graph_route():
    # Display the graph

    # data = subprocess.check_output(["ibnetdiscover"])
    # text = data.decode("utf-8")
    return plot_graph(text)

if __name__ == '__main__':
    plot_graph(text)