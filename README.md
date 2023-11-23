### ***TAB-dataset : A tool for structuring tabular data***

*TAB-dataset analyzes, measures and transforms the relationships between Fields in any tabular Dataset.*

*The TAB-dataset tool is part of the [Environmental Sensing Project](https://github.com/loco-philippe/Environmental-Sensing#readme)*

For more information, see the [user guide](https://loco-philippe.github.io/tab-dataset/docs/user_guide.html) or the [github repository](https://github.com/loco-philippe/tab-dataset).

# What is TAB-dataset ?

## Principles

In tabular data, columns and rows are not equivalent, the columns (or fields) represent the 'semantics' of the data and the rows represent the objects arranged according to the structure defined by the columns.

The TAB-dataset tool measures and analyzes relationships between fields via the [TAB-analysis tool](https://github.com/loco-philippe/tab-analysis#readme).

TAB-dataset uses relationships between fields to have an optimized JSON format (JSON-TAB format).

It also identifies data that does not respect given relationships.

Finally, it proposes transformations of the data set to respect a set of relationships.

## Examples

Here is a price list of different foods based on packaging.

| 'plants'    | 'quantity' | 'product' | 'price' |
|-------------|------------|-----------|---------|
| 'fruit'     | '1 kg'     | 'apple'   | 1       |
| 'fruit'     | '10 kg'    | 'apple'   | 10      |
| 'fruit'     | '1 kg'     | 'orange'  | 2       |
| 'fruit'     | '10 kg'    | 'orange'  | 20      |
| 'vegetable' | '1 kg'     | 'peppers' | 1.5     |
| 'vegetable' | '10 kg'    | 'peppers' | 15      |
| 'fruit'     | '1 kg'     | 'banana'  | 0.5     |
| 'fruit'     | '10 kg'    | 'banana'  | 5       |

In this example, we observe two kinds of relationships:

- classification ("derived" relationship): between 'plants' and 'product' (each product belongs a plant)
- crossing ("crossed" relationship): between 'product' and 'quantity' (all the combinations of the two fields are present).

Another observation is that each record has a specific combination of 'product' and 'quantity', it will be possible to convert this dataset in matrix:

|   price   | '1 kg' | '10 kg'|
|-----------|--------|--------|
| 'apple'   | 1      | 10     |
| 'orange'  | 2      | 20     |
| 'peppers' | 1.5    | 15     |
| 'banana'  | 0.5    | 5      |

```python
In [1]: # creation of the `prices` object 
        from tab_dataset import Sdataset
        tabular = {'plants':   ['fruit', 'fruit','fruit',   'fruit','vegetable','vegetable','fruit',  'fruit' ],
                   'quantity': ['1 kg' , '10 kg', '1 kg',   '10 kg',  '1 kg',    '10 kg',   '1 kg',   '10 kg' ], 
                   'product':  ['apple', 'apple', 'orange', 'orange', 'peppers', 'peppers', 'banana', 'banana'], 
                   'price':    [1,       10,      2,        20,       1.5,       15,        0.5,      5       ]}
        prices = Sdataset.ntv(tabular)

In [2]: # the `field_partition` method return the main structure of the dataset (see TAB-analysis)
        prices.field_partition(mode='id')
Out[2]: {'primary': ['quantity', 'product'],
         'secondary': ['plants'],
         'unique': [],
         'variable': ['price']}

In [4]: # we can send the data to tools supporting the identified data structure
        prices.to_xarray()
Out[4]: <xarray.DataArray 'price' (quantity: 2, product: 4)>
        array([[1, 2, 1.5, 0.5],
               [10, 20, 15, 5]], dtype=object)
        Coordinates:
        * quantity  (quantity) object '1 kg' '10 kg'
        * product   (product)  object 'apple' 'orange' 'peppers' 'banana'
          plants    (product)  object 'fruit' 'fruit' 'vegetable' 'fruit'

In [5]: # what if an error occurs ?
        tabul_2 = {'plants':   ['fruit', 'fruit','fruit', 'fruit','vegetable','vegetable','vegetable','fruit' ],
                   'quantity': ['1 kg' , '10 kg', '1 kg',   '10 kg',  '1 kg',    '10 kg',   '1 kg',   '10 kg' ], 
                   'product':  ['apple', 'apple', 'orange', 'orange', 'peppers', 'peppers', 'banana', 'banana'], 
                   'price':    [1,       10,      2,        20,       1.5,       15,        0.5,      5       ]}
        prices = Sdataset.ntv(tabul_2)

In [6]: # the relationship is no more 'derived'
        prices.relation('plants', 'product').typecoupl
Out[6]: 'linked'

In [7]: # how much data is prohibited from being 'derived' ?
        prices.relation('plants', 'product').distomin
Out[7]: 1

In [8]: # What data needs to be corrected ?
        prices.check_relation('plants', 'product', 'derived', value=True)
Out[8]: {'row': [6, 7],
         'plants': ['vegetable', 'fruit'],
         'product': ['banana', 'banana']}
```

## Dataset structure

To analyze the relationships between fields, a particular modeling is used:

- each field is transformed into a list of distinct values and a list of pointers to these values
- the analysis is then carried out on these lists of pointers

> Example :
>
> The field: ['john', 'anna', 'paul', 'anna', 'john', 'lisa'] is transformed into:
>
> - a first list of values ['john', 'anna', 'paul', ' lisa']
> - a second list of pointers: [0, 1, 2, 1, 0, 3].
>
> We find for example this format in the 'categorical' data of pandas DataFrame.

## JSON interface

TAB-dataset uses relationships between fields to have an optimized JSON format ([JSON-TAB format](https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-TAB-standard.pdf)).

```python
In [9]: # the JSON length (equivalent to CSV length) is not optimized
        len(json.dumps(tabular))
Out[9]: 309

In [10]: # the JSON-TAB format is optimized
        len(json.dumps(prices.to_ntv().to_obj()))
Out[10]: 193

In [10]: prices.to_ntv().to_obj()
Out[10]: {'plants': [['fruit', 'vegetable'], 2, [0, 0, 1, 0]],
          'quantity': [['1 kg', '10 kg'], [1]],
          'product': [['apple', 'orange', 'peppers', 'banana'], [2]],
          'price': [1, 10, 2, 20, 1.5, 15, 0.5, 5]}

In [11]: # the JSON-TAB format is reversible
         Sdataset.from_ntv(prices.to_ntv().to_obj()) == prices
Out[11]: True
```

## Uses

TAB-dataset accepts pandas Dataframe, json data ([NTV format](https://github.com/loco-philippe/NTV#readme)) and simple structure like list of list or dict of list.

Possible uses are as follows:

- control of a dataset in relation to a data model,
- quality indicators of a dataset
- analysis of datasets
- error detection and correction,
- generation of optimized data formats (alternative to CSV format)
- interface to specific applications
