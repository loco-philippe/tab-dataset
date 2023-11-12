### ***TAB-dataset : A tool for consistency of tabular structures***

A tool to explore relationships in tabular structures

For more information, see the [user guide](https://loco-philippe.github.io/tab_dataset/docs/user_guide.html) or the [github repository](https://github.com/loco-philippe/tab_dataset).

## Examples

```python
In [1]: from tab_dataset import Sdataset
        tabular = {'plants':   ['fruit', 'fruit','fruit',   'fruit','vegetable','vegetable','fruit',  'fruit' ],
                   'quantity': ['1 kg' , '10 kg', '1 kg',   '10 kg',  '1 kg',    '10 kg',   '1 kg',   '10 kg' ], 
                   'product':  ['apple', 'apple', 'orange', 'orange', 'peppers', 'peppers', 'banana', 'banana'], 
                   'price':    [1,       10,      2,        20,       1.5,       15,        0.5,      5       ]}
        prices = Sdataset.ntv(tabular)

In [2]: prices.field_partition(mode='id')
Out[2]: {'primary': ['quantity', 'product'],
         'secondary': ['plants'],
         'unique': [],
         'variable': ['price']}

In [3]: prices.relation('plants', 'fruit').typecoupl
Out[3]: 'derived'

In [4]: prices.to_xarray()
Out[4]: <xarray.DataArray 'price' (quantity: 2, product: 4)>
        array([[1, 2, 1.5, 0.5],
               [10, 20, 15, 5]], dtype=object)
        Coordinates:
        * quantity  (quantity) object '1 kg' '10 kg'
        * product   (product)  object 'apple' 'orange' 'peppers' 'banana'
          plants    (product)  object 'fruit' 'fruit' 'vegetable' 'fruit'
```

```python
In [5]: tabul_2 = {'plants':   ['fruit', 'fruit','fruit', 'fruit','vegetable','vegetable','vegetable','fruit' ],
                   'quantity': ['1 kg' , '10 kg', '1 kg',   '10 kg',  '1 kg',    '10 kg',   '1 kg',   '10 kg' ], 
                   'product':  ['apple', 'apple', 'orange', 'orange', 'peppers', 'peppers', 'banana', 'banana'], 
                   'price':    [1,       10,      2,        20,       1.5,       15,        0.5,      5       ]}
        prices = Sdataset.ntv(tabul_2)

In [6]: prices.relation('plants', 'product').typecoupl
Out[6]: 'linked'

In [7]: prices.check_relation('plants', 'product', 'derived', value=True)
Out[7]: {'row': [6, 7],
         'plants': ['vegetable', 'fruit'],
         'product': ['banana', 'banana']}
```
