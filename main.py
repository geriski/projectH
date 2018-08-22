from lxml import html
import requests
import time
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import build as b

#Please add the URL link, needs to be parsed and the database file name.
link = 'https://www.hasznaltauto.hu/szemelyauto/dacia/logan'
filename = 'database2.json'

cars_pages_ids = b.get_url_list(link)

#load the existing database
with open(filename) as f_obj:
    cars_existing = json.load(f_obj)

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

#Creating special categories {Column_name1:{Replace_to1:[Replace_from1,Replace_from2], Column_name2:{Replace_to2:[Replace_from1,Replace_from2]}}
categories = {'Állapot':{'Normál':['Sérülésmentes','Megkímélt','Kitűnő','Újszerű'],'Sérült': ['Enyhénsérült','Motorhibás']}, 'Üzemanyag':{'Alternatív':['Benzin/Gáz','Etanol', 'LPG']}}
for cat, cat_attr in categories.items():
    for cat_tos, cat_froms in cat_attr.items():
        for cat_from in cat_froms:
            cardata[cat] = cardata[cat].str.replace(cat_from, cat_tos)

#setting the proper type of dtypes

datetimes = ['Hirdetés feladása', 'Hirdetés leszedése']
categories = ['Hajtás','Kivitel', 'Henger-elrendezés', 'Kategória', 'Klíma fajtája', 'Kárpit színe (1)', 'Kárpit színe (2)', 'Modell', 'Modellcsoport', 'Márka', 'Okmányok jellege', 'Sebességváltó típus', 'Szín', 'Tető', 'Állapot', 'Üzemanyag']

#for datetime1 in datetimes:
#  cardata[datetime1] = cardata[datetime1].astype('datetime64')
for category1 in categories:
  cardata[category1] = cardata[category1].astype('category')

#convert dates to date types
dates1 = ['Évjárat','Műszaki vizsga érvényes']
for date1 in dates1:
    cardata[date1]= pd.to_datetime(cardata[date1], errors='coerce')

#ensure that were numerical data is a must, there would be only num data

numdatas = ['Ajtók száma', 'Hengerűrtartalom', 'Kilométeróra állása','Saját tömeg','Sebességváltó fokozat','Szállítható szem. száma', 'Teljes tömeg', 'Teljesítmény(LE)', 'Vételár', 'Vételár EUR']
for numdata in numdatas:
    cardata[numdata] =pd.to_numeric(cardata[numdata], errors='coerce')

#additional variables in Pandas
cardata['Hirdetési idő(nap)'] = cardata['Hirdetés feladása'] - cardata['Hirdetés leszedése']
cardata['Autó kora(nap)']=cardata['Évjárat'] - pd.to_datetime('today')
cardata['Műszaki még érvenyes(nap)']=cardata['Műszaki vizsga érvényes'] - pd.to_datetime('today')
cardata['Évjárat'] =pd.to_numeric(cardata['Évjárat'], errors='coerce')

#showing a spec row
#print(cardata.ix[12963080])

#running OLS multilinear regression analysis
#clear the datas

#remove the rows, where in a spec columns has NaN
drop_nans = ['Évjárat', 'Vételár', 'Autó kora(nap)']
for drop_nan in drop_nans:
    cardata = cardata.dropna(subset=[drop_nan])

#cardata = cardata.drop(cardata[cardata['Kilométeróra állása'] < 1100].index)
#cardata = cardata.drop(cardata[cardata['Vételár'] > 4099000].index)
cardata = cardata.drop(cardata[cardata['Üzemanyag'] == 'Alternatív'].index)

#Renaming columns
cardata['Telj'] = cardata['Teljesítmény(LE)']
cardata['km'] = cardata['Kilométeróra állása']
cardata['ido'] = ((cardata['Autó kora(nap)'] / np.timedelta64(1, 'D')).astype(int))*-1

#Design matrices
#Notice that dmatrices has split: the categorical variable into a set of indicator variables.
#added a constant to the exogenous regressors matrix.
#returned pandas DataFrames instead of simple numpy arrays. This is useful because DataFrames allow statsmodels to carry-over meta-data (e.g. variable names) when reporting results.
from patsy import dmatrices
y, X = dmatrices('Vételár ~  km + Modell + Állapot + ido + Üzemanyag', data=cardata, return_type='dataframe')

#Model fit and summary
model = sm.OLS(y,X).fit()
print(model.summary())

#print figures
fig = plt.figure(figsize=(15,8))
fig = sm.graphics.plot_regress_exog(model, "ido", fig=fig)
plt.show()

#Printing required values for predition
print('\nRequired values for prediction: ', X.columns)

#Predict new value
Xnew = np.asarray((1,0,0,1,0,104500,2600))
ynewpred= model.predict(Xnew)

#Printing predected value
print('Estimated value: ', ynewpred, ' HUF')
