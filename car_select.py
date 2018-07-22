#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 20:27:49 2018

@author: attilakiss
"""


def car_selection():
    """car maker and maker's model selection"""
    complied = ""
    basis = 'https://www.hasznaltauto.hu/szemelyauto/'
    make = input("maker?: ")
    make = make.lower()
    make = make.replace(" ", "")
    model = input("model? (write 'none' if you do not want to specify the model): ")
    if model == "none":
        compiled = basis + make + "/"
    else:
        model = model.lower()
        model = model.replace(" ", "")
        complied = basis + make + "/" + model + "/"
    return complied