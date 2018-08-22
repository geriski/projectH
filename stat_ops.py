"""
Contains the function for statistic operations to projectH
@author: geriski
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import time
from datetime import datetime, timedelta

def make_categoricals(cardata):
    """
    Creating special categories. Template:
    {Column_name1:
      {Replace_to1:[Replace_from1,Replace_from2],
    Column_name2:
      {Replace_to2:[Replace_from1,Replace_from2]}}
    """
    categories = {'Állapot':
                {'Normál':['Sérülésmentes','Megkímélt','Kitűnő','Újszerű'],
                 'Sérült': ['Enyhénsérült','Motorhibás']}, 
              'Üzemanyag':
                {'Alternatív':['Benzin/Gáz','Etanol', 'LPG']}}
    for cat, cat_attr in categories.items():
        for cat_tos, cat_froms in cat_attr.items():
            for cat_from in cat_froms:
                cardata[cat] = cardata[cat].str.replace(cat_from, cat_tos)
    return cardata
