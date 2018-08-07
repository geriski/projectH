from lxml import html
import requests
from lxml import etree
from io import StringIO, BytesIO
import json
link1= 'http://www.kozbeszerzes.hu/adatbazis/megtekint/hirdetmeny/portal_'
pagelists=[]
for num in range(1,20):
    pagelists.append(str(link1) + str(num+5950) + '_2018/')
print(pagelists)
notice = {}
for link in pagelists:
    notice_page = requests.get(link)
    tree = html.fromstring(notice_page.content)
    notice_attributes = {}
    notice_attributes_all = {}

    notice_page = (notice_page.content).decode('utf-8')
    
    if notice_page.find('A keresett oldal nem található') == -1:
    
        notice_table_names = tree.xpath('//table[@class="notice__heading"]/tr/th/text()')
        
        for notice_table_name in notice_table_names:
            
            length_name_find = notice_page.find(notice_table_name)
            length_name_start= notice_page[length_name_find:].find('<td>')
            length_name_end = notice_page[length_name_find:].find('</td></tr>')
            tree_name_string = notice_page[length_name_find+length_name_start+4:length_name_find+length_name_end]
            notice_attributes[notice_table_name] =  tree_name_string
            
            #HREF correction
            
            if notice_table_name == 'Letöltés:':
                 
                length_name_find = notice_page.find(notice_table_name)
                length_name_start= notice_page[length_name_find:].find('href="')
                length_name_end = notice_page[length_name_find+7:].find('target="')
                tree_name_string = notice_page[length_name_find+length_name_start+7:length_name_find+length_name_end+5]
                tree_name_string = 'http://www.kozbeszerzes.hu/' + tree_name_string
                notice_attributes[notice_table_name] =  tree_name_string
            
            if notice_table_name == 'Közbeszerzési eljárás:':
                length_name_find = notice_page.find(notice_table_name)
                length_name_start= notice_page[length_name_find:].find('href="')
                length_name_end = notice_page[length_name_find+7:].find('target="')
                tree_name_string = notice_page[length_name_find+length_name_start+6:length_name_find+length_name_end+5]
                notice_attributes[notice_table_name] =  tree_name_string
        if notice_attributes['Beszerzés tárgya:'] == 'Szolgáltatásmegrendelés' :
            continue
        #Ajánlatkérő
        notice_attributes['Ajánlakérő:'] ={}
        contracting_authority={}
        length_name_start= notice_page.find('I.1) Név és címek')
        length_name_end = notice_page.find('I.2) Közös közbeszerzés')
        if length_name_end ==-1 :
            length_name_end = notice_page.find('II. szakasz')
        sub_tree_string = notice_page[length_name_start:length_name_end]
        
        print('Ajánlatkérő,60:', length_name_start, length_name_end)
        
        parser = etree.HTMLParser()
        sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
        contracting_authority_names = sub_tree.xpath('//div[@style="padding-left:2em;"]/text()')
        for contracting_authority_name in contracting_authority_names:
            length_name_find = sub_tree_string.find(contracting_authority_name)
            length_name_start= sub_tree_string[length_name_find:].find('<span')
            length_name_end = sub_tree_string[length_name_find:].find('</span>')
            tree_name_string = sub_tree_string[length_name_find+length_name_start+47:length_name_find+length_name_end]
            contracting_authority[contracting_authority_name] =  tree_name_string
        notice_attributes['Ajánlakérő:'] = contracting_authority
        notice_attributes['Ajánlakérő:']['Ajánlatkérő típusa:'] = notice_attributes['Ajánlatkérő típusa:']
        notice_attributes['Ajánlakérő:']['Ajánlatkérő fő tevényeségi köre:'] = notice_attributes['Ajánlatkérő fő tevényeségi köre:']
        notice_attributes_all['Alap adatok'] = notice_attributes
        
        
        #Tárgy
        
        subject={}
        length_name_start= notice_page.find('II. szakasz:')
        length_name_end = notice_page.find('III. szakasz:')
        if length_name_end ==-1 :
            length_name_end = notice_page.find('IV. szakasz')
        
        sub_tree_string = notice_page[length_name_start:length_name_end]
        
        parser = etree.HTMLParser()
        sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
        subject_categories = sub_tree.xpath('//div[@style="padding-left:0px;"]/text()')
        deleting = ['II.1)','II.2)']
        for dele in deleting:
            for sc in subject_categories:
                if dele in sc:
                    subject_categories.remove(sc)
        #print(subject_categories)        
        for subject_category in subject_categories:
            length_name_start= notice_page.find(subject_category)
            try:
                length_name_end = notice_page[length_name_start:].find(subject_categories[subject_categories.index(subject_category)+1])
            except IndexError:
                length_name_end = notice_page.find('III. szakasz:')
                if length_name_end ==-1 :
                    length_name_end = notice_page.find('IV. szakasz')
                if length_name_end ==-1 :
                    length_name_end = notice_page.find('VI. szakasz') 
    
            sub_tree_string = notice_page[length_name_start:length_name_start+length_name_end]
            parser = etree.HTMLParser()
            sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
            subject_items = sub_tree.xpath('//span[@style="font-weight:200;color: #336699;"]/text()')
            subject[subject_category]=subject_items
            #print(subject_category)
        
        notice_attributes_all['Tárgy']= subject
        #eredmény
        notice_attributes_all['Eredmény'] ={}
        
        #megkötés dátuma
        if notice_page.find('V.2.1) A szerződés megkötésének dátuma') != -1:
          length_name_start= notice_page.find('V.2.1) A szerződés megkötésének dátuma')
          length_name_end = notice_page.find('V.2.2) Ajánlatokra vonatkozó információk')
          sub_tree_string = notice_page[length_name_start:length_name_end]
          parser = etree.HTMLParser()
          sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
          result_items = sub_tree.xpath('//span[@style="font-weight:200;color: #336699;"]/text()')
          try:
            result_date = result_items[0]
          except IndexError:
            notice_attributes_all['Eredmény']['Szerződés megkötés dátuma'] = None
          else:
            notice_attributes_all['Eredmény']['Szerződés megkötés dátuma']= result_date
        
          #nyertes
          result_contractor_attrib = {}
          length_name_start= notice_page.find('V.2.3) A nyertes ajánlattevő neve és címe')
          length_name_end = notice_page.find('V.2.4) A szerződés/rész')
          sub_tree_string = notice_page[length_name_start:length_name_end]
          parser = etree.HTMLParser()
          sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
          result_categories = sub_tree.xpath('//div[@style="padding-left:2em;"]/text()')
        
          for result_category in result_categories:
              length_name_start= sub_tree_string.find(result_category)
              try:
                length_name_end = sub_tree_string[length_name_start:].find(result_categories[result_categories.index(result_category)+1])
              except IndexError:
                length_name_end = 10
          
              subsub_tree_string = sub_tree_string[length_name_start:length_name_start+length_name_end]
              print('nyertes,150:', length_name_start, length_name_end)
              parser = etree.HTMLParser()
              subsub_tree   = etree.parse(StringIO(subsub_tree_string), parser)
              result_items = subsub_tree.xpath('//span[@style="font-weight:200;color: #336699;"]/text()')
              try:
                result_contractor_attrib[result_category]=result_items[0]
              except IndexError:
                result_contractor_attrib[result_category] = None
                
          notice_attributes_all['Nyertes'] = result_contractor_attrib
        else:
          notice_attributes_all['Eredmény']['Szerződés megkötés dátuma'] = None
          notice_attributes_all['Nyertes'] = None
        notice[notice_attributes['Iktatószám:']] = notice_attributes_all
        print(notice_attributes['Iktatószám:'])
    else:
      continue
print(notice.keys())
#print(notice_attributes_all)
#export

json = json.dumps(notice,  indent=4, ensure_ascii=False)
f = open("dict.json","w")
f.write(json)
f.close()
