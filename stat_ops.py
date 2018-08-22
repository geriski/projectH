"""
Contains the function for statistic operations to projectH
@author: geriski
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import time
from datetime import datetime, timedelta

def make_categoricals(cardata):
    """
    Creating special categories. Template:
    {Column_name1:
      {Replace_to1:[Replace_from1,Replace_from2],
    Column_name2:
      {Replace_to2:[Replace_from1,Replace_from2]}}
    """
    categories = {'Állapot':
                {'Normál':['Sérülésmentes','Megkímélt','Kitűnő','Újszerű'],
                 'Sérült': ['Enyhénsérült','Motorhibás']}, 
              'Üzemanyag':
                {'Alternatív':['Benzin/Gáz','Etanol', 'LPG']}}
    for cat, cat_attr in categories.items():
        for cat_tos, cat_froms in cat_attr.items():
            for cat_from in cat_froms:
                cardata[cat] = cardata[cat].str.replace(cat_from, cat_tos)
    return cardata

def set_dtypes(cardata):
    """
    Setting the proper type of dtypes
    """

    datetimes = ['Hirdetés feladása', 'Hirdetés leszedése']
    categories = ['Hajtás','Kivitel', 'Henger-elrendezés', 'Kategória', 'Klíma fajtája',
                  'Kárpit színe (1)', 'Kárpit színe (2)', 'Modell', 'Modellcsoport', 'Márka', 
                  'Okmányok jellege', 'Sebességváltó típus', 'Szín', 'Tető', 'Állapot', 
                  'Üzemanyag']
    
    #TEMPORARLY DISABLED
    #for datetime1 in datetimes:
    #  cardata[datetime1] = cardata[datetime1].astype('datetime64')
    for category1 in categories:
      cardata[category1] = cardata[category1].astype('category')
    
    #Convert dates to date types
    dates1 = ['Évjárat','Műszaki vizsga érvényes']
    for date1 in dates1:
        cardata[date1]= pd.to_datetime(cardata[date1], errors='coerce')
    
    #Ensure that were numerical data is a must, there would be only num data
    
    numdatas = ['Ajtók száma', 'Hengerűrtartalom', 'Kilométeróra állása','Saját tömeg',
                'Sebességváltó fokozat','Szállítható szem. száma', 'Teljes tömeg', 
                'Teljesítmény(LE)', 'Vételár', 'Vételár EUR']
    for numdata in numdatas:
        cardata[numdata] =pd.to_numeric(cardata[numdata], errors='coerce')
    return cardata
