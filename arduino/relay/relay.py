#*-* coding:UTF-8*-*

"""
    Este trasto actúa como relé, reenvía los datos de los sensores al servdiro de test.
"""


import serial
import requests
import time
import sys
import json
import queue
import threading
import random


#Esta clase se encarga de conseguir los datos
class Worker(threading.Thread):     
    def generate_rnd_msg(self):
        self.rnd_msg = {}
        msgs = ['!data>']
        self.rnd_msg['msg'] = msgs[0]
        self.rnd_msg['data'] = 'temp!24:hum!53'

    def get_msg(self):
        if self.source == 'serial':
            msg = self.ser.readline().decode()[:-2]
        if self.source == 'mock':
            time.sleep(5)
            self.generate_rnd_msg()
            msg = self.rnd_msg['msg']
        return msg
        
    def get_data(self):
        if self.source == 'serial':
            data = self.ser.readline().decode()[:-2] 
        if self.source == 'mock':
            data = self.rnd_msg['data']
        return data
        
    def run(self):
        #source indica que clase se usa para conseguir los datos (arduino via serie o mock)
        self.source = self._kwargs['source']
        
        if self.source == 'mock':
            self.rnd_msg = {}
        
        if self.source == 'serial':
            self.port = input("Serial port: ")
            self.ser = serial.Serial("/dev/tty"+self.port, 9600)
            
        while True:
            msg = self.get_msg()
            if msg == "!data>": 
                cmd = {'msg': 'data', 'data':{}}
                data = self.get_data()
                for pair in data.split(":"): 
                    k,v = pair.split("!")
                    cmd['data'][k] = v
                q.put(cmd)


#La parte que envía los datos al server por un lado
with open("relay_cfg.json", "r") as f:
    cfg = json.load(f)

baseurl = cfg['URL']
soil_endpoint = baseurl+'/insertar'


def new_measure(data):
    r = requests.post(soil_endpoint, data=json.dumps({'data':data}))
    print(r.text)

#cola de trabajos
q = queue.Queue()

#lanzar worker thread
t = Worker(kwargs={'source': 'mock'})
t.start()
while True:
    cmd = q.get()
    print(cmd)
    if cmd['msg'] == "data": 
        #print(cmd['data'])
        new_measure(cmd['data'])

    q.task_done()
