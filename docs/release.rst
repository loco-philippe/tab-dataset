Version x.y.z
=============

0.1.1 RC1 (2023-01-05)
--------------------

- add method `check_relation` in Cfield class
- add 'unique' Field in string representation 
- consistency with NTV for default datatype 'json'
- bugs #1, #2

0.1.0 RC1 (2023-11-23)
--------------------

- First release candidate

- **constructor**
    - Dataset : from CSV, from NTV, from file
    - Field : from NTV, from boolean list, like

- **analysis**
    - Interface with TAB-analysis package (Field category, Partitions, Relationship category, Tree representation, indicators)

- **structure**
    - merging, coupling, extending
    - check Relationship
    - filter, sort, ordering

- **interface**
    - Interface with pandas-NTV package 
    - json, csv, pandas Dataframe/Series, xarray
    - plot, view, voxel

- **information**
    - Indicator (Dataset, Fields, Size, Structure, Consistency)

- **data**
    - Simple data (Sdataset, Sfield)
    - Semantic NTV data (Ndataset, Nfield)

- **accessibility**
    - Selecting 
    - Updating