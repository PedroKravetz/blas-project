import numpy as np
import pandas as pd
import os
import io
import time
from PIL import Image as im 
from flask import Flask, request, jsonify
from io import StringIO
from datetime import datetime
import threading
import psutil

import base64
from io import BytesIO

current_directory = os.getcwd()
app = Flask(__name__)

print("Reading Start")
h1 = np.array(pd.read_csv(current_directory+'\\h1.csv', header=None, delimiter=','))
h2 = np.array(pd.read_csv(current_directory+'\\h2.csv', header=None, delimiter=','))
g1 = np.array(pd.read_csv(current_directory+'\\G-1.csv', header=None, delimiter=';'))
print("Reading Finished")
MAX_CONCURRENT_THREADS = 5
semaphore = threading.Semaphore(MAX_CONCURRENT_THREADS)

def normalize(l):
    c=0
    for j in l:
        for i in j:
            c+=i*i
    c=np.sqrt(c)
    return c

def cgnr(g, h):
    i = 0
    f0 = 0
    r0 = g
    z0 = h.transpose().dot(r0)
    p0=z0
    while (1):
        i+=1
        w=h.dot(p0)
        nz0 = normalize(z0)
        nw = normalize(w)
        a = (nz0*nz0)/(nw*nw) 
        f1 = f0 + a*(p0)
        r1 = r0 - a*(w)
        z1 = h.transpose().dot(r1)
        nz1 = normalize(z1)
        b = (nz1*nz1)/(nz0*nz0)
        p0 = z1 + b*p0
        f0=f1
        z0=z1
        if (abs(normalize(r1) - normalize(r0)) < 0.0001):
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
        if (abs(normalize(r1)-normalize(r0))<0.0001):
            if np.size(f1) == 900:
                array2 = np.reshape(f1, (30, 30)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                print(img_str)
                data2.save('cgne30x30.png')
            elif np.size(f1) == 3600:
                array2 = np.reshape(f1, (60, 60)).transpose()
                data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
                buffered = BytesIO()
                data2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())
                img_str = img_str.decode("utf-8")
                print(img_str)
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
    return normalize(matriz.transpose().dot(matriz))

@app.post("/blas")
def control():
        dataInicio = datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f')[:-4]
        semaphore.acquire()  # Bloqueia até que um permit esteja disponível

        print("> Dealing with a new client")
        
        json = request.json
        matriz = np.array(json["sinal"])
        usuario = json["usuario"]
        modelo = int(json["modelo"])
        # print(usuario)
        # print(modelo)
        # print(g1)
        # print(matriz)
        inicio = 0
        fim =  0
        matriz = matriz.astype(np.float64)

        if (modelo == 1):
            #print("teste 1")
            inicio= time.time()
            #matriz = ganhoSinal1(matriz)
            #c = regularizacao1(matriz)
            #for x in range(matriz.size):
            #    matriz[x]=matriz[x]*c
            lista = cgnr(matriz, h1)
        else:
            #print("teste 2")
            inicio= time.time()
            #matriz = ganhoSinal2(matriz)
            #c = regularizacao2(matriz)
            #for x in range(matriz.size):
            #    matriz[x]=matriz[x]*c
            lista = cgnr(matriz, h2)
        fim=time.time()-inicio
        dataFinal = datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f')[:-4]
        #print(dataInicio)
        #print(dataFinal)
        semaphore.release()
        #print("Terminou")
        return {"sinal": lista[0].tolist(), "str": lista[2], "tempo": fim, "usuario": usuario, "interacoes": lista[1], "dataInicio": dataInicio, "dataFinal": dataFinal}, 200
        #return {"retorno": "verdadeiro"}, 200
    
@app.get("/performance")
def system_performance():
    semaphore.acquire()
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    semaphore.release()
    return{"cpu": cpu, "mem": mem.percent, "time": datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f')[:-4]}

@app.route("/")
def hello_world():
    return "<p> Hello World!</p>"


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