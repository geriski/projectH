from lxml import html
import requests
import time
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import functions as f

link = 'https://www.hasznaltauto.hu/szemelyauto/dacia/logan'

cars_pages_ids = f.get_url_list(link)

#load the existing database
filename = 'database2.json'
with open(filename) as f_obj:
    cars_existing = json.load(f_obj)

car_url_list = f.searching_new_cars(cars_pages_ids,cars_existing)

new_cars=[]
car_ids = []
car_attributions_all = []


#Get all the information for a car as it can
for page in car_url_list:
    car_id =[]
    car_attributions = []
    carpage = requests.get(page)
    tree = html.fromstring(carpage.content)
    table_header = tree.xpath('//table[@class="hirdetesadatok"]/tr/th/text()')
    car_id = tree.xpath('//div[@class="hagomb-belso"]/strong/text()')
    attributum_names = tree.xpath('//table[@class="hirdetesadatok"]/tr/td/text()')
    attributum_values = tree.xpath(
        '//table[@class="hirdetesadatok"]/tr/td/strong/text()')
    items_categories = tree.xpath('//div[@class="col-xs-28 col-sm-14"]/h4/text()')
    items = tree.xpath('//div[@class="col-xs-28 col-sm-14"]/ul/li/text()')
    description = tree.xpath('//div[@class="leiras"]/div/text()')
    category = tree.xpath('//a[@type="kategoria"]/text()')
    marka = tree.xpath('//a[@type="marka"]/text()')
    modellcsoport = tree.xpath('//a[@type="modellcsoport"]/text()')
    modell = tree.xpath('//a[@type="modell"]/text()')
    try: 
        attributum_names.remove('Extrákkal növelt ár:')
        
    except ValueError:
        sale_price = 0
    else:
        sale_price = 1
        try:
            attributum_names.remove('Akció feltételei:')
            attributum_values.insert(0,min(tree.xpath('//span[@class="arsorpiros"]/text()')))
        except ValueError:
            sale_price = 1
                
    if sale_price ==1:
        try:
            attributum_names.remove('Akciós ár:')
        except ValueError:
            blabla=1
            
    try: 
        attributum_names.remove('Alaptípus ára:')
    except ValueError:
        sale_price = 0
    if sale_price == 1:    
        attributum_names.insert(0,'Vételár:')
    
    car_attributions = dict(zip(attributum_names,attributum_values))
    try:
        car_attributions['Leírás'] = description[0]
    except IndexError:
        car_attributions['Leírás'] = "Nincs"
    else:
        car_attributions['Leírás'] = description[0]
    car_attributions['Felszereltség'] = tree.xpath('//ul[@class="pontos"]/li/text()')
    car_attributions['Cím'] = tree.xpath('//div[@class="hagomb-belso"]/text()')[0]
    helyiseg = tree.xpath('//meta[@name="description"]/@content')[0]
    car_attributions['Helyiség'] = helyiseg[helyiseg.rfind(':')+2:helyiseg.find(')')]
    car_attributions['Kategória'] = category[0]
    car_attributions['Márka'] = marka[0]
    car_attributions['Hirdetés feladása'] = (datetime.strftime(datetime.now(), '%Y-%m-%d'))
    car_attributions['Hirdetés leszedése'] = None
    car_attributions['Évjárat év'] = None
    car_attributions['Évjárat hónap'] = None
    try:
        car_attributions['Teljesítmény(LE)'] = car_attributions['Teljesítmény:'][car_attributions['Teljesítmény:'].find(',')+2:car_attributions['Teljesítmény:'].find('LE')-1]
    except KeyError:
        c=0
  #no need  
    #Formatting 'Évjárat' to creating year, and months
  #  if car_attributions['Évjárat:'] != None:
  #      if car_attributions['Évjárat:'].find('(') != -1:
  #          ev_honap = car_attributions['Évjárat:'][:(car_attributions['Évjárat:'].find('('))]
  #          car_attributions['Évjárat év'] = ev_honap[:ev_honap.find('/')]
  #          car_attributions['Évjárat hónap'] = ev_honap[ev_honap.find('/')+1:]
  #      elif car_attributions['Évjárat:'].find('/') != -1:
  #          ev_honap = car_attributions['Évjárat:']
  #          car_attributions['Évjárat év'] = ev_honap[:ev_honap.find('/')]
  #         car_attributions['Évjárat hónap'] = ev_honap[ev_honap.find('/')+1:]
  #      else:
  #          car_attributions['Évjárat év'] = car_attributions['Évjárat:']    
    
    try:
        car_attributions['Sebességváltó fajtája:'] != None
    except KeyError:
        c=0
    else:
        if car_attributions['Sebességváltó fajtája:'] != None:
            car_attributions['Sebességváltó típus'] = car_attributions['Sebességváltó fajtája:'][:car_attributions['Sebességváltó fajtája:'].find('(')]
            car_attributions['Sebességváltó fokozat'] = car_attributions['Sebességváltó fajtája:'][car_attributions['Sebességváltó fajtája:'].find('(')+1:car_attributions['Sebességváltó fajtája:'].find('(')+2]    
    try:
        car_attributions['Modellcsoport'] = modellcsoport[0]
    except IndexError:
        car_attributions['Modellcsoport'] = "Nincs"
    else:
        car_attributions['Modellcsoport'] = modellcsoport[0]
    car_attributions['Modell'] = modell[0]
    
