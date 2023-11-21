# -*- coding: utf-8 -*-
"""
The `cdataset` module is part of the `tab-dataset` package.

It contains the classes `DatasetAnalysis`, `Cdataset` for Dataset entities.

For more information, see the 
[user guide](https://loco-philippe.github.io/tab-dataset/docs/user_guide.html) 
or the [github repository](https://github.com/loco-philippe/tab-dataset).
"""
from copy import copy

from tab_dataset.cfield import Cfield, Cutil

from json_ntv import Ntv
from json_ntv.ntv_util import NtvUtil, NtvConnector

from tab_analysis import AnaDataset, Util


class DatasetAnalysis:
    '''This class is the Cdataset interface class with the tab_analysis module.'''

# %% property
    @property
    def analysis(self):
        '''The analysis attribute is associated to the AnaDataset object'''
        if self._analysis is None or self._analysis.hashd != self._hashd:
            self._analysis = AnaDataset(self.to_analysis(True))
        return self._analysis

    @property
    def anafields(self):
        ''' list of AnaField'''
        return self.analysis.fields

    @property
    def partitions(self):
        ''' list of partitions defined with index representation (AnaDataset method)'''
        return self.analysis.partitions('index')

    @property
    def complete(self):
        ''' complete property of the dataset (AnaDataset method)'''
        return self.analysis.complete

    @property
    def dimension(self):
        ''' dimension of the dataset (AnaDataset method)'''
        return self.analysis.dimension

    @property
    def lvarname(self):
        ''' list of variable Field name (AnaDataset method)'''
        return Util.view(self.analysis.variable, mode='id')

    @property
    def primaryname(self):
        ''' list of primary name (AnaDataset method)'''
        return Util.view(self.analysis.primary, mode='id')

    @property
    def secondaryname(self):
        ''' list of secondary name (AnaDataset method)'''
        return Util.view(self.analysis.secondary, mode='id')


# %% methods

    def indexinfos(self, keys=None):
        '''return a dict with infos of each index (AnaDataset method) :
            
        - num, name, cat, diffdistparent, child, parent, distparent,
        crossed, pparent, rateder (struct info)
        - lencodec, mincodec, maxcodec, typecodec, ratecodec (base info)

        *Parameters*

        - **keys** : string, list or tuple (default None) - list of attributes
        to returned.
        if 'all' or None, all attributes are returned.
        if 'struct', only structural attributes are returned.

        *Returns* : dict'''
        return self.analysis.to_dict(mode='index', keys=keys)

    def field_partition(self, partition=None, mode='index'):
        '''return a partition dict with the list of primary, secondary, unique
        and variable fields (index).

         *Parameters*

        - **partition** : list (default None) - if None, partition is the first
        - **mode** : str (default 'index') - Field representation ('id', 'index')
        '''
        if not partition and len(self.partitions) > 0:
            partition = self.partitions[0]
        part = [self.analysis.dfield(fld)
                for fld in partition] if partition else None
        return self.analysis.field_partition(mode=mode, partition=part,
                                             distributed=True)

    def relation(self, fld1, fld2):
        '''relationship between two fields (AnaDataset method)'''
        return self.analysis.get_relation(fld1, fld2)

    def tree(self, mode='derived', width=5, lname=20, string=True):
        '''return a string with a tree of derived Field (AnaDataset method).

         *Parameters*

        - **lname** : integer (default 20) - length of the names
        - **width** : integer (default 5) - length of the lines
        - **string** : boolean (default True) - if True return str else return dict
        - **mode** : string (default 'derived') - kind of tree :
            'derived' : derived tree
            'distance': min distance tree
            'distomin': min distomin tree
        '''
        return self.analysis.tree(mode=mode, width=width, lname=lname, string=string)

    def indicator(self, fullsize=None, size=None):
        '''generate size indicators: ol (object lightness), ul (unicity level),
        gain (sizegain)

        *Parameters*

        - **fullsize** : int (default none) - size with full codec
        - **size** : int (default none) - size with existing codec

        *Returns* : dict'''
        if not fullsize:
            fullsize = len(self.to_obj(encoded=True, modecodec='full'))
        if not size:
            size = len(self.to_obj(encoded=True))
        return self.analysis.indicator(fullsize, size)


