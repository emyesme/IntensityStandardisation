
This repository contains a dockerfile which install 
- fsl v5.0.1
- python3.6.4
- SimpleITK
- the repository of [intensity normalization](https://github.com/jcreinhold/intensity-normalization)

Also, copy and configure the files siena_standardisation.py and run_intensities.py where 

- z-score method
- fuzzy c-means based white matter segmentation
- kernel density estimation based white matter segmentation
- gaussian mixture model based white matter segmentation
- piece wise linear histogram matching method
- white stripe method
- RAVEL method

The methods are implemented for the FSL-SIENA v5.0.1 pipeline ![Alt](pipeline.png "pipeline before intensity standardisation before registration)

To use the dockerfile in the repository it is **necessary** to have docker.io installed v19.03.8 or later and perform the following instructions

1. clone the repository
2. Download [ROBEX](https://www.nitrc.org/projects/robex/)
2. Move the folder named ROBEX to the cloned repository
2. Inside the local repository execute ```docker build . ``` **this is going to take some time (hours)**
4. To bind the docker container to the folder data, use 
```docker run -it --mount type=bind,src=/path/to/repository/data,dst=/data container_id_or_tag```

To use the pipeline, here is an example with the kernel density estimation method:

``` ./src/siena_standardisation.py -b mri_image_1.nii.gz -f mri_image_2.nii.gz -s kde -o /data/ ```

Instructions:

```
Usage:  ./src/siena_standardisation.py -b path to baseline MRI T1-w scan (nii or nii.gz file)
        -f path to follow up MRI T1-w scan (nii or nii.gz file)
        -s intensity standardisation method to use, options:
        zscore: z-zscore method
        fcm: fuzzy c-means based white matter segmentation
        gmm: gaussian mixture model based white matter segmentation
        kde: kernel density estimation based white matter segmentation (recommmended)
        hm: piecewise linear histogram matching
        ws: white stripe method 
        RAVEL: Removal of artificial voxel effect by linear regression
        -o output directory

```
