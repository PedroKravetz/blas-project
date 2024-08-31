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
app = Flask(__name__)

h1 = np.array(pd.read_csv(current_directory+'/h1.csv', header=None, delimiter=','))
h2 = np.array(pd.read_csv(current_directory+'/h2.csv', header=None, delimiter=','))

active_clients = 0
waiting_clients = 0
# test_rounds > 2, how many times exec alg to determine cpu and mem
# dif > 0, determine difference allowed between default and test
# cpu_cap and mem_cap > max cpu/mem usage
test_rounds = 2
cpu_cap = 80.0
mem_cap = 90.0

cgnr_cpus = []
cgnr_mems = []

def determine_cpu_mem():
    print("Start determine_cpu_mem")
    files = ['/G-1.csv', '/G-2.csv', '/A-60x60-1.csv', '/g-30x30-1.csv', '/g-30x30-2.csv', '/A-30x30-1.csv']
    start_cpu = []
    start_mem = []
    mid_cpu = []
    mid_mem = []
    for i in range(0,6):
        print(f"file: {files[i]}")
        g = np.array(pd.read_csv(current_directory+files[i], header=None, delimiter=';'))
      
        for j in range(0,test_rounds):
            start_cpu.append(psutil.cpu_percent(interval=0.1))
            start_mem.append(psutil.virtual_memory().percent)
            if i < 3:
                mcpu, mmem = det_cgnr(g, h1)
            else:
                mcpu, mmem = det_cgnr(g, h2)
            mid_cpu.append(mcpu)
            mid_mem.append(mmem)
            time.sleep(5)
           
        cgnr_cpus.append(abs((sum(mid_cpu)/len(mid_cpu)) - (sum(start_cpu)/len(start_cpu))))
        cgnr_mems.append(abs((sum(mid_mem)/len(mid_mem)) - (sum(start_mem)/len(start_mem))))
        start_cpu.clear()
        start_mem.clear()
        mid_cpu.clear()
        mid_mem.clear()
        time.sleep(15)
    cgnr_cpus.append(np.max(cgnr_cpus))
    cgnr_mems.append(np.max(cgnr_mems))
    print("End determine_cpu_mem")


