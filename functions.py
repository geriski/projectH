"""
Contains the related modules to projectH
@author: geriski
"""
import requests
from lxml import html
import json

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
