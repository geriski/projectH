"""
Contains the related modules to projectH
@author: geriski
"""
import requests
from lxml import html

def get_url_list(link):
    """
    Get the url lists, where the actual url of the cars can be found. If there is 1 page, append just that one.
    """
    modelpage = requests.get(link)
    tree = html.fromstring(modelpage.content)
    maxlist = tree.xpath('//li[@class="last"]/a/@href')
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
    return pagelists