class Cdataset(DatasetAnalysis):
    # %% magic
    '''
    A `Cdataset` is a representation of a tabular data.

    *Attributes (for @property see methods)* :

    - **lindex** : list of Field
    - **name** : name of the Cdataset
    - **_analysis** : AnaDataset object

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Cdataset.ntv`
    - `Cdataset.from_ntv`

    *dynamic value - module analysis (getters @property)*

    - `DatasetAnalysis.analysis`
    - `DatasetAnalysis.anafields`
    - `DatasetAnalysis.lvarname`
    - `DatasetAnalysis.partitions`
    - `DatasetAnalysis.primaryname`
    - `DatasetAnalysis.secondaryname`
    - `DatasetAnalysis.complete`
    - `DatasetAnalysis.dimension`

    *selecting - infos methods (module analysis)*

    - `DatasetAnalysis.field_partition`
    - `DatasetAnalysis.indexinfos`
    - `DatasetAnalysis.indicator`
    - `DatasetAnalysis.relation`
    - `DatasetAnalysis.tree`

    *dynamic value (getters @property)*

    - `Cdataset.keys`
    - `Cdataset.iindex`
    - `Cdataset.indexlen`
    - `Cdataset.lenindex`
    - `Cdataset.lname`
    - `Cdataset.lunicname`
    - `Cdataset.lunicrow`
    - `Cdataset.tiindex`

    *add - update methods (`observation.dataset_structure.DatasetStructure`)*

    - `Cdataset.add`
    - `Cdataset.delindex`
    - `Cdataset.renameindex`
    - `Cdataset.setname`

    *structure management - methods (`observation.dataset_structure.DatasetStructure`)*

    - `Cdataset.check_relation`
    - `Cdataset.check_relationship`
    - `Cdataset.nindex`
    - `Cdataset.reindex`
    - `Cdataset.reorder`
    - `Cdataset.swapindex`
    - `Cdataset.to_analysis`
    '''
    field_class = Cfield

    def __init__(self, listidx=None, name=None, reindex=True):
        '''
        Dataset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Field data
        - **name** :  string (default None) - name of the dataset
        - **reindex** : boolean (default True) - if True, default codec for each Field'''

        if isinstance(listidx, Cdataset):
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.name = name if name else listidx.name
            self._analysis = listidx._analysis
            return
        if listidx.__class__.__name__ == 'DataFrame':
            lindex = NtvConnector.connector(
            )['DataFrameConnec'].to_listidx(listidx)[0]
            listidx = [Cfield(field['codec'], field['name'], field['keys'])
                       for field in lindex]
        self.name = name
        self.lindex = [] if listidx is None else listidx
        if reindex:
            self.reindex()
        self._analysis = None
        return

    def __repr__(self):
        '''return classname, number of value and number of indexes'''
        return self.__class__.__name__ + '[' + str(len(self)) + ', ' + str(self.lenindex) + ']'

    def __str__(self):
        '''return string format for var and lidx'''
        stri = ''
        stri += 'fields :\n'
        for idx in self.lindex:
            stri += '    ' + str(idx) + '\n'
        return stri

    def __len__(self):
        ''' len of values'''
        if not self.lindex:
            return 0
        return len(self.lindex[0])

    def __contains__(self, item):
        ''' list of lindex values'''
        return item in self.lindex

    def __getitem__(self, ind):
        ''' return value record (value conversion)'''
        res = [idx[ind] for idx in self.lindex]
        if len(res) == 1:
            return res[0]
        return res

    def __setitem__(self, ind, item):
        ''' modify the Field values for each Field at the row ind'''
        if not isinstance(item, list):
            item = [item]
        for val, idx in zip(item, self.lindex):
            idx[ind] = val

    def __delitem__(self, ind):
        ''' remove all Field item at the row ind'''
        for idx in self.lindex:
            del idx[ind]

    def __hash__(self):
        '''return hash of all hash(Field)'''
        #return hash(tuple(hash(idx) for idx in self.lindex))
        return sum(hash(idx) for idx in self.lindex)

    def __eq__(self, other):
        ''' equal if hash values are equal'''
        return hash(self) == hash(other)

    def __copy__(self):
        ''' Copy all the data '''
        return self.__class__(self)

