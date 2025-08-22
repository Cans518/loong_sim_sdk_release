import time
import numpy as np
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("..")
from sdk.loong_jnt_sdk.loong_jnt_sdk_datas import jntSdkSensDataClass, jntSdkCtrlDataClass

jntNum=31
fingerDofLeft=6
fingerDofRight=6

useUdp=2  # 0=共享内存  1=udp   2=纯Python版udp

if(useUdp==0):   # 共享内存版，仅可本机运行，亚毫秒级延迟，最高1khz，且需匹配目录层级（父级含config目录），否则报错！！
	from sdk.loong_jnt_sdk.loong_jnt_sdk_shm import jntSdkClass
	sdk=jntSdkClass(jntNum, fingerDofLeft, fingerDofRight)
elif(useUdp==1): # udp版，毫秒级延时，最高200hz
	from sdk.loong_jnt_sdk.loong_jnt_sdk_udp import jntSdkClass
	sdk=jntSdkClass('0.0.0.0',8006, jntNum, fingerDofLeft, fingerDofRight)
	sdk.waitSens()
elif(useUdp==2): # 纯Python版，毫秒级延时，最高200hz
	from sdk.loong_jnt_sdk.loong_jnt_sdk_udp2 import jntSdkClass
	sdk=jntSdkClass('172.18.175.239',8006, jntNum, fingerDofLeft, fingerDofRight)
	sdk.waitSens()
	
while True:
    sens=sdk.recv()
    sens.print()
    time.sleep(0.02)  # 模拟控制频率