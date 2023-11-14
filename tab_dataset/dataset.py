# -*- coding: utf-8 -*-
"""
The `dataset` module is part of the `tab-dataset` package.

It contains the classes `DatasetAnalysis`, `Cdataset` for Dataset entities.

For more information, see the 
[user guide](https://loco-philippe.github.io/tab-dataset/documentation/user_guide.html) 
or the [github repository](https://github.com/loco-philippe/tab-dataset).

---
"""
from collections import Counter
from copy import copy
from abc import ABC
import math
import json
import csv


from tab_dataset.cfield import Cutil
from tab_dataset.dataset_interface import DatasetInterface
#from tab_dataset.dataset_structure import DatasetStructure
from tab_dataset.field import Nfield, Sfield
from tab_dataset.cdataset import Cdataset, DatasetError

FILTER = '$filter'

#class Sdataset(DatasetStructure, DatasetInterface, ABC, Cdataset):
class Sdataset(DatasetInterface, ABC, Cdataset):
    # %% intro
    '''
    `Sdataset` is a child class of Cdataset where internal value can be different
    from external value (list is converted in tuple and dict in json-object).
    
    One attribute is added: 'field' to define the 'field' class.

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Sdataset.from_csv`
    - `Sdataset.from_file`
    - `Sdataset.merge`
    - `Sdataset.ext`
    - `Cdataset.ntv`
    - `Cdataset.from_ntv`

    *dynamic value - module analysis (getters @property)*

    - `DatasetAnalysis.analysis`
    - `DatasetAnalysis.anafields`
    - `Sdataset.extidx`
    - `Sdataset.extidxext`
    - `DatasetAnalysis.field_partition`
    - `Sdataset.idxname`
    - `Sdataset.idxlen`
    - `Sdataset.iidx`
    - `Sdataset.lenidx`
    - `Sdataset.lidx`
    - `Sdataset.lidxrow`
    - `Sdataset.lisvar`
    - `Sdataset.lvar`
    - `DatasetAnalysis.lvarname`
    - `Sdataset.lvarrow`
    - `Cdataset.lunicname`
    - `Cdataset.lunicrow`
    - `DatasetAnalysis.partitions`
    - `DatasetAnalysis.primaryname`
    - `DatasetAnalysis.relation`
    - `DatasetAnalysis.secondaryname`
    - `Sdataset.setidx`
    - `Sdataset.zip`

    *dynamic value (getters @property)*

    - `Cdataset.keys`
    - `Cdataset.iindex`
    - `Cdataset.indexlen`
    - `Cdataset.lenindex`
    - `Cdataset.lname`
    - `Cdataset.tiindex`

    *global value (getters @property)*

    - `DatasetAnalysis.complete`
    - `Sdataset.consistent`
    - `DatasetAnalysis.dimension`
    - `Sdataset.primary`
    - `Sdataset.secondary`

    *selecting - infos methods*

    - `Sdataset.idxrecord`
    - `DatasetAnalysis.indexinfos`
    - `DatasetAnalysis.indicator`
    - `Sdataset.iscanonorder`
    - `Sdataset.isinrecord`
    - `Sdataset.keytoval`
    - `Sdataset.loc`
    - `Cdataset.nindex`
    - `Sdataset.record`
    - `Sdataset.recidx`
    - `Sdataset.recvar`
    - `Cdataset.to_analysis`
    - `DatasetAnalysis.tree`
    - `Sdataset.valtokey`

    *add - update methods*

    - `Cdataset.add`
    - `Sdataset.addindex`
    - `Sdataset.append`
    - `Cdataset.delindex`
    - `Sdataset.delrecord`
    - `Sdataset.orindex`
    - `Cdataset.renameindex`
    - `Cdataset.setname`
    - `Sdataset.updateindex`

    *structure management - methods*

    - `Sdataset.applyfilter`
    - `Cdataset.check_relation`
    - `Cdataset.check_relationship`
    - `Sdataset.coupling`
    - `Sdataset.full`
    - `Sdataset.getduplicates`
    - `Sdataset.mix`
    - `Sdataset.merging`
    - `Cdataset.reindex`
    - `Cdataset.reorder`
    - `Sdataset.setfilter`
    - `Sdataset.sort`
    - `Cdataset.swapindex`
    - `Sdataset.setcanonorder`
    - `Sdataset.tostdcodec`

    *exports methods (`observation.dataset_interface.DatasetInterface`)*

    - `Dataset.json`
    - `Dataset.plot`
    - `Dataset.to_obj`
    - `Dataset.to_csv`
    - `Dataset.to_dataframe`
    - `Dataset.to_file`
    - `Dataset.to_ntv`
    - `Dataset.to_obj`
    - `Dataset.to_xarray`
    - `Dataset.view`
    - `Dataset.vlist`
    - `Dataset.voxel`
    '''

    field_class = Sfield

    def __init__(self, listidx=None, name=None, reindex=True):
        '''
        Dataset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Field data
        - **name** :  string (default None) - name of the dataset
        - **reindex** : boolean (default True) - if True, default codec for each Field'''

        self.field = self.field_class
        Cdataset.__init__(self, listidx, name, reindex=reindex)

    @classmethod
    def from_csv(cls, filename='dataset.csv', header=True, nrow=None, decode_str=True,
                 decode_json=True, optcsv={'quoting': csv.QUOTE_NONNUMERIC}):
        '''
        Dataset constructor (from a csv file). Each column represents index values.

        *Parameters*

        - **filename** : string (default 'dataset.csv'), name of the file to read
        - **header** : boolean (default True). If True, the first raw is dedicated to names
        - **nrow** : integer (default None). Number of row. If None, all the row else nrow
        - **optcsv** : dict (default : quoting) - see csv.reader options'''
        if not optcsv:
            optcsv = {}
        if not nrow:
            nrow = -1
        with open(filename, newline='', encoding="utf-8") as file:
            reader = csv.reader(file, **optcsv)
            irow = 0
            for row in reader:
                if irow == nrow:
                    break
                if irow == 0:
                    idxval = [[] for i in range(len(row))]
                    idxname = [''] * len(row)
                if irow == 0 and header:
                    idxname = row
                else:
                    for i in range(len(row)):
                        if decode_json:
                            try:
                                idxval[i].append(json.loads(row[i]))
                            except:
                                idxval[i].append(row[i])
                        else:
                            idxval[i].append(row[i])
                irow += 1
        lindex = [cls.field_class.from_ntv(
            {name: idx}, decode_str=decode_str) for idx, name in zip(idxval, idxname)]
        return cls(listidx=lindex, reindex=True)

    @classmethod
    def from_file(cls, filename, forcestring=False, reindex=True, decode_str=False):
        '''
        Generate Object from file storage.

         *Parameters*

        - **filename** : string - file name (with path)
        - **forcestring** : boolean (default False) - if True,
        forces the UTF-8 data format, else the format is calculated
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **decode_str**: boolean (default False) - if True, string are loaded in json data

        *Returns* : new Object'''
        with open(filename, 'rb') as file:
            btype = file.read(1)
        if btype == bytes('[', 'UTF-8') or btype == bytes('{', 'UTF-8') or forcestring:
            with open(filename, 'r', newline='', encoding="utf-8") as file:
                bjson = file.read()
        else:
            with open(filename, 'rb') as file:
                bjson = file.read()
        return cls.from_ntv(bjson, reindex=reindex, decode_str=decode_str)

    def merge(self, fillvalue=math.nan, reindex=False, simplename=False):
        '''
        Merge method replaces Dataset objects included into its constituents.

        *Parameters*

        - **fillvalue** : object (default nan) - value used for the additional data
        - **reindex** : boolean (default False) - if True, set default codec after transformation
        - **simplename** : boolean (default False) - if True, new Field name are
        the same as merged Field name else it is a composed name.

        *Returns*: merged Dataset '''
        ilc = copy(self)
        delname = []
        row = ilc[0]
        if not isinstance(row, list):
            row = [row]
        #merged, oldname, newname = Dataset._mergerecord(self.ext(row, ilc.lname),
        merged, oldname, newname = self.__class__._mergerecord(
            self.ext(row, ilc.lname), simplename=simplename)
        if oldname and not oldname in merged.lname:
            delname.append(oldname)
        for ind in range(1, len(ilc)):
            oldidx = ilc.nindex(oldname)
            for name in newname:
                ilc.addindex(self.field(oldidx.codec, name, oldidx.keys))
            row = ilc[ind]
            if not isinstance(row, list):
                row = [row]
            #rec, oldname, newname = Dataset._mergerecord(self.ext(row, ilc.lname),
            rec, oldname, newname = self.__class__._mergerecord(
                self.ext(row, ilc.lname), simplename=simplename)
            if oldname and newname != [oldname]:
                delname.append(oldname)
            for name in newname:
                oldidx = merged.nindex(oldname)
                fillval = self.field.s_to_i(fillvalue)
                merged.addindex(
                    self.field([fillval] * len(merged), name, oldidx.keys))
            merged += rec
        for name in set(delname):
            if name:
                merged.delindex(name)
        if reindex:
            merged.reindex()
        ilc.lindex = merged.lindex
        return ilc

    @classmethod
    def ext(cls, idxval=None, idxname=None, reindex=True, fast=False):
        '''
        Dataset constructor (external index).

        *Parameters*

        - **idxval** : list of Field or list of values (see data model)
        - **idxname** : list of string (default None) - list of Field name (see data model)'''
        if idxval is None:
            idxval = []
        if not isinstance(idxval, list):
            return None
        val = []
        for idx in idxval:
            if not isinstance(idx, list):
                val.append([idx])
            else:
                val.append(idx)
        lenval = [len(idx) for idx in val]
        if lenval and max(lenval) != min(lenval):
            raise DatasetError('the length of Iindex are different')
        length = lenval[0] if lenval else 0
        idxname = [None] * len(val) if idxname is None else idxname
        for ind, name in enumerate(idxname):
            if name is None or name == '$default':
                idxname[ind] = 'i'+str(ind)
        lindex = [cls.field_class(codec, name, lendefault=length, reindex=reindex,
                                  fast=fast) for codec, name in zip(val, idxname)]
        return cls(lindex, reindex=False)

