#!/usr/bin/env python3
# coding=utf-8
'''=========== ***doc description @ yyp*** ===========
Copyright 2025 人形机器人（上海）有限公司, https://www.openloong.net/
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
Author: YYP

udp通信，可多机联调，存在毫秒级不等的延时
纯Python实现，不依赖C++库
======================================================'''

import socket
import time
import threading
from loong_jnt_sdk_datas import jntSdkSensDataClass, jntSdkCtrlDataClass

class jntSdkClass:
    def __init__(self, ip: str, port: int, jntNum, fingerDofLeft, fingerDofRight):
        # 创建UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)  # 设置接收超时
        
        # 绑定本地端口（任意可用端口）
        self.sock.bind(('0.0.0.0', 0))
        
        # 设置目标地址和端口
        self.target_addr = (ip, port)
        
        # 初始化传感数据类
        self.sens = jntSdkSensDataClass(jntNum, fingerDofLeft, fingerDofRight)
        
        # 创建接收缓冲区
        self.recv_buffer = bytearray(2048)
        
        # 创建接收线程和缓冲区锁
        self.buffer_lock = threading.Lock()
        self.latest_data = None
        self.running = True
        self.recv_thread = threading.Thread(target=self._receive_loop)
        self.recv_thread.daemon = True
        self.recv_thread.start()
    
    def _receive_loop(self):
        """后台接收线程，持续接收数据并更新最新数据"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                with self.buffer_lock:
                    self.latest_data = data
            except socket.timeout:
                pass
            except Exception as e:
                print(f"接收错误: {e}")
    
    def send(self, ctrl: jntSdkCtrlDataClass):
        """发送控制数据"""
        try:
            buf = ctrl.packData()
            self.sock.sendto(buf, self.target_addr)
        except Exception as e:
            print(f"发送错误: {e}")
    
    def waitSens(self):
        """等待连接并接收第一个有效的传感数据"""
        self.send(jntSdkCtrlDataClass(31, 1, 1))
        while True:
            time.sleep(0.5)
            print("sdk等待连接...")
            sens = self.recv()
            if sens.timestamp > 0:
                break
    
    def recv(self) -> jntSdkSensDataClass:
        """接收传感数据"""
        with self.buffer_lock:
            data = self.latest_data
        
        if data:
            self.sens.unpackData(data)
        return self.sens
    
    def __del__(self):
        """析构函数，清理资源"""
        self.running = False
        if hasattr(self, 'recv_thread') and self.recv_thread.is_alive():
            self.recv_thread.join(1.0)  # 等待接收线程结束，最多1秒
        if hasattr(self, 'sock'):
            self.sock.close()