# %% property
    @property
    def _hashd(self):
        '''return hash of all hashf(Field)'''
        # return sum([idx._hashi() for idx in self.lindex])
        return hash(tuple(fld.hashf for fld in self.lindex))

    @property
    def indexlen(self):
        ''' list of index codec length'''
        return [len(idx.codec) for idx in self.lindex]

    @property
    def iindex(self):
        ''' list of keys for each index'''
        return [idx.keys for idx in self.lindex]

    @property
    def keys(self):
        ''' list of keys for each index'''
        return [idx.keys for idx in self.lindex]

    @property
    def lenindex(self):
        ''' number of indexes'''
        return len(self.lindex)

    @property
    def lunicname(self):
        ''' list of unique index name'''
        return [idx.name for idx in self.lindex if len(idx.codec) == 1]

    @property
    def lunicrow(self):
        '''list of unic idx row'''
        return [self.lname.index(name) for name in self.lunicname]

    @property
    def lname(self):
        ''' list of index name'''
        return [idx.name for idx in self.lindex]

    @property
    def tiindex(self):
        ''' list of keys for each record'''
        return Cutil.list(list(zip(*self.iindex)))

# %%methods

    @classmethod
    def ntv(cls, ntv_value, reindex=True, fast=False):
        '''Generate an Dataset Object from a ntv_value

        *Parameters*

        - **ntv_value** : bytes, string, Ntv object to convert
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **fast** : boolean (default False) - if True, ntv_value are not converted in json-value'''
        return cls.from_ntv(ntv_value, reindex=reindex, fast=fast)

    @classmethod
    def from_ntv(cls, ntv_value, reindex=True, decode_str=False, fast=False):
        '''Generate a Dataset Object from a ntv_value

        *Parameters*

        - **ntv_value** : bytes, string, Ntv object to convert
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **decode_str**: boolean (default False) - if True, string are loaded in json data
        - **fast** : boolean (default False) - if True, ntv_value are not converted in json-value'''
        ntv = Ntv.obj(ntv_value, decode_str=decode_str, fast=fast)
        if len(ntv) == 0:
            return cls()
        lidx = [list(NtvUtil.decode_ntv_tab(
            ntvf, cls.field_class.ntv_to_val)) for ntvf in ntv]
        leng = max(idx[6] for idx in lidx)
        for ind in range(len(lidx)):
            if lidx[ind][0] == '':
                lidx[ind][0] = 'i'+str(ind)
            NtvConnector.init_ntv_keys(ind, lidx, leng)
        lindex = [cls.field_class(idx[2], idx[0], idx[4], None,  # idx[1] pour le type,
                                  reindex=reindex) for idx in lidx]
        return cls(lindex, reindex=reindex, name=ntv.name)

    def add(self, other, name=False, solve=True):
        ''' Add other's values to self's values for each index

        *Parameters*

        - **other** : Dataset object to add to self object
        - **name** : Boolean (default False) - Add values with same index name (True) or
        same index row (False)
        - **solve** : Boolean (default True) - If True, replace None other's codec value
        with self codec value.

        *Returns* : self '''
        if self.lenindex != other.lenindex:
            raise DatasetError('length are not identical')
        if name and sorted(self.lname) != sorted(other.lname):
            raise DatasetError('name are not identical')
        for i in range(self.lenindex):
            if name:
                self.lindex[i].add(other.lindex[other.lname.index(self.lname[i])],
                                   solve=solve)
            else:
                self.lindex[i].add(other.lindex[i], solve=solve)
        return self

    def to_analysis(self, distr=False):
        '''return a dict with data used in AnaDataset module

        *Parameters*

        - **distr** : Boolean (default False) - If True, add distr information'''
        return {'name': self.name, 'fields': [fld.to_analysis for fld in self.lindex],
                'length': len(self), 'hashd': self._hashd,
                'relations': {self.lindex[i].name:
                              {self.lindex[j].name: Cutil.dist(
                                  self.lindex[i].keys, self.lindex[j].keys, distr)
                               for j in range(i+1, len(self.lindex))}
                              for i in range(len(self.lindex)-1)}
                }

    def reindex(self):
        '''Calculate a new default codec for each index (Return self)'''
        for idx in self.lindex:
            idx.reindex()
        return self

    def delindex(self, delname=None, savename=None):
        '''remove an Field or a list of Field.

        *Parameters*

        - **delname** : string or list of string - name of index to remove
        - **savename** : string or list of string - name of index to keep

        *Returns* : none '''
        if not delname and not savename:
            return
        if isinstance(delname, str):
            delname = [delname]
        if isinstance(savename, str):
            savename = [savename]
        if delname and savename:
            delname = [name for name in delname if not name in savename]
        if not delname:
            delname = [name for name in self.lname if not name in savename]
        for idxname in delname:
            if idxname in self.lname:
                self.lindex.pop(self.lname.index(idxname))

    def nindex(self, name):
        ''' index with name equal to attribute name'''
        if name in self.lname:
            return self.lindex[self.lname.index(name)]
        return None

    def renameindex(self, oldname, newname):
        '''replace an index name 'oldname' by a new one 'newname'. '''
        for i in range(self.lenindex):
            if self.lname[i] == oldname:
                self.lindex[i].setname(newname)
        for i in range(len(self.lvarname)):
            if self.lvarname[i] == oldname:
                self.lvarname[i] = newname

    def reorder(self, recorder=None):
        '''Reorder records in the order define by 'recorder' '''
        if recorder is None or set(recorder) != set(range(len(self))):
            return None
        for idx in self.lindex:
            idx.set_keys([idx.keys[i] for i in recorder])
        return None

    def setname(self, listname=None):
        '''Update Field name by the name in listname'''
        for i in range(min(self.lenindex, len(listname))):
            self.lindex[i].name = listname[i]

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

    def check_relation(self, field, parent, typecoupl, value=True):
        '''get the inconsistent records for a relationship

         *Parameters*

        - **field** : int or str - index or name of the field involved in the relation
        - **parent**: int or str - index or name of the second field involved in the relation
        - **typecoupl**: str - relationship to check ('derived' or 'coupled')
        - **value**: boolean (default True) - if True return a dict with inconsistent
        values of the fields, else a tuple with index of records)

        *Returns* :

        - dict with inconsistent values of the fields
        - or a tuple with index of records'''
        f_parent = self.nindex(parent) if isinstance(
            parent, str) else self.lindex[parent]
        f_field = self.nindex(field) if isinstance(
            field, str) else self.lindex[field]
        match typecoupl:
            case 'derived':
                errors = f_parent.coupling(f_field, reindex=True)
            case 'coupled':
                errors = f_parent.coupling(
                    f_field, derived=False, reindex=True)
            case _:
                raise DatasetError(typecoupl + "is not a valid relationship")
        if not value:
            return errors
        return {'row': list(errors), f_field.name: f_field[errors], f_parent.name: f_parent[errors]}

    def check_relationship(self, relations):
        '''get the inconsistent records for each relationship defined in relations

         *Parameters*

        - **relations** : list of dict or single dict - list of fields with relationship property

        *Returns* :

        - dict with for each relationship: key = string with the two fields name,
        and value = list of inconsistent records
        - or if single relationship : value'''
        if not isinstance(relations, (list, dict)):
            raise DatasetError("relations is not correct")
        if isinstance(relations, dict):
            relations = [relations]
        dic_res = {}
        for field in relations:
            if not 'relationship' in field or not 'name' in field:
                continue
            if not 'parent' in field['relationship'] or not 'link' in field['relationship']:
                raise DatasetError("relationship is not correct")
            rel = field['relationship']['link']
            f_parent = field['relationship']['parent']
            f_field = field['name']
            name_rel = f_field + ' - ' + f_parent
            if self.nindex(f_parent) is None or self.nindex(f_field) is None:
                raise DatasetError("field's name is not present in data")
            dic_res[name_rel] = self.check_relation(
                f_field, f_parent, rel, False)
        if len(dic_res) == 1:
            return list(dic_res.values())[0]
        return dic_res


class DatasetError(Exception):
    # %% errors
    ''' Dataset Exception'''
    # pass
