import numpy as np
import pandas as pd
import os
from PIL import Image as im 

current_directory = os.getcwd()

def normalize(l):
    c=0
    for j in l:
        for i in j:
            c+=i*i
    c=np.sqrt(c)
    return c

def cgnr(g, h):
    f0 = 0
    r0 = g
    z0 = h.transpose().dot(r0)
    p0=z0
    while (1):
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
            array2 = np.reshape(f1, (60, 60)).transpose()
            data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
            data2.save('teste.png') 
            return f1
        r0=r1

def cgne(g, h):
    f0 = 0
    r0 = g
    p0 = h.transpose().dot(r0)
    while (1):
        a0 = (r0.transpose().dot(r0))/(p0.transpose().dot(p0))
        f1 = f0 + a0*p0
        r1 = r0 - a0*h.dot(p0)
        b0 = (r1.transpose().dot(r1))/(r0.transpose().dot(r0))
        p1 = h.transpose().dot(r1) + b0*p0
        if (abs(normalize(r1)-normalize(r0))<0.0001):
            array2 = np.reshape(f1, (60, 60)).transpose()
            data2 = im.fromarray((abs(array2*255)).astype(np.uint8))
            data2.save('teste2.png') 
            return f1
        p0 = p1
        r0 = r1
        f0 = f1

def ganhoSinal1(matriz):
    ganho1 = 0
    for x in range(65):
        if (x):
            for y in range(795):
                if (y):
                    ganho1 = 100 + 0.05*y*np.sqrt(y)
                    matriz[x-1][y-1]*=ganho1
    return matriz


h1 = np.array(pd.read_csv(current_directory+'\\h1.csv', header=None, delimiter=','))
h2 = np.array(pd.read_csv(current_directory+'\\h2.csv', header=None, delimiter=','))
g1 = np.array(pd.read_csv(current_directory+'\\G-1.csv', header=None, delimiter=';'))
g2 = np.array(pd.read_csv(current_directory+'\\A-30x30-1.csv', header=None, delimiter=';'))
aux = h1.transpose().dot(h1).transpose()
c1 = normalize(aux)
regularizacao1=-1
aux = h1.transpose().dot(g1)
for j in aux:
    for i in j:
        if (abs(i)>regularizacao1):
            regularizacao1=abs(i)
regularizacao1*=0.1





aux = h2.transpose().dot(h2).transpose()
c2 = normalize(aux)
regularizacao2=-1
aux = h2.transpose().dot(g2)
for j in aux:
    for i in j:
        if (abs(i)>regularizacao2):
            regularizacao2=abs(i)
regularizacao2*=0.1
ganho2 = 0
for x in range(65):
    if (x):
        for y in range(437):
            if (y):
                ganho2 = 100 + 0.05*y*np.sqrt(y)

print(h1)
print(g1)
print(c1)
print(regularizacao1)
print(h2)
print(g2)
print(c2)
print(regularizacao2)
print(ganho2)
print(cgnr(g1, h1))
print(cgne(g1, h1))
#print(cgnr(g2, h2))