# %% internal
    @staticmethod
    def _mergerecord(rec, mergeidx=True, updateidx=True, simplename=False):
        row = rec[0]
        if not isinstance(row, list):
            row = [row]
        var = -1
        for ind, val in enumerate(row):
            if val.__class__.__name__ in ['Sdataset', 'Ndataset']:
                var = ind
                break
        if var < 0:
            return (rec, None, [])
        ilis = row[var]
        oldname = rec.lname[var]
        if ilis.lname == ['i0']:
            newname = [oldname]
            ilis.setname(newname)
        elif not simplename:
            newname = [oldname + '_' + name for name in ilis.lname]
            ilis.setname(newname)
        else:
            newname = copy(ilis.lname)
        for name in rec.lname:
            if name in newname:
                newname.remove(name)
            else:
                updidx = name in ilis.lname and not updateidx
                ilis.addindex({name: [rec.nindex(name)[0]] * len(ilis)},
                              merge=mergeidx, update=updidx)
        return (ilis, oldname, newname)

# %% special
    def __str__(self):
        '''return string format for var and lidx'''
        stri = ''
        if self.lvar:
            stri += 'variables :\n'
            for idx in self.lvar:
                stri += '    ' + str(idx) + '\n'
        if self.lidx:
            stri += 'index :\n'
            for idx in self.lidx:
                stri += '    ' + str(idx) + '\n'
        return stri

    def __add__(self, other):
        ''' Add other's values to self's values in a new Dataset'''
        newil = copy(self)
        newil.__iadd__(other)
        return newil

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        return self.add(other, name=True, solve=False)

    def __or__(self, other):
        ''' Add other's index to self's index in a new Dataset'''
        newil = copy(self)
        newil.__ior__(other)
        return newil

    def __ior__(self, other):
        ''' Add other's index to self's index'''
        return self.orindex(other, first=False, merge=True, update=False)

