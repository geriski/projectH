from lxml import html
import requests
import time
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

link = 'https://www.hasznaltauto.hu/szemelyauto/barkas/'
modelpage = requests.get(link)

tree = html.fromstring(modelpage.content)
maxlist = tree.xpath('//li[@class="last"]/a/@href')
#get the url lists, where the actual url of the cars can be found, if there is 1 page, append just that one
try:
    string = maxlist[0]
except IndexError:
    pagelists = [link]
else:
    string = maxlist[0]
    len = string.find('page')
    maxpage = string[(len)+4:]
    link = string[:len]
    pagelists = []
    for maxpage in range(1,int(maxpage)+1):
        pagelists.append(str(link) + "page" + str(maxpage))
        
#Get the ID-s and URL's of the cars in a dictionary
cars_pages_ids={}
for pagelist in pagelists:
    pagelis = requests.get(pagelist)
    tree = html.fromstring(pagelis.content)
    
    #Get the url's of the cars
    carpages = tree.xpath('//a[@class=""]/@href')
    
    #Remove dupplicates
    hirdetes_kodok = set(carpages)
    
    cars_pages_id={}
    
    #Making the ID-s from the URL links
    for hirdetes_kod in hirdetes_kodok:
        leng = hirdetes_kod.rfind('-')
        kod = hirdetes_kod[(leng)+1:]
        if kod.isdigit():
            cars_pages_id[kod] = hirdetes_kod
        else:
            cars_pages_id[kod] = 'error'

    #Build a dictionary with the webpages and car ID's

    cars_pages_ids.update(cars_pages_id)
    
# search for the new cars

#load the database
filename = 'database.json'
with open(filename) as f_obj:
    cars_existing = json.load(f_obj)

download_cars = {}  
for cars_pages_id_check, cars_urls in cars_pages_ids.items():
    if cars_pages_id_check in cars_existing.keys():
        continue
    else:
        download_cars[cars_pages_id_check] = cars_urls
new_cars=[]
car_ids = []
car_attributions_all = []
car_url_list = download_cars.values()

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
    car_attributions = dict(zip(attributum_names,attributum_values))
    try:
        car_attributions['Leírás'] = description[0]
    except IndexError:
        car_attributions['Leírás'] = "Nincs"
    else:
        car_attributions['Leírás'] = description[0]
    car_attributions['Kategória'] = category[0]
    car_attributions['Márka'] = marka[0]
    car_attributions['Hirdetés feladása'] = (datetime.strftime(datetime.now(), '%Y-%m-%d'))
    car_attributions['Hirdetés leszedése'] = None
    car_attributions['Évjárat év'] = None
    car_attributions['Évjárat hónap'] = None
    
    #Formatting 'Évjárat' to creating year, and months
    if car_attributions['Évjárat:'] != None:
        if car_attributions['Évjárat:'].find('(') != -1:
            ev_honap = car_attributions['Évjárat:'][:(car_attributions['Évjárat:'].find('('))]
            car_attributions['Évjárat év'] = ev_honap[:ev_honap.find('/')]
            car_attributions['Évjárat hónap'] = ev_honap[ev_honap.find('/')+1:]
        elif car_attributions['Évjárat:'].find('/') != -1:
            ev_honap = car_attributions['Évjárat:']
            car_attributions['Évjárat év'] = ev_honap[:ev_honap.find('/')]
            car_attributions['Évjárat hónap'] = ev_honap[ev_honap.find('/')+1:]
        else:
            car_attributions['Évjárat év'] = car_attributions['Évjárat:']    
    #Why Keyerror below??? -- Investigate!
    #if car_attributions['Sebességváltó fajtája:'] != None:
    #    car_attributions['Sebességváltó típus'] = car_attributions['Sebességváltó fajtája:'][:car_attributions['Sebességváltó fajtája:'].find('(')]
    #   car_attributions['Sebességváltó fokozat'] = car_attributions['Sebességváltó fajtája:'][car_attributions['Sebességváltó fajtája:'].find('(')+1:car_attributions['Sebességváltó fajtája:'].find(')')]
    #There are a lot of cars without parameter 'modellcsoport'
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
            else:
                value=value.replace('\xa0','')
                value=value.replace('Ft','')
                value=value.replace('€','')
                value=value.replace('km','')
                value=value.replace(' ','')
                value=value.replace('kg','')
                value=value.replace('cm³','')
            car_attributions.update({k: value})
    
    car_attributions_all.append(car_attributions)
    car_ids.append(car_id[0])

#Build a dictionary with the car ID's and all the infos
new_cars = dict(zip(car_ids, car_attributions_all))

#update the advertisement end date of removed cars 

for cars_existing_key, cars_existing_values in cars_existing.items():
    if cars_existing_key not in cars_pages_ids.keys():
        cars_existing_values['Hirdetés leszedése'] = (datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d'))

#Add the new cars to the original database
cars_existing.update(new_cars)

#import the cars to a Panda DataFramework object
car = pd.DataFrame.from_dict(cars_existing, orient='index')

#import data to json

filename = 'database'
with open(filename, 'w') as f_obj:
    json.dump(cars_existing,f_obj)
