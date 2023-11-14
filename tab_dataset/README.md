# Installation

## dataset package

The `tab_dataset` package includes

- `cdataset` module
  - class `Cdataset` : core class for datasets
  - class `DatasetAnalysis` : interface with TAB-Analysis package

- `dataset` module
  - class `Sdataset` : child `Cdataset` class for usual data
  - class `Ndataset` : child `Cdataset` class for complex data with NTV representation

- `dataset_interface` module
  - class `DatasetInterface` : Interface and conversion

- `cfield` module
  - class `Cfield` : core class for fields

- `field` module
  - class `Sfield` : child `Cfield` class for usual data
  - class `Nfield` : child `Cfield` class for complex data with NTV representation

- `field_interface` module
  - class `FieldInterface` : Interface and conversion

## installation

`tab_dataset` itself is a pure Python package. maintained on [tab-dataset github repository](https://github.com/loco-philippe/tab-dataset).

It can be installed with `pip`.

    pip install tab_dataset

dependency:

- None
