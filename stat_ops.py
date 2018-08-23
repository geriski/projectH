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

def make_spec_categoricals(spec_categories, cardata):
    """
    Creating special categories. Template:
    {Column_name1:
      {Replace_to1:[Replace_from1,Replace_from2],
    Column_name2:
      {Replace_to2:[Replace_from1,Replace_from2]}}
    """

    for cat, cat_attr in spec_categories.items():
        for cat_tos, cat_froms in cat_attr.items():
            for cat_from in cat_froms:
                cardata[cat] = cardata[cat].str.replace(cat_from, cat_tos)
    return cardata

def set_dtypes(datetimes, categories, numdatas, cardata):
    """
    Setting the proper type of dtypes
    """

    for category1 in categories:
      cardata[category1] = cardata[category1].astype('category')
    
    #Convert dates to date types
    
    for date1 in datetimes:
        cardata[date1]= pd.to_datetime(cardata[date1], errors='coerce')
    
    #Ensure that were numerical data is a must, there would be only num data
    
    for numdata in numdatas:
        cardata[numdata] =pd.to_numeric(cardata[numdata], errors='coerce')
    return cardata
    
def additional_variables(cardata):
    """
    Adding additional variables to the DataFramework
    """
    cardata['Hirdetési idő(nap)'] = cardata['Hirdetés feladása'] - cardata['Hirdetés leszedése']
    cardata['Autó kora(nap)']=cardata['Évjárat'] - pd.to_datetime('today')
    cardata['Műszaki még érvenyes(nap)']=cardata['Műszaki vizsga érvényes'] - pd.to_datetime('today')
    cardata['Évjárat'] =pd.to_numeric(cardata['Évjárat'], errors='coerce')
    return cardata
    
def drop_nan(drop_nans, cardata):
    """
    Remove the rows, where in a spec columns has NaN.
    """
    for drop_nan in drop_nans:
        cardata = cardata.dropna(subset=[drop_nan])
    return cardata
    
def print_figure(model, variable_to_show):
    """
    Printing 4 kind of plot figure.
    """
    fig = plt.figure(figsize=(15,8))
    fig = sm.graphics.plot_regress_exog(model, variable_to_show, fig=fig)
    plt.show()