def det_cgnr(g, h):
    cgnr_cpu = []
    cgnr_mem = []
    i = 0
    f0 = 0
    r0 = g
    z0 = h.transpose().dot(r0)
    p0=z0
    while (1):
        i+=1
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
        cgnr_cpu.append(psutil.cpu_percent(interval=0.1))
        cgnr_mem.append(psutil.virtual_memory().percent)
        if (abs(np.linalg.norm(r1) - np.linalg.norm(r0)) < 0.0001):
            if np.size(f1) == 900:
                array2 = np.reshape(f1, (30, 30)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                cgnr_cpu.append(psutil.cpu_percent(interval=0.1))
                cgnr_mem.append(psutil.virtual_memory().percent)
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgnr30x30.png') 
            elif np.size(f1) == 3600:
                array2 = np.reshape(f1, (60, 60)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                cgnr_cpu.append(psutil.cpu_percent(interval=0.1))
                cgnr_mem.append(psutil.virtual_memory().percent)
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgnr60x60.png') 
            mcpu = max(cgnr_cpu)
            mmem = max(cgnr_mem)
            return mcpu, mmem
        r0=r1

def det_cgne(g, h):
    cgne_cpu = []
    cgne_mem = []
    f0 = 0
    r0 = g
    p0 = h.transpose().dot(r0)
    i=0
    while (1):
        i+=1
        a0 = (r0.transpose().dot(r0))/(p0.transpose().dot(p0))
        f1 = f0 + a0*p0
        r1 = r0 - a0*h.dot(p0)
        b0 = (r1.transpose().dot(r1))/(r0.transpose().dot(r0))
        p1 = h.transpose().dot(r1) + b0*p0
        cgne_cpu.append(psutil.cpu_percent(interval=0.1))
        cgne_mem.append(psutil.virtual_memory().percent)
        if (abs(np.linalg.norm(r1)-np.linalg.norm(r0))<0.0001) or i >= 20:
            if np.size(f1) == 900:
                array2 = np.reshape(f1, (30, 30)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                cgne_cpu.append(psutil.cpu_percent(interval=0.1))
                cgne_mem.append(psutil.virtual_memory().percent)
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgne30x30.png')
            elif np.size(f1) == 3600:
                array2 = np.reshape(f1, (60, 60)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                cgne_cpu.append(psutil.cpu_percent(interval=0.1))
                cgne_mem.append(psutil.virtual_memory().percent)
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgne60x60.png') 
            mcpu = max(cgne_cpu)
            mmem = max(cgne_mem)
            return mcpu, mmem
        p0 = p1
        r0 = r1
        f0 = f1

def cgnr(g, h):
    i = 0
    f0 = 0
    r0 = g
    z0 = h.transpose().dot(r0)
    p0=z0
    while (1):
        i+=1
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
            return [f1, i, img_str]
        r0=r1

def cgne(g, h):
    f0 = 0
    r0 = g
    p0 = h.transpose().dot(r0)
    i=0
    while (1):
        i+=1
        a0 = (r0.transpose().dot(r0))/(p0.transpose().dot(p0))
        f1 = f0 + a0*p0
        r1 = r0 - a0*h.dot(p0)
        b0 = (r1.transpose().dot(r1))/(r0.transpose().dot(r0))
        p1 = h.transpose().dot(r1) + b0*p0
        if (abs(np.linalg.norm(r1)-np.linalg.norm(r0))<0.0001):
            if np.size(f1) == 900:
                array2 = np.reshape(f1, (30, 30)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgne30x30.png')
            elif np.size(f1) == 3600:
                array2 = np.reshape(f1, (60, 60)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                data2.save('cgne60x60.png') 
            return [f1, i, img_str]
        p0 = p1
        r0 = r1
        f0 = f1

def ganhoSinal1(matriz):
    ganho1 = 0
    for x in range(64):
        for y in range(794):
            ganho1 = 100 + 0.05*y*np.sqrt(y)
            matriz[(x*794)+y]=matriz[(x*794)+y]*ganho1
    return matriz

def ganhoSinal2(matriz):
    ganho2 = 0
    for x in range(64):
            for y in range(436):
                ganho2 = 100 + 0.05*y*np.sqrt(y)
                matriz[(x*436)+y]=matriz[(x*436)+y]*ganho2
    return matriz

def regularizacao1(matriz):
    regularizacao1=-1
    aux = h1.transpose().dot(matriz)
    for j in aux:
        for i in j:
            if (abs(i)>regularizacao1):
                regularizacao1=abs(i)
    regularizacao1*=0.1
    return regularizacao1

def regularizacao2(matriz):
    regularizacao1=-1
    aux = h2.transpose().dot(matriz)
    for j in aux:
        for i in j:
            if (abs(i)>regularizacao1):
                regularizacao1=abs(i)
    regularizacao1*=0.1
    return regularizacao1

def reducao(matriz):
    return np.linalg.norm(matriz.transpose().dot(matriz))


def client_wait(id, alg):
    global active_clients
    global waiting_clients
    permit = False
    while (not permit):
        semaphore7.acquire()
        current_cpu = psutil.cpu_percent(interval=0.1)
        current_mem = psutil.virtual_memory().percent
        if active_clients == 0 or (alg == "cgnr" and (current_cpu + cgnr_cpus[id] <= cpu_cap and current_mem + cgnr_mems[id] <= mem_cap)) or (alg == "cgne" and (current_cpu + cgne_cpus[id] <= cpu_cap and current_mem + cgne_mems[id] <= mem_cap)):
            permit = True
        semaphore7.release()
    waiting_clients -= 1


@app.post("/blas")
def control():
        global active_clients
        global waiting_clients
        print(f"Active clients: {active_clients}, waiting clients: {waiting_clients}")
        dataInicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

        json = request.json
        arquivo = json["arquivo"]
        if (int(json["performance"])==1):
            return redirect("http://localhost:5000/performance", code=302)
        
        matriz = np.array(json["sinal"])
        usuario = json["usuario"]
        modelo = int(json["modelo"])
        metodo = json["metodo"]

        current_cpu = psutil.cpu_percent(interval=0.1)
        current_mem = psutil.virtual_memory().percent

        if arquivo == "G-1":
            waiting_clients += 1
            t_wait = threading.Thread(target=client_wait,args=(0,metodo,))
            semaphore0.acquire()
            t_wait.start()
            t_wait.join()
            semaphore0.release()
        elif arquivo == "G-2":
            waiting_clients += 1
            t_wait = threading.Thread(target=client_wait,args=(1,metodo,))
            semaphore1.acquire()
            t_wait.start()
            t_wait.join()
            semaphore1.release()
        elif arquivo == "A-60x60-1":
            waiting_clients += 1
            t_wait = threading.Thread(target=client_wait,args=(2,metodo,))
            semaphore2.acquire()
            t_wait.start()
            t_wait.join()
            semaphore2.release()
        elif arquivo == "g-30x30-1":
            waiting_clients += 1
            t_wait = threading.Thread(target=client_wait,args=(3,metodo,))
            semaphore3.acquire()
            t_wait.start()
            t_wait.join()
            semaphore3.release()
        elif arquivo == "g-30x30-2":
            waiting_clients += 1
            t_wait = threading.Thread(target=client_wait,args=(4,metodo,))
            semaphore4.acquire()
            t_wait.start()
            t_wait.join()
            semaphore4.release()
        elif arquivo == "A-30x30-1":
            waiting_clients += 1
            t_wait = threading.Thread(target=client_wait,args=(5,metodo,))
            semaphore5.acquire()
            t_wait.start()
            t_wait.join()
            semaphore5.release()
        else:
            waiting_clients += 1
            t_wait = threading.Thread(target=client_wait,args=(6,metodo,))
            semaphore6.acquire()
            t_wait.start()
            t_wait.join()
            semaphore6.release()

        active_clients += 1
        print("> Dealing with a client")
        print(f"Active clients: {active_clients}, waiting clients: {waiting_clients}")
        
        inicio = 0
        fim =  0
        inicio= time.time()
        matriz = matriz.astype(np.float64)

        if (modelo == 1 and metodo == "cgnr"):
            lista = cgnr(matriz, h1)
        elif (metodo == "cgnr"):
            lista = cgnr(matriz, h2)
        elif(modelo == 1):
            lista = cgne(matriz, h1)
        else:
            lista = cgne(matriz, h2)
        fim=time.time()-inicio
        dataFinal = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
        active_clients -= 1
        print(f"Active clients: {active_clients}, waiting clients: {waiting_clients}")
        return {"sinal": lista[0].tolist(), "str": lista[2], "tempo": fim, "usuario": usuario, "interacoes": lista[1], "dataInicio": dataInicio, "dataFinal": dataFinal, "metodo":  metodo.upper(), "arquivo":arquivo}, 200
    
@app.get("/performance")
def system_performance():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return{"cpu": cpu, "mem": mem.percent, "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]}


semaphore0 = threading.Semaphore(1)
semaphore1 = threading.Semaphore(1)
semaphore2 = threading.Semaphore(1)
semaphore3 = threading.Semaphore(1)
semaphore4 = threading.Semaphore(1)
semaphore5 = threading.Semaphore(1)
semaphore6 = threading.Semaphore(1)
semaphore7 = threading.Semaphore(1)

determine_cpu_mem()
print(f"cpus cgnr: {cgnr_cpus}")
print(f"mems cgnr: {cgnr_mems}")
app.run(host="localhost", port=5000)