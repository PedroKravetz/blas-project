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

#print("Reading Start")
h1 = np.array(pd.read_csv(current_directory+'/h1.csv', header=None, delimiter=','))
h2 = np.array(pd.read_csv(current_directory+'/h2.csv', header=None, delimiter=','))
#print("Reading Finished")

active_clients = 0
waiting_clients = 0
# test_rounds > 2, how many times exec alg to determine cpu and mem
# dif > 0, determine difference allowed between default and test
# cpu_cap and mem_cap > max cpu/mem usage
test_rounds = 5
dif = 2.0
cpu_cap = 80.0
mem_cap = 90.0

# sinal G1, G2, A60, g1, g2, A30
cgnr_cpus = [16.414, 18.2, 20.03, 3.40, 4.31, 4.23]
cgnr_mems = [31.56, 34.37, 34.46, 5.10, 4.87, 4.81]

cgne_cpus = [11.1, 11.08, 16.44, 2.12, 2.42, 13.55]
cgne_mems = [0.02, 0.06, 0.06, 0.02, 0.0, 0.06]
sleep_times = [20, 8, 8, 5, 5, 10]


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
        
        # first cgnr
        time.sleep(15)
        start_cpu.append(psutil.cpu_percent(interval=0.1))
        start_mem.append(psutil.virtual_memory().percent)
        if i < 3:
            mcpu, mmem = det_cgnr(g, h1)
        else:
            mcpu, mmem = det_cgnr(g, h2)

        if abs(mcpu - start_cpu[0]) >= (cgnr_cpus[i] - dif) and abs(mcpu - start_cpu[0]) <= (cgnr_cpus[i] + dif) and abs(mmem - start_mem[0]) >= (cgnr_mems[i] - dif) and abs(mmem - start_mem[0]) <= (cgnr_mems[i] + dif):
            # if close to default values, theres no need to change
            start_cpu.clear()
            start_mem.clear()
        else:
            # needs to change
            mid_cpu.append(mcpu)
            mid_mem.append(mmem)
            for j in range(0,test_rounds-1):
                start_cpu.append(psutil.cpu_percent(interval=0.1))
                start_mem.append(psutil.virtual_memory().percent)
                if i < 3:
                    mcpu, mmem = det_cgnr(g, h1)
                else:
                    mcpu, mmem = det_cgnr(g, h2)
                mid_cpu.append(mcpu)
                mid_mem.append(mmem)
                time.sleep(5)
           
            cgnr_cpus[i] = abs((sum(mid_cpu)/len(mid_cpu)) - (sum(start_cpu)/len(start_cpu)))
            cgnr_mems[i] = abs((sum(mid_mem)/len(mid_mem)) - (sum(start_mem)/len(start_mem)))
            start_cpu.clear()
            start_mem.clear()
            mid_cpu.clear()
            mid_mem.clear()
        
        # second cgne
        time.sleep(15)
        start_cpu.append(psutil.cpu_percent(interval=0.1))
        start_mem.append(psutil.virtual_memory().percent)
        if i < 3:
            mcpu, mmem = det_cgne(g, h1)
        else:
            mcpu, mmem = det_cgne(g, h2)

        if abs(mcpu - start_cpu[0]) >= (cgne_cpus[i] - dif) and abs(mcpu - start_cpu[0]) <= (cgne_cpus[i] + dif) and abs(mmem - start_mem[0]) >= (cgne_mems[i] - dif) and abs(mmem - start_mem[0]) <= (cgne_mems[i] + dif):
            # if close to default values, theres no need to change
            start_cpu.clear()
            start_mem.clear()
        else:
            # needs to change
            mid_cpu.append(mcpu)
            mid_mem.append(mmem)
            for j in range(0,test_rounds-1):
                start_cpu.append(psutil.cpu_percent(interval=0.1))
                start_mem.append(psutil.virtual_memory().percent)
                if i < 3:
                    mcpu, mmem = det_cgne(g, h1)
                else:
                    mcpu, mmem = det_cgne(g, h2)
                mid_cpu.append(mcpu)
                mid_mem.append(mmem)
                time.sleep(5)
           
            cgne_cpus[i] = abs((sum(mid_cpu)/len(mid_cpu)) - (sum(start_cpu)/len(start_cpu)))
            cgne_mems[i] = abs((sum(mid_mem)/len(mid_mem)) - (sum(start_mem)/len(start_mem)))
            start_cpu.clear()
            start_mem.clear()
            mid_cpu.clear()
            mid_mem.clear()
        g = []
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
                #print(img_str)
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
                #print(img_str)
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
    count = 0
    while (not permit):
        if count == 10:
            print(f"client still waiting, file {id}")
            print(f"Active clients: {active_clients}, waiting clients: {waiting_clients}")
            count = 0
        count += 1
        time.sleep(sleep_times[id])
        current_cpu = psutil.cpu_percent(interval=0.1)
        current_mem = psutil.virtual_memory().percent
        if active_clients == 0 or (alg == "cgnr" and (current_cpu + cgnr_cpus[id] <= cpu_cap and current_mem + cgnr_mems[id] <= mem_cap)) or (alg == "cgne" and (current_cpu + cgne_cpus[id] <= cpu_cap and current_mem + cgne_mems[id] <= mem_cap)):
            permit = True
            print(f"client exiting wait time {id}")
    waiting_clients -= 1


