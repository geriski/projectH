from lxml import html
import requests
import time
import json

modelpage = requests.get(
    'https://www.hasznaltauto.hu/szemelyauto/daihatsu/')
tree = html.fromstring(modelpage.content)

#get the next url list, where the url of the cars can be found
maxlist = tree.xpath('//li[@class="last"]/a/@href')
string = maxlist[0]
len = string.find('page')
maxpage = string[(len)+4:]
link = string[:len]
pagelists = []
for maxpage in range(1,int(maxpage)+1):
    pagelists.append(str(link) + "page" + str(maxpage))

carpages_all =[]
for pagelist in pagelists:
    pagelis = requests.get(pagelist)
    tree = html.fromstring(pagelis.content)
    #Get the url's of the cars
    carpages = tree.xpath('//a[@class=""]/@href')

    hirdetes_kodok = tree.xpath('//div[@class="talalatisor-info '
                               'talalatisor-hirkod"]//text()')
    carnames = tree.xpath('//div[@class="col-xs-28 col-sm-19 '
                          'cim-kontener"]/h3/a/text()')
    hirdetes_kodok =[w.replace('Hirdetéskód: ', '')for w in hirdetes_kodok]
    hirdetes_kodok =[w.replace('(', '')for w in hirdetes_kodok]
    hirdetes_kodok =[w.replace(')', '')for w in hirdetes_kodok]
    hirdetes_kodok =[w.replace('', '')for w in hirdetes_kodok]

    #Build a dictionary with the webpages and car ID's
    cars_pages = dict(zip(hirdetes_kodok, carpages))
    carpages_all.append(carpages)

cars=[]
car_ids = []
car_attributions_all = []
flat_list = [item for sublist in carpages_all for item in sublist]

#Get all the information for a car as it can
for page in flat_list:
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
    #There are a lot of cars without parameter 'modellcsoport'
    try:
        car_attributions['Modellcsoport'] = modellcsoport[0]
    except IndexError:
        car_attributions['Modellcsoport'] = "Nincs"
    else:
        car_attributions['Modellcsoport'] = modellcsoport[0]
    car_attributions['Modell'] = modell[0]
    car_attributions_all.append(car_attributions)
    car_ids.append(car_id[0])

#Build a dictionary with the car ID's and all the infos
cars = dict(zip(car_ids, car_attributions_all))

#import data to json

filename = 'daihatsu_20180602.json'
with open(filename, 'w') as f_obj:
    json.dump(cars,f_obj)
