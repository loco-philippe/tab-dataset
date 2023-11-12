# -*- coding: utf-8 -*-
"""
***TAB-Dataset Package***

Created on Fri Dec 24 15:21:14 2021

@author: philippe@loco-labs.io

This package contains the following classes and functions:

- `tab-dataset.cfield` :
    - `tab-dataset.cfield.Cfield`
    - `tab-dataset.cfield.Cutil`
    - `tab-dataset.cfield.root` (function)
    - `tab-dataset.cfield.identity` (function)

- `tab-dataset.cdataset` :
    - `tab-dataset.cdataset.Cdataset`
        
- `tab-dataset.field` :
    - `tab-dataset.field.Field`
    - `tab-dataset.field.Nfield`
    - `tab-dataset.field.Sfield`

- `tab-dataset.field_interface` :
    - `tab-dataset.field_interface.FieldInterface`
    - `tab-dataset.field_interface.FieldEncoder`
    - `tab-dataset.field_interface.CborDecoder`

- `tab-dataset.dataset` :
    - `tab-dataset.dataset.Dataset    

- `tab-dataset.dataset_structure` :
    - `tab-dataset.dataset_structure.DatasetStructure
    
- `tab-dataset.dataset_interface` :
    - `tab-dataset.dataset_interface.DatasetInterface
    
- `tab-dataset.dataset_analysis` :
    - `tab-dataset.dataset_analysis.DatasetAnalysis

Note: Analysis functions are in another package `tab-analysis` 

For more information, see the 
[user guide](https://loco-philippe.github.io/tab-dataset/documentation/user_guide.html) 
or the [github repository](https://github.com/loco-philippe/tab-dataset).
"""
from tab_dataset.dataset import Ndataset, Sdataset
from tab_dataset.cdataset import Cdataset
from tab_dataset.field import Nfield, Sfield
from tab_dataset.cfield import Cfield

#print('package :', __package__)