@app.post("/blas")
def control():
        global active_clients
        global waiting_clients

        dataInicio = datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f')[:-4]
        #semaphore.acquire()  # Bloqueia até que um permit esteja disponível
        json = request.json
        arquivo = json["arquivo"]
        if (int(json["performance"])==1):
            #semaphore.release()
            return redirect("http://localhost:5000/performance", code=302)
        
        matriz = np.array(json["sinal"])
        usuario = json["usuario"]
        modelo = int(json["modelo"])
        metodo = json["metodo"]

        if arquivo == "G-1":
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_mem = psutil.virtual_memory().percent
            if (metodo == "cgnr" and (current_cpu + cgnr_cpus[0] > cpu_cap or current_mem + cgnr_mems[0] > mem_cap)) or (metodo == "cgne" and (current_cpu + cgne_cpus[0] > cpu_cap or current_mem + cgne_mems[0] > mem_cap)):
                print("[] New client wait, file 0")
                waiting_clients += 1
                client_wait(0, metodo)
        elif arquivo == "G-2":
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_mem = psutil.virtual_memory().percent
            if (metodo == "cgnr" and (current_cpu + cgnr_cpus[1] > cpu_cap or current_mem + cgnr_mems[1] > mem_cap)) or (metodo == "cgne" and (current_cpu + cgne_cpus[1] > cpu_cap or current_mem + cgne_mems[1] > mem_cap)):
                print("[] New client wait, file 1")
                waiting_clients += 1
                client_wait(1, metodo)
        elif arquivo == "A-60x60-1":
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_mem = psutil.virtual_memory().percent
            if (metodo == "cgnr" and (current_cpu + cgnr_cpus[2] > cpu_cap or current_mem + cgnr_mems[2] > mem_cap)) or (metodo == "cgne" and (current_cpu + cgne_cpus[2] > cpu_cap or current_mem + cgne_mems[2] > mem_cap)):
                print("[] New client wait, file 2")
                waiting_clients += 1
                client_wait(2, metodo)
        elif arquivo == "g-30x30-1":
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_mem = psutil.virtual_memory().percent
            if (metodo == "cgnr" and (current_cpu + cgnr_cpus[3] > cpu_cap or current_mem + cgnr_mems[3] > mem_cap)) or (metodo == "cgne" and (current_cpu + cgne_cpus[3] > cpu_cap or current_mem + cgne_mems[3] > mem_cap)):
                print("[] New client wait, file 3")
                waiting_clients += 1
                client_wait(3, metodo)
        elif arquivo == "g-30x30-2":
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_mem = psutil.virtual_memory().percent
            if (metodo == "cgnr" and (current_cpu + cgnr_cpus[4] > cpu_cap or current_mem + cgnr_mems[4] > mem_cap)) or (metodo == "cgne" and (current_cpu + cgne_cpus[4] > cpu_cap or current_mem + cgne_mems[4] > mem_cap)):
                print("[] New client wait, file 4")
                waiting_clients += 1
                client_wait(4, metodo)
        elif arquivo == "A-30x30-1":
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_mem = psutil.virtual_memory().percent
            if (metodo == "cgnr" and (current_cpu + cgnr_cpus[5] > cpu_cap or current_mem + cgnr_mems[5] > mem_cap)) or (metodo == "cgne" and (current_cpu + cgne_cpus[5] > cpu_cap or current_mem + cgne_mems[5] > mem_cap)):
                print("[] New client wait, file 5")
                waiting_clients += 1
                client_wait(5, metodo)

        active_clients += 1
        print("> Dealing with a client")
        
        # print(usuario)
        # print(modelo)
        # print(g1)
        # print(matriz)
        inicio = 0
        fim =  0
        inicio= time.time()
        matriz = matriz.astype(np.float64)

        if (modelo == 1 and metodo == "cgnr"):
            #print("teste 1")
            #matriz = ganhoSinal1(matriz)
            #c = regularizacao1(matriz)
            #for x in range(matriz.size):
            #    matriz[x]=matriz[x]*c
            lista = cgnr(matriz, h1)
        elif (metodo == "cgnr"):
            #print("teste 2")
            #matriz = ganhoSinal2(matriz)
            #c = regularizacao2(matriz)
            #for x in range(matriz.size):
            #    matriz[x]=matriz[x]*c
            lista = cgnr(matriz, h2)
        elif(modelo == 1):
            lista = cgne(matriz, h1)
        else:
            lista = cgne(matriz, h2)
        fim=time.time()-inicio
        dataFinal = datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f')[:-4]
        #print(dataInicio)
        #print(dataFinal)
        #semaphore.release()
        #print("Terminou")
        active_clients -= 1
        print(f"Active clients: {active_clients}, waiting clients: {waiting_clients}")
        return {"sinal": lista[0].tolist(), "str": lista[2], "tempo": fim, "usuario": usuario, "interacoes": lista[1], "dataInicio": dataInicio, "dataFinal": dataFinal, "metodo":  metodo.upper()}, 200
        #return {"retorno": "verdadeiro"}, 200
    
@app.get("/performance")
def system_performance():
    #semaphore.acquire()
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    #semaphore.release()
    return{"cpu": cpu, "mem": mem.percent, "time": datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f')[:-4]}


#MAX_CONCURRENT_THREADS = 10
#semaphore = threading.Semaphore(MAX_CONCURRENT_THREADS)
choice = input("Press '1' to determine cpu and mem, else use default values.\n[>] Your choice: ")
if choice == "1":
    determine_cpu_mem()
    #print(f"cpus cgnr: {cgnr_cpus}")
    #print(f"mems cgnr: {cgnr_mems}")
    #print(f"cpus cgne: {cgne_cpus}")
    #print(f"mems cgne: {cgne_mems}")
app.run(host="localhost", port=5000)

#print(h1)
#print(g1)
#print(c1)
#print(regularizacao1)
#print(h2)
#print(g2)
#print(c2)
#print(regularizacao2)
#print(ganho2)
#print(cgnr(g1, h1))
#print(cgne(g1, h1))
#print(cgnr(g2, h2))