#formatting the attributions of the car, eg. cut the spaces and metrics
    #Get rid of ':' in keys
    car_attributions = { k.replace(':', ''): v for k, v in car_attributions.items() }
    
    #Format values
    for k, value in car_attributions.items():
        #In case of the replace function doesn't work, don't do anything
        try:
            value=value.replace('\xa0','')
        except AttributeError:
            continue
        else:
            if k == ('Leírás'):
                continue
            elif k == ('Okmányok jellege'):
                continue
            elif k == ('Felszereltség'):
                continue
            elif k ==('Cím'):
                continue
            elif k ==('Tető'):
                continue
            else:
                value=value.replace('\xa0','')
                value=value.replace('Ft','')
                value=value.replace('€','')
                value=value.replace('km','')
                value=value.replace(' ','')
                value=value.replace('kg','')
                value=value.replace('cm³','')
                value=value.replace('f\u0151','')
                value=value.replace('liter','')
                
            car_attributions.update({k: value})
    
    car_attributions_all.append(car_attributions)
    car_ids.append(car_id[0])

#Build a dictionary with the car ID's and all the infos
new_cars = dict(zip(car_ids, car_attributions_all))

#update the advertisement end date of removed cars TEMP.DISABLED

#for cars_existing_key, cars_existing_values in cars_existing.items():
#    if cars_existing_key not in cars_pages_ids.keys():
#        cars_existing_values['Hirdetés leszedése'] = (datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d'))

#Add the new cars to the original database
cars_existing.update(new_cars)

#import the cars to a Panda DataFramework object
cardata = pd.DataFrame.from_dict(cars_existing, orient='index')

#Formatting Állapot and Üzemenyag categories to 2 categories each / Állapot: Normal or Sérült, Üzemanyag: Benzin or Diesel or Alt.
cardata['Állapot'] = cardata['Állapot'].str.replace('Sérülésmentes', 'Normál')
cardata['Állapot'] = cardata['Állapot'].str.replace('Megkímélt', 'Normál')
cardata['Állapot'] = cardata['Állapot'].str.replace('Kitűnő', 'Normál')
cardata['Állapot'] = cardata['Állapot'].str.replace('Újszerű', 'Normál')
cardata['Állapot'] = cardata['Állapot'].str.replace('Enyhénsérült', 'Sérült')
cardata['Állapot'] = cardata['Állapot'].str.replace('Motorhibás', 'Sérült')
cardata['Üzemanyag'] = cardata['Üzemanyag'].str.replace('Benzin/Gáz', 'Alternatív')
cardata['Üzemanyag'] = cardata['Üzemanyag'].str.replace('Etanol', 'Alternatív')
cardata['Üzemanyag'] = cardata['Üzemanyag'].str.replace('LPG', 'Alternatív')

#setting the proper type of dtypes

datetimes = ['Hirdetés feladása', 'Hirdetés leszedése']
categories = ['Hajtás','Kivitel', 'Henger-elrendezés', 'Kategória', 'Klíma fajtája', 'Kárpit színe (1)', 'Kárpit színe (2)', 'Modell', 'Modellcsoport', 'Márka', 'Okmányok jellege', 'Sebességváltó típus', 'Szín', 'Tető', 'Állapot', 'Üzemanyag']

for datetime1 in datetimes:
  cardata[datetime1] = cardata[datetime1].astype('datetime64')
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
#remove the rows, where in a spec columns has NaN
#cardata = cardata.dropna(subset=['Kilométeróra állása'])

#import database to Pandas
#cardata = pd.read_json(path_or_buf= 'database2.json', orient='index')

#export data to json
filename = 'database2.json'
with open(filename, 'w') as f_obj:
    json.dump(cars_existing,f_obj)

#running OLS multilinear regression analysis
#clear the datas

cardata = cardata.dropna(subset=['Évjárat'])
cardata = cardata.dropna(subset=['Vételár'])
cardata = cardata.dropna(subset=['Autó kora(nap)'])
#cardata = cardata.drop(cardata[cardata['Kilométeróra állása'] < 1100].index)
#cardata = cardata.drop(cardata[cardata['Vételár'] > 4099000].index)
cardata = cardata.drop(cardata[cardata['Üzemanyag'] == 'Alternatív'].index)

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
print(model.summary())
fig = plt.figure(figsize=(15,8))
fig = sm.graphics.plot_regress_exog(model, "ido", fig=fig)
plt.show()

#values must have add to the predition
print(X.columns)
#Predict new value
Xnew = np.asarray((1,0,0,1,0,104500,2600))
ynewpred= model.predict(Xnew)
#predected value
print(ynewpred)
