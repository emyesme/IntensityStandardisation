This repository contains a dockerfile and code to perform the SIENA tool from FSL  package with the a proposed pipeline presented later.

## Requirements

Some of the important requirements to perform the code are:
- fsl v5.0.1
- python v3.6.4
- SimpleITK v2.0.1
- the repository of [intensity normalization](https://github.com/jcreinhold/intensity-normalization)
- [ROBEX](https://www.nitrc.org/projects/robex/)

The dockerfile copy and configure the files siena_standardisation.py and run_intensities.py with:

- z-score method
- fuzzy c-means based white matter segmentation method
- kernel density estimation based white matter segmentation method
- gaussian mixture model based white matter segmentation method
- piece wise linear histogram matching method
- white stripe method
- RAVEL method

The methods are implemented for the FSL-SIENA v5.0.1 pipeline ![pipeline](/pipeline.png)

## Instructions

To use the dockerfile in the repository it is **necessary** to have docker.io installed v19.03.8 or later and perform the following instructions

1. clone the repository
2. Download [ROBEX](https://www.nitrc.org/projects/robex/)
3. Move the folder named ROBEX to the cloned repository
4. Inside the local repository execute ```docker build . ``` 
**this is going to take some time (hours)**
5. To bind the docker container to the folder data, use 
```docker run -it --mount type=bind,src=/path/to/repository/data,dst=/data container_id_or_tag```

## Usage

To use the pipeline, here is an example with the kernel density estimation method from the data folder:

``` ./../src/siena_standardisation.py -b mri_image_1.nii.gz -f mri_image_2.nii.gz -s kde -o /data/ ```

Instructions:

```
Usage:  ./src/siena_standardisation.py -b path to baseline MRI T1-w scan (nii or nii.gz file)
        -b path to baseline MRI T1-w scan (nii or nii.gz file)
        -f path to follow up MRI T1-w scan (nii or nii.gz file)
        -s intensity standardisation method to use
        Options:
            zscore: z-zscore method
            fcm: fuzzy c-means based white matter segmentation
            gmm: gaussian mixture model based white matter segmentation
            kde: kernel density estimation based white matter segmentation (recommended)
            hm: piecewise linear histogram matching
            ws: white stripe method 
            RAVEL: Removal of artificial voxel effect by linear regression
        -o output directory

```
