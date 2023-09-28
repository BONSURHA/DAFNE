# DAFNE: a dataset of Fresco fragments

## INTRO
this program can generate a dataset of fragment using parameters and folder with image having this extension:
* png 
* jpg
* jpeg

## HOW TO USE

### required library
* numpy
* opencv-python
### required arguments
* input directory: the folder that contain/s the image/s

### optional arguments
* text file, where there are the parameters,  formatted as follows:

```
seed: 3500
num_fragments: 400
min_distance: 10
erosion_probability: 0.65
erosion_percentage: 25
removal_percentage: 10 
num_spurius: 4 
```
`removal_percentage` and `num_spurius` are optional parameters

* output directory
* spurius directory

also you can use this command to know how to add the parameters:
```console
python DAFNE.py -h
```

### To run the code: 

```console
python DAFNE.py arguments
```
### removal_fragments.py
after running DAFNE.py, you can run this script to remove fragments and, optional, to add spurius fragment, these functions are applied to a copy of the folder
#### required parameters
* input directory (a folder genereated by DAFNE.py)
* original image (the original image used to generate the input directory)
#### optional arguments
* text file, where there are the parameters,  formatted as follows:

```
seed: 3500
removal_percentage: 10
num_spurius: 4 
```
`num_spurius` is optional parameter

* output directory
* spurius directory (if you add in the parameters 'num_spurius')

#### To run the code: 

```console
python remove_fragments.py arguments
```








