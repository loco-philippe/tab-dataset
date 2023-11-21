# -*- coding: utf-8 -*-
"""
The `field_interface` module is part of the `tab-dataset` package.

It contains the classes `FieldInterface` for Field entities.

For more information, see the 
[user guide](https://loco-philippe.github.io/tab-dataset/docs/user_guide.html) 
or the [github repository](https://github.com/loco-philippe/tab-dataset).
"""
# %% declarations
import json
import datetime
import numpy as np
import pandas as pd

from json_ntv.ntv import NtvSingle, NtvList
from json_ntv.ntv_util import NtvUtil
from tab_dataset.cfield import FieldError, Cutil, identity


class CborDecoder(json.JSONDecoder):
    ''' Cbor extension for integer keys (codification keys)'''

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.codecbor)

    def codecbor(self, dic):
        ''' convert dict keys into integer and return new dict'''
        dic2 = {}
        for key, val in dic.items():
            try:
                key2 = int(key)
            except:
                key2 = key
            dic2[key2] = val
        return dic2


class FieldEncoder(json.JSONEncoder):
    """new json encoder for Field and Dataset"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        option = {'encoded': False, 'format': 'json'}
        if o.__class__.__name__ in ('Dataset', 'TimeSlot', 'Ndataset', 'Sdataset'):
            return o.json(**option)
        # if issubclass(o.__class__, ESValue):
        #    return o.json(**option)
        try:
            return o.to_json(**option)
        except:
            try:
                return o.__to_json__()
            except:
                return json.JSONEncoder.default(self, o)


class FieldInterface:
    '''this class includes Field methods :

    - `FieldInterface.json`
    - `FieldInterface.to_obj`
    - `FieldInterface.to_dict_obj`
    - `FieldInterface.to_numpy`
    - `FieldInterface.to_pandas`
    - `FieldInterface.vlist`
    - `FieldInterface.v_name`
    - `FieldInterface.vSimple`
    '''

    def to_numpy(self, func=None, codec=False, npdtype=None, **kwargs):
        '''
        Transform Field in a Numpy array.

        *Parameters*

        - **func** : function (default None) - function to apply for each value of the Field.
        If func is the 'index' string, values are replaced by raw values.
        - **npdtype** : string (default None) - numpy dtype for the Array ('object' if None)
        - **kwargs** : parameters to apply to the func function

        *Returns* : Numpy Array'''
        return self.to_pandas(func=func, codec=codec, npdtype=npdtype, numpy=True, **kwargs)

    def to_ntv(self, modecodec='optimize', codecval=False, def_type=None,
               keys=None, parent=None, name=True, coef=None):
        '''Return a Ntv field value

        *Parameters (kwargs)*

        - **modecodec** : string (default 'optimize') - if 'full', index is with a full codec
        if 'default' index has keys, if 'optimize' keys are optimized,
        - **codecval** : boolean (default False) - if True, only list of codec values is included
        - **def_type** : string (default 'json') - default ntv_type for NtvList or NtvSet
        - **name** : boolean (default True) - if False, index name are not included
        - **keys** : list (default None) - used only with 'optimize' mode
        - **parent** : int or str (default None) - used only with 'optimize' mode

        *Returns* : Ntv object'''
        leng = len(self)
        codec = self.i_to_n(self.codec)
        decode_name, decode_type, sep = NtvUtil.from_obj_name(self.name)
        decode_name = decode_name if sep == '::' else self.name
        def_type = decode_type if sep == '::' and decode_type else def_type
        def_type = codec[0].ntv_type if not def_type and codec else def_type
        idxname = None if decode_name == '$default' or not name else decode_name
        if leng == 1 or len(codec) == 1 and modecodec != 'full':
            return NtvSingle(codec[0].ntv_value, idxname, codec[0].ntv_type)
        if codecval or modecodec == 'nokeys':
            return NtvList(codec, idxname, ntv_type=def_type)
        if len(codec) == leng or modecodec == 'full':
            return NtvList(self.values, idxname, ntv_type=def_type)
        if modecodec == 'default':
            return NtvList([NtvList(codec, ntv_type=def_type),
                            NtvList(self.keys, ntv_type='json')], idxname, ntv_type='json')
        if coef:
            return NtvList([NtvList(codec, ntv_type=def_type),
                            NtvList([coef], ntv_type='json')], idxname, ntv_type='json')
        if modecodec == 'optimize':
            ntv_value = [NtvList(codec, ntv_type=def_type)]
            if not parent is None:
                ntv_value.append(NtvSingle(parent, ntv_type='json'))
            if keys:
                ntv_value.append(NtvList(keys, ntv_type='json'))
            elif parent is None:
                ntv_value.append(NtvList(self.keys, ntv_type='json'))
            return NtvList(ntv_value, idxname, ntv_type='json')
        return None

    def to_pandas(self, func=None, codec=False, npdtype=None,
                  series=True, index=True, numpy=False, **kwargs):
        '''
        Transform Field in a Pandas Series, Pandas DataFrame or Numpy array.

        *Parameters*

        - **func** : function (default None) - function to apply for each value of the Field.
        If func is the 'index' string, values are replaced by raw values.
        - **npdtype** : string (default None) - numpy dtype for the Array ('object' if None)
        - **series** : boolean (default True) - if True, return a Series.
        If False return a DataFrame
        - **index** : boolean (default True) - if True, index is keys.
        - **numpy** : boolean (default False) - if True, return a Numpy array.
        - **kwargs** : parameters to apply to the func function

        *Returns* : Pandas Series, Pandas DataFrame, Numpy Array'''
        if len(self) == 0:
            raise FieldError("Dataset is empty")
        if npdtype:
            npdtype = np.dtype(npdtype)
        else:
            npdtype = 'object'
        if func is None:
            func = identity
        if func == 'index':
            return np.array(list(range(len(self))))
        if not codec:
            values = Cutil.funclist(self.values, func, **kwargs)
        else:
            values = Cutil.funclist(self._codec, func, **kwargs)
        npdtype1 = npdtype
        if isinstance(values[0], (datetime.datetime)):
            npdtype1 = np.datetime64
        pdindex = None
        if index:
            pdindex = self._keys
        try:
            if numpy:
                return np.array(values, dtype=npdtype1)
            if series:
                return pd.Series(values, dtype=npdtype1,
                                 index=pdindex, name=self.name)
            return pd.DataFrame(pd.Series(values, dtype=npdtype1,
                                          index=pdindex, name=self.name))
        except:
            if numpy:
                return np.array(values, dtype=npdtype)
            if series:
                return pd.Series(values, dtype=npdtype,
                                 index=pdindex, name=self.name)
            return pd.DataFrame(pd.Series(values, dtype=npdtype,
                                          index=pdindex, name=self.name))

    def vlist(self, func, *args, extern=True, **kwargs):
        '''
        Apply a function to values and return the result.

        *Parameters*

        - **func** : function - function to apply to values
        - **args, kwargs** : parameters for the function
        - **extern** : if True, the function is apply to external values, else internal

        *Returns* : list of func result'''
        if extern:
            return Cutil.funclist(self.val, func, *args, **kwargs)
        return Cutil.funclist(self.values, func, *args, **kwargs)

    def v_name(self):
        '''Return the list of name of values'''
        return [self.i_to_name(val) for val in self.values]

    """def vSimple(self, string=False):
        '''
        Apply a vSimple function to values and return the result.

        *Parameters*

        - **string** : boolean(default False) - if True the values returned are string

        *Returns* : list of vSimple values (string or not)'''
        if string:
            return json.dumps([util.cast(val, 'simple', string=string) for val in self.values],
                              cls=ESValueEncoder)
        return [util.cast(val, 'simple', string=string) for val in self.values]"""
