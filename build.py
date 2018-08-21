"""
Contains the related modules to projectH
@author: geriski
"""
import requests
from lxml import html
import json
import time
from datetime import datetime, timedelta

def get_url_list(link):
    """
    Bulid a dictionary with the car ID's and the webpages URL addresses.
    """
    modelpage = requests.get(link)
    tree = html.fromstring(modelpage.content)
    
    # Get the url lists, where the actual url of the cars can be found.
    maxlist = tree.xpath('//li[@class="last"]/a/@href')
    try:
        string = maxlist[0]
        
    #If there is 1 page, append just that one.
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
    return cars_pages_ids
    
def searching_new_cars(cars_pages_ids, cars_existing):
    """
    Searching for the new cars.
    """
    

    #compare the new id's to the old ones
    download_cars = {}  
    for cars_pages_id_check, cars_urls in cars_pages_ids.items():
        if cars_pages_id_check in cars_existing.keys():
            continue
        else:
            download_cars[cars_pages_id_check] = cars_urls
    car_url_list = download_cars.values()
    return car_url_list
def download_new_cars(car_url_list):
    """
    Download all information available for the cars and format it.
    """
    
    new_cars = {}
    for page in car_url_list:
        new_car = {}
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
        
        #Formatting the attributions of the car, eg. cut the spaces and metrics
        
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
    
        new_car[car_id[0]] = car_attributions
        new_cars.update(new_car)
    return new_cars
