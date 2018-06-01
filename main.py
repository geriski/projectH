from lxml import html
import requests

modelpage = requests.get(
    'https://www.hasznaltauto.hu/szemelyauto/abarth/')
tree = html.fromstring(modelpage.content)
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
cars=[]
car_ids = []
car_attributions_all = []

#Get all the information for a car as it can
for page in carpages:
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

# Print the cars and infos
for cars_id, cars_attrb in cars.items():
    print("Car ID: " + cars_id + "\nDescriptions:")
    for cars_attrb_name, cars_attrb_value in cars_attrb.items():
        print("\t-" + str(cars_attrb_name) + " : " + str(cars_attrb_value))


