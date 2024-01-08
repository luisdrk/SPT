import pandas as pd
import numpy as np
pga=0.28 #Peack ground accesk (g)
M= 6.9 #Earthquacke magnitude
d=1.8 #Water table depth (m)
PEdry= 19 #Average gamma above water table (kN/m3) 
PEsat=20 #Average gamma below water table (kN/m3) 
diam=100 #Borehole diammeter (mm)
Correction="NO" #Requires correction for sampler lineres (YES/NO)

df = pd.read_csv("C:/Users/lvillanes/Desktop\py/SPT_DATA.csv")
#headers: number;Depth;N;Flag;Fines_content;Energy_ratio
#Definimos CE
df["CE"]=df["Energy_ratio"]/60
#Definimos CB
if diam<115.1:
    df["CB"]=1
elif diam < 150.1:
    df["CB"]=1
else:
    df["CB"]=1.15


#Definimos CR
# Definir una función que aplique la fórmula a un valor de CR
def CR(valor):
    if (valor + 1.5) < 3:
        return 0.75
    elif (valor + 1.5) < 4:
        return 0.8
    elif (valor + 1.5) < 6:
        return 0.85
    elif (valor + 1.5) < 10:
        return 0.95
    else:
        return 1.0
# Aplicar la función a la columna y crear una nueva columna 'Resultado'
df["CR"] = df['Depth'].apply(CR)

#Definimos CS

if Correction=="NO":
     df["CS"]=1
else:
    df["CS"]="error"


# Defiimos N60

df["N60"]=df["N"]*df["CE"]*df["CB"]*df["CR"]*df["CS"]

#definimos el esfuerzo vc

def ESvc(valor):
    if valor < d:
        return valor * PEdry
    else:
        return d * PEdry + (valor-d)*PEsat

# Reemplaza B15, D6, E7 y E8 con los valores deseados
df["ESvc"] = df['Depth'].apply(ESvc)

#definimos el esfuerzo vc'

# Definir una función para calcular el resultado
def ESvce(r):
    g = 9.81
    max_value = max(r['Depth'] - d, 0)
    resultado = r['ESvc'] - max_value * g
    return resultado

# Aplicar la función a cada fila del DataFrame y crear una nueva columna 'Resultado'
df['ESvce'] = df.apply(ESvce, axis=1)
# Definimos la funcion CN
df['CN'] = 1
df["N160"]=1
def CN (a):
    if a['N160']=="n.a":
        minimo=46
    else:
        minimo=min(a['N160'],46)
    resultado=min(1.7,(101/a['ESvce'])**(0.784-0.0768*np.sqrt(minimo)))
    return resultado

def N160 (a):
    if a['Flag'] == "Clay":
        return "n.a"
    else:
        return a['N60']*a['CN']

for i in range(500):
    df['CN'] = df.apply(CN,axis=1)
    df['N160'] = df.apply(N160,axis=1)
###########################################################
def deltaN(a):
    if a['Flag'] == "Clay":
        return "n.a"
    else:
        resultado = np.exp(1.63 + 9.7 / (a['Fines_content'] + 0.01) - (15.7 / (a['Fines_content'] + 0.01))**2)
        return resultado 
df['deltaN'] = df.apply(deltaN,axis=1)
##########################################################
def N160CS(a):
    if a['Flag'] == "Clay":
        return "n.a"
    elif a['Fines_content'] =="n.a":
        return "n.a"
    else:
        return a['N160'] + a['deltaN']
    
df['N160CS'] = df.apply(N160CS,axis=1)
#############################################################################
def rd(a):
    r = np.exp(-1.012 - 1.126 * np.sin(a['Depth'] / 11.73 + 5.133) + M * (0.106 + 0.118 * np.sin(a['Depth'] / 11.28 + 5.142)))
    return r
df['rd'] = df.apply(rd,axis=1)
##############################################################

def CSR(a):
    return 0.65*pga*(a['ESvc']/a['ESvce'])*a['rd']

df['CSR'] = df.apply(CSR,axis=1)
#########################################################

df['MSF']= min(1.8, 6.9 * np.exp(-M / 4) - 0.058)

#######################################################

def Ksigma(a):
    if a['N160CS']=="n.a":
        r=min(1.1, 1 - (1 / (18.9 - 2.55 * np.sqrt(37)) * np.log(a['ESvce'] / 101)))
    else:
        r=min(1.1, 1 - (1 / (18.9 - 2.55 * np.sqrt(min(a['N160CS'], 37))) * np.log(a['ESvce'] / 101)))
    
    return r 

df['Ksigma'] = df.apply(Ksigma,axis=1)
##############################################################

def CRR_75(a):
    if a['Flag'] == "Clay":
        return "n.a."
    elif a['N160CS'] < 37.5:
        resultado = np.exp(a['N160CS'] / 14.1 + (a['N160CS'] / 126) ** 2 - (a['N160CS'] / 23.6) ** 3 + (a['N160CS'] / 25.4) ** 4 - 2.8)
        return resultado
    else:
        return 2.0

df['CRR_75'] = df.apply(CRR_75,axis=1)

###############################################################################################
def CRR(a):
    if a['Flag'] == "Clay" or a['Flag'] == "Unsaturated":
        return "n.a."
    elif a['Flag'] == "Unreliable":
        return "?"
    else:
        resultado = min(2, a['MSF'] * a['Ksigma'] * a['CRR_75'])
        return resultado

df['CRR'] = df.apply(CRR,axis=1)

###########################################################################################

def FoS(a):
    if a['Flag'] == "Clay" or a['Flag'] == "Unsaturated":
        return "n.a."
    elif a['Flag'] == "Unreliable":
        return "?"
    else:
        if a['CRR'] / a['CSR'] > 2:
            resultado = 2
        else:
            resultado = a['CRR'] / a['CSR']
        return resultado
    
df['FoS'] = df.apply(FoS,axis=1)






print(df)
#guardar data frame
df.to_csv('nuevo_archivo.csv', index=False)

