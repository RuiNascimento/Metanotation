# Metanotation
#### Scripts to get further functional anotations to MassTRIX results

##### Usage:

**1.** Clone or Download this repository

**2.** In metanotation.py change the following lines to correpond to the input and output file:
```python
file = 'test_files/masses.annotated.reformat.tsv'
output = 'test_files/annotated.csv'
```
The input file is expected to be an MassTRIX compunds in AGI format

------------

This package will create a local cache of already fetched compounds to speed up future look-up.
Cache files will be stored in cache/ and automatically re-download after 30 to mantain recent information from the respectives databases.
