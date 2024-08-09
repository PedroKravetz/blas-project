import numpy as np
import pandas as pd
import os
import io
import time
from PIL import Image as im 
from flask import Flask, request, jsonify, redirect
from io import StringIO
from datetime import datetime
import threading
import psutil

import base64
from io import BytesIO

current_directory = os.getcwd()

print("Reading Start")
h1 = np.array(pd.read_csv(current_directory+'\\h1.csv', header=None, delimiter=','))
h2 = np.array(pd.read_csv(current_directory+'\\h2.csv', header=None, delimiter=','))
g1 = np.array(pd.read_csv(current_directory+'\\G-1.csv', header=None, delimiter=';'))
print("Reading Finished")

print(f"Norm of h1: {np.linalg.norm(h1)}")
print(f"Norm of h2: {np.linalg.norm(h2)}")
print(f"Norm of g1: {np.linalg.norm(g1)}")

'''
def cgnr(g, h):
    cgnr_cpu = []
    cgnr_mem = []
    i = 0
    f0 = 0
    r0 = g
    z0 = h.transpose().dot(r0)
    p0=z0
    while (1):
        i+=1
        print(f"i: {i}")
        w=h.dot(p0)
        nz0 = np.linalg.norm(z0)
        nw = np.linalg.norm(w)
        a = (nz0*nz0)/(nw*nw) 
        f1 = f0 + a*(p0)
        r1 = r0 - a*(w)
        z1 = h.transpose().dot(r1)
        nz1 = np.linalg.norm(z1)
        b = (nz1*nz1)/(nz0*nz0)
        p0 = z1 + b*p0
        f0=f1
        z0=z1
        cgnr_cpu.append(psutil.cpu_percent(interval=1))
        cgnr_mem.append(psutil.virtual_memory().percent)
        if (abs(np.linalg.norm(r1) - np.linalg.norm(r0)) < 0.0001):
            if np.size(f1) == 900:
                array2 = np.reshape(f1, (30, 30)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgnr30x30.png') 
            elif np.size(f1) == 3600:
                array2 = np.reshape(f1, (60, 60)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgnr60x60.png') 
            mcpu = max(cgnr_cpu)
            mmem = max(cgnr_mem)
            return mcpu, mmem
        r0=r1

def cgne(g, h):
    cgne_cpu = []
    cgne_mem = []
    f0 = 0
    r0 = g
    p0 = h.transpose().dot(r0)
    i=0
    while (1):
        i+=1
        print(f"i: {i}")
        a0 = (r0.transpose().dot(r0))/(p0.transpose().dot(p0))
        f1 = f0 + a0*p0
        r1 = r0 - a0*h.dot(p0)
        b0 = (r1.transpose().dot(r1))/(r0.transpose().dot(r0))
        p1 = h.transpose().dot(r1) + b0*p0
        cgne_cpu.append(psutil.cpu_percent(interval=1))
        cgne_mem.append(psutil.virtual_memory().percent)
        if (abs(np.linalg.norm(r1)-np.linalg.norm(r0))<0.0001):
            if np.size(f1) == 900:
                array2 = np.reshape(f1, (30, 30)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                #print(img_str)
                data2.save('cgne30x30.png')
            elif np.size(f1) == 3600:
                array2 = np.reshape(f1, (60, 60)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                #print(img_str)
                data2.save('cgne60x60.png') 
            mcpu = max(cgne_cpu)
            mmem = max(cgne_mem)
            return mcpu, mmem
        p0 = p1
        r0 = r1
        f0 = f1


alg_cgnr = True
print("[ 1 ] CGNR")
print("[ 2 ] CGNE")
alg = input("Your choice: ")

if alg == "1":
    alg_cgnr = True
elif alg == "2":
    alg_cgnr = False
else:
    print("Default is CGNR\n")

print("[ 1 ] 60X60 A-60x60-1")
print("[ 2 ] 60X60 G-1")
print("[ 3 ] 60X60 G-2")
print("[ 4 ] 30X30 A-30x30-1")
print("[ 5 ] 30X30 g-30x30-1")
print("[ 6 ] 30X30 g-30x30-2")
choice = input("Your choice: ")

if choice == "1":
    print("Reading Start")
    h = np.array(pd.read_csv(current_directory+'\\h1.csv', header=None, delimiter=','))
    g = np.array(pd.read_csv(current_directory+'\\A-60x60-1.csv', header=None, delimiter=';'))
    print("Reading Finished")
elif choice == "2":
    print("Reading Start")
    h = np.array(pd.read_csv(current_directory+'\\h1.csv', header=None, delimiter=','))
    g = np.array(pd.read_csv(current_directory+'\\G-1.csv', header=None, delimiter=';'))
    print("Reading Finished")
elif choice == "3":
    print("Reading Start")
    h = np.array(pd.read_csv(current_directory+'\\h1.csv', header=None, delimiter=','))
    g = np.array(pd.read_csv(current_directory+'\\G-2.csv', header=None, delimiter=';'))
    print("Reading Finished")
elif choice == "4":
    print("Reading Start")
    h = np.array(pd.read_csv(current_directory+'\\h2.csv', header=None, delimiter=','))
    g = np.array(pd.read_csv(current_directory+'\\A-30x30-1.csv', header=None, delimiter=';'))
    print("Reading Finished")
elif choice == "5":
    print("Reading Start")
    h = np.array(pd.read_csv(current_directory+'\\h2.csv', header=None, delimiter=','))
    g = np.array(pd.read_csv(current_directory+'\\g-30x30-1.csv', header=None, delimiter=';'))
    print("Reading Finished")
elif choice == "6":
    print("Reading Start")
    h = np.array(pd.read_csv(current_directory+'\\h2.csv', header=None, delimiter=','))
    g = np.array(pd.read_csv(current_directory+'\\g-30x30-2.csv', header=None, delimiter=';'))
    print("Reading Finished")
else:
    print("Default is 30X30 g-30x30-2")
    print("Reading Start")
    h = np.array(pd.read_csv(current_directory+'\\h2.csv', header=None, delimiter=','))
    g = np.array(pd.read_csv(current_directory+'\\g-30x30-2.csv', header=None, delimiter=';'))
    print("Reading Finished")

start_cpu = []
middle_cpu = []
end_cpu = []
start_mem = []
middle_mem = []
end_mem = []

if alg_cgnr:
    #for k in range(0,100):
    for k in range(0,10):
        print(f"CGNR Round {k}")
        start_cpu.append(psutil.cpu_percent(interval=1))
        start_mem.append(psutil.virtual_memory().percent)
        mcpu, mmem = cgnr(g, h)
        middle_cpu.append(mcpu)
        middle_mem.append(mmem)
        end_cpu.append(psutil.cpu_percent(interval=1))
        end_mem.append(psutil.virtual_memory().percent)
else:
    for k in range(0,10):
        print(f"CGNE Round {k}")
        start_cpu.append(psutil.cpu_percent(interval=1))
        start_mem.append(psutil.virtual_memory().percent)
        mcpu, mmem = cgne(g, h)
        middle_cpu.append(mcpu)
        middle_mem.append(mmem)
        end_cpu.append(psutil.cpu_percent(interval=1))
        end_mem.append(psutil.virtual_memory().percent)

print("---")
print(f"MAX Start CPU: {max(start_cpu)}")
print(f"MIN Start CPU: {min(start_cpu)}")
print(f"Mean of Start CPU : {sum(start_cpu)/len(start_cpu)}")
print("---")
print(f"MAX Middle CPU: {max(middle_cpu)}")
print(f"MIN Middle CPU: {min(middle_cpu)}")
print(f"Mean of Middle CPU : {sum(middle_cpu)/len(middle_cpu)}")
print("---")
print(f"MAX End CPU: {max(end_cpu)}")
print(f"MIN End CPU: {min(end_cpu)}")
print(f"Mean of End CPU : {sum(end_cpu)/len(end_cpu)}")
print("---")
print(f"MAX Start MEM: {max(start_mem)}")
print(f"MIN Start MEM: {min(start_mem)}")
print(f"Mean of Start MEM : {sum(start_mem)/len(start_mem)}")
print("---")
print(f"MAX Middle MEM: {max(middle_mem)}")
print(f"MIN Middle MEM: {min(middle_mem)}")
print(f"Mean of Middle MEM : {sum(middle_mem)/len(middle_mem)}")
print("---")
print(f"MAX End MEM: {max(end_mem)}")
print(f"MIN End MEM: {min(end_mem)}")
print(f"Mean of End MEM : {sum(end_mem)/len(end_mem)}")


'''