# %% property
    @property
    def consistent(self):
        ''' True if all the record are different'''
        selfiidx = self.iidx
        if not selfiidx:
            return True
        return max(Counter(zip(*selfiidx)).values()) == 1

    @property
    def extidx(self):
        '''idx values (see data model)'''
        return [idx.values for idx in self.lidx]

    @property
    def extidxext(self):
        '''idx val (see data model)'''
        return [idx.val for idx in self.lidx]

    @property
    def idxname(self):
        ''' list of idx name'''
        return [idx.name for idx in self.lidx]

    @property
    def idxlen(self):
        ''' list of idx codec length'''
        return [len(idx.codec) for idx in self.lidx]

    @property
    def iidx(self):
        ''' list of keys for each idx'''
        return [idx.keys for idx in self.lidx]

    @property
    def lenidx(self):
        ''' number of idx'''
        return len(self.lidx)

    @property
    def lidx(self):
        '''list of idx'''
        return [self.lindex[i] for i in self.lidxrow]

    @property
    def lisvar(self):
        '''list of boolean : True if Field is var'''
        return [name in self.lvarname for name in self.lname]

    @property
    def lvar(self):
        '''list of var'''
        return [self.lindex[i] for i in self.lvarrow]

    @property
    def lvarrow(self):
        '''list of var row'''
        return [self.lname.index(name) for name in self.lvarname]

    @property
    def lidxrow(self):
        '''list of idx row'''
        return [i for i in range(self.lenindex) if i not in self.lvarrow]

    @property
    def primary(self):
        ''' list of primary idx'''
        return [self.lidxrow.index(self.lname.index(name)) for name in self.primaryname]

    @property
    def secondary(self):
        ''' list of secondary idx'''
        return [self.lidxrow.index(self.lname.index(name)) for name in self.secondaryname]

    @property
    def setidx(self):
        '''list of codec for each idx'''
        return [idx.codec for idx in self.lidx]

    @property
    def zip(self):
        '''return a zip format for transpose(extidx) : tuple(tuple(rec))'''
        textidx = Cutil.transpose(self.extidx)
        if not textidx:
            return None
        return tuple(tuple(idx) for idx in textidx)

    # %% structure
    def addindex(self, index, first=False, merge=False, update=False):
        '''add a new index.

        *Parameters*

        - **index** : Field - index to add (can be index Ntv representation)
        - **first** : If True insert index at the first row, else at the end
        - **merge** : create a new index if merge is False
        - **update** : if True, update actual values if index name is present (and merge is True)

        *Returns* : none '''
        idx = self.field.ntv(index)
        idxname = self.lname
        if len(idx) != len(self) and len(self) > 0:
            raise DatasetError('sizes are different')
        if not idx.name in idxname:
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
        elif not merge:  # si idx.name in idxname
            while idx.name in idxname:
                idx.name += '(2)'
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
        elif update:  # si merge et si idx.name in idxname
            self.lindex[idxname.index(idx.name)].setlistvalue(idx.values)

    def append(self, record, unique=False):
        '''add a new record.

        *Parameters*

        - **record** :  list of new index values to add to Dataset
        - **unique** :  boolean (default False) - Append isn't done if unique
        is True and record present

        *Returns* : list - key record'''
        if self.lenindex != len(record):
            raise DatasetError('len(record) not consistent')
        record = self.field.l_to_i(record)
        if self.isinrecord(self.idxrecord(record), False) and unique:
            return None
        return [self.lindex[i].append(record[i]) for i in range(self.lenindex)]

    def applyfilter(self, reverse=False, filtname=FILTER, delfilter=True, inplace=True):
        '''delete records with defined filter value.
        Filter is deleted after record filtering.

        *Parameters*

        - **reverse** :  boolean (default False) - delete record with filter's
        value is reverse
        - **filtname** : string (default FILTER) - Name of the filter Field added
        - **delfilter** :  boolean (default True) - If True, delete filter's Field
        - **inplace** : boolean (default True) - if True, filter is apply to self,

        *Returns* : self or new Dataset'''
        if not filtname in self.lname:
            return None
        if inplace:
            ilis = self
        else:
            ilis = copy(self)
        ifilt = ilis.lname.index(filtname)
        ilis.sort([ifilt], reverse=not reverse, func=None)
        lisind = ilis.lindex[ifilt].recordfromvalue(reverse)
        if lisind:
            minind = min(lisind)
            for idx in ilis.lindex:
                del idx.keys[minind:]
        if inplace:
            self.delindex(filtname)
        else:
            ilis.delindex(filtname)
            if delfilter:
                self.delindex(filtname)
        ilis.reindex()
        return ilis

    def coupling(self, derived=True, level=0.1):
        '''Transform idx with low dist in coupled or derived indexes (codec extension).

        *Parameters*

        - **level** : float (default 0.1) - param threshold to apply coupling.
        - **derived** : boolean (default : True). If True, indexes are derived,
        else coupled.

        *Returns* : None'''
        ana = self.analysis
        child = [[]] * len(ana)
        childroot = []
        level = level * len(self)
        for idx in range(self.lenindex):
            if derived:
                iparent = ana.fields[idx].p_distomin.index
            else:
                iparent = ana.fields[idx].p_distance.index
            if iparent == -1:
                childroot.append(idx)
            else:
                child[iparent].append(idx)
        for idx in childroot:
            self._couplingidx(idx, child, derived, level, ana)

    def _couplingidx(self, idx, child, derived, level, ana):
        ''' Field coupling (included childrens of the Field)'''
        fields = ana.fields
        if derived:
            iparent = fields[idx].p_distomin.index
            dparent = ana.get_relation(*sorted([idx, iparent])).distomin
        else:
            iparent = fields[idx].p_distance.index
            dparent = ana.get_relation(*sorted([idx, iparent])).distance
        # if fields[idx].category in ('coupled', 'unique') or iparent == -1\
        if fields[idx].category in ('coupled', 'unique') \
                or dparent >= level or dparent == 0:
            return
        if child[idx]:
            for childidx in child[idx]:
                self._couplingidx(childidx, child, derived, level, ana)
        self.lindex[iparent].coupling(self.lindex[idx], derived=derived,
                                      duplicate=False)
        return

    def delrecord(self, record, extern=True):
        '''remove a record.

        *Parameters*

        - **record** :  list - index values to remove to Dataset
        - **extern** : if True, compare record values to external representation
        of self.value, else, internal

        *Returns* : row deleted'''
        self.reindex()
        reckeys = self.valtokey(record, extern=extern)
        if None in reckeys:
            return None
        row = self.tiindex.index(reckeys)
        for idx in self:
            del idx[row]
        return row

    def _fullindex(self, ind, keysadd, indexname, varname, leng, fillvalue, fillextern):
        if not varname:
            varname = []
        idx = self.lindex[ind]
        lenadd = len(keysadd[0])
        if len(idx) == leng:
            return
        #inf = self.indexinfos()
        ana = self.anafields
        parent = ana[ind].p_derived.view('index')
        # if inf[ind]['cat'] == 'unique':
        if ana[ind].category == 'unique':
            idx.set_keys(idx.keys + [0] * lenadd)
        elif self.lname[ind] in indexname:
            idx.set_keys(idx.keys + keysadd[indexname.index(self.lname[ind])])
        # elif inf[ind]['parent'] == -1 or self.lname[ind] in varname:
        elif parent == -1 or self.lname[ind] in varname:
            fillval = fillvalue
            if fillextern:
                fillval = self.field.s_to_i(fillvalue)
            idx.set_keys(idx.keys + [len(idx.codec)] * len(keysadd[0]))
            idx.set_codec(idx.codec + [fillval])
        else:
            #parent = inf[ind]['parent']
            if len(self.lindex[parent]) != leng:
                self._fullindex(parent, keysadd, indexname, varname, leng,
                                fillvalue, fillextern)
            # if inf[ind]['cat'] == 'coupled':
            if ana[ind].category == 'coupled':
                idx.tocoupled(self.lindex[parent], coupling=True)
            else:
                idx.tocoupled(self.lindex[parent], coupling=False)

    def full(self, reindex=False, idxname=None, varname=None, fillvalue='-',
             fillextern=True, inplace=True, canonical=True):
        '''tranform a list of indexes in crossed indexes (value extension).

        *Parameters*

        - **idxname** : list of string - name of indexes to transform
        - **varname** : string - name of indexes to use
        - **reindex** : boolean (default False) - if True, set default codec
        before transformation
        - **fillvalue** : object value used for var extension
        - **fillextern** : boolean(default True) - if True, fillvalue is converted
        to internal value
        - **inplace** : boolean (default True) - if True, filter is apply to self,
        - **canonical** : boolean (default True) - if True, Field are ordered
        in canonical order

        *Returns* : self or new Dataset'''
        ilis = self if inplace else copy(self)
        if not idxname:
            idxname = ilis.primaryname
        if reindex:
            ilis.reindex()
        keysadd = Cutil.idxfull([ilis.nindex(name) for name in idxname])
        if keysadd and len(keysadd) != 0:
            newlen = len(keysadd[0]) + len(ilis)
            for ind in range(ilis.lenindex):
                ilis._fullindex(ind, keysadd, idxname, varname, newlen,
                                fillvalue, fillextern)
        if canonical:
            ilis.setcanonorder()
        return ilis

    def getduplicates(self, indexname=None, resindex=None, indexview=None):
        '''check duplicate cod in a list of indexes. Result is add in a new
        index or returned.

        *Parameters*

        - **indexname** : list of string (default none) - name of indexes to check
        (if None, all Field)
        - **resindex** : string (default None) - Add a new index named resindex
        with check result (False if duplicate)
        - **indexview** : list of str (default None) - list of fields to return

        *Returns* : list of int - list of rows with duplicate cod '''
        if not indexname:
            indexname = self.lname
        duplicates = []
        for name in indexname:
            duplicates += self.nindex(name).getduplicates()
        if resindex and isinstance(resindex, str):
            newidx = self.field([True] * len(self), name=resindex)
            for item in duplicates:
                newidx[item] = False
            self.addindex(newidx)
        dupl = tuple(set(duplicates))
        if not indexview:
            return dupl
        return [tuple(self.record(ind, indexview)) for ind in dupl]

    def iscanonorder(self):
        '''return True if primary indexes have canonical ordered keys'''
        primary = self.primary
        canonorder = Cutil.canonorder(
            [len(self.lidx[idx].codec) for idx in primary])
        return canonorder == [self.lidx[idx].keys for idx in primary]

    def isinrecord(self, record, extern=True):
        '''Check if record is present in self.

        *Parameters*

        - **record** : list - value for each Field
        - **extern** : if True, compare record values to external representation
        of self.value, else, internal

        *Returns boolean* : True if found'''
        if extern:
            return record in Cutil.transpose(self.extidxext)
        return record in Cutil.transpose(self.extidx)

    def idxrecord(self, record):
        '''return rec array (without variable) from complete record (with variable)'''
        return [record[self.lidxrow[i]] for i in range(len(self.lidxrow))]

    def keytoval(self, listkey, extern=True):
        '''
        convert a keys list (key for each index) to a values list (value for each index).

        *Parameters*

        - **listkey** : key for each index
        - **extern** : boolean (default True) - if True, compare rec to val else to values

        *Returns*

        - **list** : value for each index'''
        return [idx.keytoval(key, extern=extern) for idx, key in zip(self.lindex, listkey)]

    def loc(self, rec, extern=True, row=False):
        '''
        Return record or row corresponding to a list of idx values.

        *Parameters*

        - **rec** : list - value for each idx
        - **extern** : boolean (default True) - if True, compare rec to val,
        else to values
        - **row** : Boolean (default False) - if True, return list of row,
        else list of records

        *Returns*

        - **object** : variable value or None if not found'''
        locrow = None
        try:
            if len(rec) == self.lenindex:
                locrow = list(set.intersection(*[set(self.lindex[i].loc(rec[i], extern))
                                               for i in range(self.lenindex)]))
            elif len(rec) == self.lenidx:
                locrow = list(set.intersection(*[set(self.lidx[i].loc(rec[i], extern))
                                               for i in range(self.lenidx)]))
        except:
            pass
        if locrow is None:
            return None
        if row:
            return locrow
        return [self.record(locr, extern=extern) for locr in locrow]

    def mix(self, other, fillvalue=None):
        '''add other Field not included in self and add other's values'''
        sname = set(self.lname)
        oname = set(other.lname)
        newself = copy(self)
        copother = copy(other)
        for nam in oname - sname:
            newself.addindex({nam: [fillvalue] * len(newself)})
        for nam in sname - oname:
            copother.addindex({nam: [fillvalue] * len(copother)})
        return newself.add(copother, name=True, solve=False)

    def merging(self, listname=None):
        ''' add a new Field build with Field define in listname.
        Values of the new Field are set of values in listname Field'''
        #self.addindex(Field.merging([self.nindex(name) for name in listname]))
        self.addindex(Sfield.merging([self.nindex(name) for name in listname]))

    def orindex(self, other, first=False, merge=False, update=False):
        ''' Add other's index to self's index (with same length)

        *Parameters*

        - **other** : self class - object to add
        - **first** : Boolean (default False) - If True insert indexes
        at the first row, else at the end
        - **merge** : Boolean (default False) - create a new index
        if merge is False
        - **update** : Boolean (default False) - if True, update actual
        values if index name is present (and merge is True)

        *Returns* : none '''
        if len(self) != 0 and len(self) != len(other) and len(other) != 0:
            raise DatasetError("the sizes are not equal")
        otherc = copy(other)
        for idx in otherc.lindex:
            self.addindex(idx, first=first, merge=merge, update=update)
        return self

    def record(self, row, indexname=None, extern=True):
        '''return the record at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val record else
        value record
        - **indexname** : list of str (default None) - list of fields to return
        *Returns*

        - **list** : val record or value record'''
        if indexname is None:
            indexname = self.lname
        if extern:
            record = [idx.val[row] for idx in self.lindex]
            #record = [idx.values[row].to_obj() for idx in self.lindex]
            #record = [idx.valrow(row) for idx in self.lindex]
        else:
            record = [idx.values[row] for idx in self.lindex]
        return [record[self.lname.index(name)] for name in indexname]

    def recidx(self, row, extern=True):
        '''return the list of idx val or values at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for idx'''
        if extern:
            return [idx.values[row].to_obj() for idx in self.lidx]
            # return [idx.valrow(row) for idx in self.lidx]
        return [idx.values[row] for idx in self.lidx]

    def recvar(self, row, extern=True):
        '''return the list of var val or values at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for var'''
        if extern:
            return [idx.values[row].to_obj() for idx in self.lvar]
            # return [idx.valrow(row) for idx in self.lvar]
        return [idx.values[row] for idx in self.lvar]

    def setcanonorder(self, reindex=False):
        '''Set the canonical index order : primary - secondary/unique - variable.
        Set the canonical keys order : ordered keys in the first columns.

        *Parameters*
        - **reindex** : boolean (default False) - if True, set default codec after
        transformation

        *Return* : self'''
        order = self.primaryname
        order += self.secondaryname
        order += self.lvarname
        order += self.lunicname
        self.swapindex(order)
        self.sort(reindex=reindex)
        # self.analysis.actualize()
        return self

    def setfilter(self, filt=None, first=False, filtname=FILTER, unique=False):
        '''Add a filter index with boolean values

        - **filt** : list of boolean - values of the filter idx to add
        - **first** : boolean (default False) - If True insert index at the first row,
        else at the end
        - **filtname** : string (default FILTER) - Name of the filter Field added

        *Returns* : self'''
        if not filt:
            filt = [True] * len(self)
        idx = self.field(filt, name=filtname)
        idx.reindex()
        if not idx.cod in ([True, False], [False, True], [True], [False]):
            raise DatasetError('filt is not consistent')
        if unique:
            for name in self.lname:
                if name[:len(FILTER)] == FILTER:
                    self.delindex(FILTER)
        self.addindex(idx, first=first)
        return self

    def sort(self, order=None, reverse=False, func=str, reindex=True):
        '''Sort data following the index order and apply the ascending or descending
        sort function to values.

        *Parameters*

        - **order** : list (default None)- new order of index to apply. If None or [],
        the sort function is applied to the existing order of indexes.
        - **reverse** : boolean (default False)- ascending if True, descending if False
        - **func**    : function (default str) - parameter key used in the sorted function
        - **reindex** : boolean (default True) - if True, apply a new codec order (key = func)

        *Returns* : self'''
        if not order:
            order = list(range(self.lenindex))
        orderfull = order + list(set(range(self.lenindex)) - set(order))
        if reindex:
            for i in order:
                self.lindex[i].reindex(codec=sorted(
                    self.lindex[i].codec, key=func))
        newidx = Cutil.transpose(sorted(Cutil.transpose(
            [self.lindex[orderfull[i]].keys for i in range(self.lenindex)]),
            reverse=reverse))
        for i in range(self.lenindex):
            self.lindex[orderfull[i]].set_keys(newidx[i])
        return self

    """
    def swapindex(self, order):
        '''
        Change the order of the index .

        *Parameters*

        - **order** : list of int or list of name - new order of index to apply.

        *Returns* : self '''
        if self.lenindex != len(order):
            raise DatasetError('length of order and Dataset different')
        if not order or isinstance(order[0], int):
            self.lindex = [self.lindex[ind] for ind in order]
        elif isinstance(order[0], str):
            self.lindex = [self.nindex(name) for name in order]
        return self
    """

    def tostdcodec(self, inplace=False, full=True):
        '''Transform all codec in full or default codec.

        *Parameters*

        - **inplace** : boolean  (default False) - if True apply transformation
        to self, else to a new Dataset
        - **full** : boolean (default True)- full codec if True, default if False


        *Return Dataset* : self or new Dataset'''
        lindex = [idx.tostdcodec(inplace=False, full=full)
                  for idx in self.lindex]
        if inplace:
            self.lindex = lindex
            return self
        return self.__class__(lindex, self.lvarname)

    def updateindex(self, listvalue, index, extern=True):
        '''update values of an index.

        *Parameters*

        - **listvalue** : list - index values to replace
        - **index** : integer - index row to update
        - **extern** : if True, the listvalue has external representation, else internal

        *Returns* : none '''
        self.lindex[index].setlistvalue(listvalue, extern=extern)

    def valtokey(self, rec, extern=True):
        '''convert a record list (value or val for each idx) to a key list
        (key for each index).

        *Parameters*

        - **rec** : list of value or val for each index
        - **extern** : if True, the rec value has external representation, else internal

        *Returns*

        - **list of int** : record key for each index'''
        return [idx.valtokey(val, extern=extern) for idx, val in zip(self.lindex, rec)]

class Ndataset(Sdataset):
    # %% Ndataset
    '''    
    `Ndataset` is a child class of Cdataset where internal value are NTV entities.
    
    All the methods are the same as `Sdataset`.
    '''
    field_class = Nfield
