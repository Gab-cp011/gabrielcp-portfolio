from new_roots import *
import numpy as np
from tools import *
import pandas as pd
import math
from scipy.interpolate import interp1d
from print_functions import * # arquivo com métodos de prints para acompanhamento da simulação
from velocity_correction import * # método original de correção de velocidades
# Código reformulado do loop, em que o método de correção de velocidades foi colocado
# em outro arquivo python, para facilitar a leitura do código e organização.
# Nesse código está implementada a remoção da slope e com novos métodos de print
# para auxiliar no acompanhamento da simulação. Também estou usando-o para testar
# uma nova metodologia de predição de velocidades com base em raios futuros de curva
# Além de uma metodologia de suavização do raio com butterworth e filtragem pelo raio
# mínimo. A dúvida está sendo em como encaixar o método de predição no código
# pois quando tento realizar uma filtragem de velocidades com ele, acaba gerando bugs 
# no roots. 


def loop(fx,fy,x,y,z,P,m,Cl,Cd,Af,Crr,ld,lt,h,Tracao,Vo,
        Frenagem,Vmax,mu,nu,marcha=False,Ps=0,ns=0,finaldrive=0,
        gearslist=0,rw=0, use_z=False, radius_method=None,N=3, 
        fc=0.03, r_min=50,order=3):
    
    P = P*735.499

    if marcha:
        Ps = [i * 735.499 for i in Ps]
        pcurve = powercurve(Ps, ns, finaldrive, gearslist, rw)
        Pv = interp1d(pcurve[1], pcurve[0], fill_value='extrapolate')
    else:
        pcurve = []
        Pv = []

    g = 9.81
    x, y, z = [float(i) for i in x], [float(i) for i in y], [float(i) for i in z]

    if  radius_method is None:
        R = radiusXYZ(x, y, z)

    elif radius_method=='butter':
        R = radiusXYZ(x, y, z)
        
        print('Vetor de raios (índice -> valor):')
        for i, r in enumerate(R):
            print(f"{i:4d}: {r:.2f} m")
        print(f"Total de valores: {len(R)}")

    if use_z==False:
        D = distanceXYZ(x, y, use_z=use_z)
    else:
        D = distanceXYZ(x, y,z=z, use_z=True)

    angle = grading(z, D) if use_z else [0] * len(R)

    V = [Vo/3.6 + 0.0001]
    Vmax = Vmax/3.6
    meq = m*1.05

    rhoAR = 1.25
    kl = Cl*Af*rhoAR/2
    ka = Cd*Af*rhoAR/2
    k = (ka-kl*Crr)/meq
    
    # Teste para verificar com slope=0 
    if use_z:
        slope = [(i + Crr*math.cos(i)) * m / meq for i in angle]
    else: 
        slope=[0]*len(angle)

    Axmin = Frenagem*g*fx
    AxmaxL, AymaxL = [], []

    contagem_metodo = {
        "Correção por Torricelli Modificado": 0,
        "Correção por fórmula V1": 0
    }

    contagem_sucesso = {
        "Correção local (j=0) ": 0,
        "Correção retroativa (j>0) ": 0
    }



    for i in range(len(R)):
        Aymax = fy * (nu * g * math.cos(angle[i]) - kl * V[i]**2 / m)

        if Tracao == 'D':
            Axmax = lt * fx * ((mu * g * math.cos(angle[i]) - mu * kl * V[i]**2 / m) / (ld + h * mu + lt))
        else:
            Axmax = ld * fx * ((mu * g * math.cos(angle[i]) - mu * kl * V[i]**2 / m) / (ld - h * mu + lt))

        AxmaxL.append(Axmax)
        AymaxL.append(Aymax)

        #intervalo = Roots(V[i], D[i], R[i], Axmax, Axmin, Aymax, slope[i], g, k, pcurve, m, Pv, marcha, P, verbose=False)

        resultado_roots = Roots(V[i], D[i], R[i], AxmaxL[i], Axmin, AymaxL[i], slope[i], g, k, pcurve, m, Pv, marcha, P, verbose=False)

        #print_iteration_info(i, V[i], D[i], R[i], slope[i], Axmax, Aymax, resultado_roots)

        if resultado_roots != False:

            Viplus1 = resultado_roots[1][1]

            if Viplus1 > Vmax:
                Viplus1 = Vmax


            V.append(Viplus1)

            
        else:
                V = corrigir_velocidade(i, V, R, D, slope, AxmaxL, Axmin, AymaxL, k, g,
                    pcurve, m, Pv, marcha, P,mu, contagem_metodo, contagem_sucesso)

    Ay = [V[i + 1] ** 2 / R[i] for i in range(0, len(R))] # For V[0], Ay does not exist

    Ax = [(V[i + 1] ** 2 - V[i] ** 2) / (2 * D[i]) for i in range(0, len(R))] # Without interpolation

    Dcum = np.cumsum(D[:])

    #Definindo a direcao do deslocamento para alterar o sinal de Ay (Direita ou Esquerda):
    c = curva(x,y)
    
    Ay = [i1 * i2 for i1, i2 in zip(Ay, c)]

    Ax = [0] + Ax

    Ay = [0] + Ay

    df = pd.DataFrame ( [Dcum]+ [V] + [Ay]+[Ax]).transpose()

    df.columns = ['Distance', 'Speed','Ay','Ax']

    #Criando tempo:
    t= []
    for i in range(len(Ax)-2): 
        if Ax[i+1] == 0:
            t.append(D[i]/V[i])
        else:
            t.append((V[i+1]-V[i])/Ax[i+1])


    t = list(np.cumsum(t))
    t += [0] + [np.nan]
    df['Time'] = t
    df['Force'] = m*df.Ax
    
    #Caso nao tenho marcha:
    if marcha == False:
        return df
    #Analise das Marchas e rotacao do Motor
    else:
        gears = []
        Vs = pcurve[2]
        Vs = Vs[1:-1]
        print(Vs)
    for i in df.Speed:
        gear = False
        for j in list(range(0,len(Vs)))[::-1]: 
                if i>Vs[j]:
                    gear = j+2
                    break
        if gear == False:
            gear = 1

        gears.append(gear)

    df['Gears'] = gears

    gr = []
    listgear = list(range(1,len(gearslist)+1))

    for i in gears:
        gr.append(gearslist[listgear.index(i)])

    df['GRatios'] = gr
    enginerotation = []

    for i in range(0,len(df.Speed)):
        omega = df.Speed[i] * df.GRatios[i] * finaldrive * 30 / (rw *math.pi)

        if omega < 1000:
            omega = 1000

        enginerotation.append(omega)
        
    df['RPM'] = enginerotation

    return df