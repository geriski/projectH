from lxml import html
import requests
import time
from datetime import datetime, timedelta
import json

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from patsy import dmatrices

import build as b
import stat_ops as s


#Add the URL link, needs to be parsed and the database file name.
link = 'https://www.hasznaltauto.hu/szemelyauto/dacia/logan'
filename = 'database2.json'

#load the existing database
with open(filename) as f_obj:
    cars_existing = json.load(f_obj)

cars_pages_ids = b.get_url_list(link)
car_url_list = b.searching_new_cars(cars_pages_ids,cars_existing)
new_cars = b.download_new_cars(car_url_list)

#TEMPORARLY DISABLED
#b.removed_cars_date(cars_pages_ids,cars_existing)

#Add the new cars to the original database
cars_existing.update(new_cars)

#export data to json
with open(filename, 'w') as f_obj:
    json.dump(cars_existing,f_obj)

#Import the data of the cars to a Panda DataFramework object from the existing dictionary
cardata = pd.DataFrame.from_dict(cars_existing, orient='index')

#import json database to Pandas DataFramework
#cardata = pd.read_json(path_or_buf= filename, orient='index')

#Prepare the data to analysis
#Add the variables and special category naming scheme.
spec_categories = {'Állapot':
                        {'Normál':['Sérülésmentes','Megkímélt','Kitűnő','Újszerű'],
                        'Sérült': ['Enyhénsérült','Motorhibás']}, 
                    'Üzemanyag':
                        {'Alternatív':['Benzin/Gáz','Etanol', 'LPG']}}

cardata = s.make_spec_categoricals(spec_categories, cardata)

#Add the variables which dtype has to be set
datetimes = ['Évjárat','Műszaki vizsga érvényes']   
categories = ['Hajtás','Kivitel', 'Henger-elrendezés', 'Kategória', 'Klíma fajtája',
              'Kárpit színe (1)', 'Kárpit színe (2)', 'Modell', 'Modellcsoport', 'Márka', 
              'Okmányok jellege', 'Sebességváltó típus', 'Szín', 'Tető', 'Állapot', 
              'Üzemanyag']
numdata = ['Ajtók száma', 'Hengerűrtartalom', 'Kilométeróra állása','Saját tömeg',
            'Sebességváltó fokozat','Szállítható szem. száma', 'Teljes tömeg', 
            'Teljesítmény(LE)', 'Vételár', 'Vételár EUR']

cardata = s.set_dtypes(datetimes, categories, numdata, cardata)
cardata = s.additional_variables(cardata)

#running OLS multilinear regression analysis

#clear the data
#remove the rows, where in a spec columns has NaN
drop_nans = ['Évjárat', 'Vételár', 'Autó kora(nap)']
cardata = s.drop_nan(drop_nans, cardata)

#cardata = cardata.drop(cardata[cardata['Kilométeróra állása'] < 1100].index)
#cardata = cardata.drop(cardata[cardata['Vételár'] > 4099000].index)
cardata = cardata.drop(cardata[cardata['Üzemanyag'] == 'Alternatív'].index)

#Renaming columns
cardata['Telj'] = cardata['Teljesítmény(LE)']
cardata['km'] = cardata['Kilométeróra állása']
cardata['ido'] = ((cardata['Autó kora(nap)'] / np.timedelta64(1, 'D')).astype(int))*-1

#Design matrices
#Notice that dmatrices has split: 1.the categorical variable into a set of indicator variables.
#2.added a constant to the exogenous regressors matrix. 3.returned pandas DataFrames instead of simple numpy arrays. 
#This is useful because DataFrames allow statsmodels to carry-over meta-data (e.g. variable names) when reporting results.

y, X = dmatrices('Vételár ~  km + Modell + Állapot + ido + Üzemanyag', data=cardata, return_type='dataframe')

#Model fit and summary
model = sm.OLS(y,X).fit()
print(model.summary())

s.print_figure(model, 'ido')

#Printing required values for predition
print('\nRequired values for prediction: ', X.columns)

#Predict new value
Xnew = np.asarray((1,0,0,1,0,104500,2600))
ynewpred= model.predict(Xnew)

#Printing predected value
print('Estimated value: ', ynewpred, ' HUF')
