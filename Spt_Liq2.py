import pandas as pd
import numpy as np
class SPT():
    pga=0.28 #Peack ground accesk (g)
    M= 6.9 #Earthquacke magnitude
    d=1.8 #Water table depth (m)
    PEdry= 19 #Average gamma above water table (kN/m3) 
    PEsat=20 #Average gamma below water table (kN/m3) 
    diam=100 #Borehole diammeter (mm)
    Correction="NO" #Requires correction for sampler lineres (YES/NO)

    def __init__(self,ruta):
        self.ruta=ruta
        self.df = pd.read_csv(self.ruta)

    def CR0(self,valor):
        self.valor=valor
        if (self.valor["Depth"] + 1.5) < 3:
            return 0.75
        elif (self.valor["Depth"] + 1.5) < 4:
            return 0.8
        elif (self.valor["Depth"] + 1.5) < 6:
            return 0.85
        elif (self.valor["Depth"] + 1.5) < 10:
            return 0.95
        else:
            return 1.0
    def iniciar(self):
        self.df["CE"]=self.df["Energy_ratio"]/60
#Definimos CB
        if self.diam<115.1:
         self.df["CB"]=1
        elif self.diam < 150.1:
         self.df["CB"]=1
        else:
         self.df["CB"]=1.15
    
        self.df['CR'] = self.df.apply(self.CR0,axis=1)
        return self.df
#Definimos CR
# Definir una función que aplique la fórmula a un valor de CR


        
# Aplicar la función a la columna y crear una nueva columna 'Resultado'
    #df["CR"] = df['Depth'].apply(CR)


Luis = SPT("SPT_DATA.csv")
Luis.iniciar()
print(Luis.iniciar())

#guardar data frame
