This repository contains a dockerfile and code to perform the SIENA tool from FSL  package with the a proposed pipeline presented later.

## Requirements

Requirements to perform the code:

- FSL v5.0.1 [1]
- Python v3.6.4
- SimpleITK v2.0.1 [2]
- the repository of [intensity normalization](https://github.com/jcreinhold/intensity-normalization) [3]
- [ROBEX](https://www.nitrc.org/projects/robex/) [4]

The dockerfile copy and configure the files siena_standardisation.py and run_intensities.py with:

- Z-score method
- Fuzzy c-means based white matter segmentation method
- Kernel density estimation based white matter segmentation method
- Gaussian mixture model based white matter segmentation method
- Piece wise linear histogram matching method [5]
- White stripe method [6]
- RAVEL method [7]

The methods are implemented for the FSL-SIENA v5.0.1 pipeline ![pipeline](/pipeline.png)

## Instructions

To use the dockerfile is **necessary** to have docker.io installed v19.03.8 or later and perform the following instructions

1. clone the repository
2. Download [ROBEX](https://www.nitrc.org/projects/robex/)
3. Move the folder named ROBEX to the cloned repository
4. Inside the local repository execute ```docker build . ``` <br/> 
**this is going to take some time (hours)**
5. To bind the docker container to the folder data, use <br/> 
```docker run -it --mount type=bind,src=/path/to/repository/data,dst=/data container_id_or_tag```

## Usage

To use the pipeline, here is an example with the kernel density estimation method from the data folder:<br/> 

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

## Reference

[1] M. Jenkinson, C. F. Beckmann, T. E. Behrens, M. W. Woolrich, and S. M. Smith, “Fsl,” Neuroimage, vol. 62, no. 2, pp. 782–790, 2012.<br>
[2] R. Beare, B. Lowekamp, and Z. Yaniv, “Image segmentation, registration and characterization in r with simpleitk,” Journal of statistical software, vol. 86, 2018.<br>
[3] J. C. Reinhold, B. E. Dewey, A. Carass, and J. L. Prince, “Evaluating the impact of intensity normalization on MR image synthesis,” in Medical Imaging 2019: Image Processing, vol. 10949, p. 109493H, International Society for Optics and Photonics, 2019.<br>
[4] J. E. Iglesias, C.-Y. Liu, P. M. Thompson, and Z. Tu, “Robust brain extraction across datasets and comparison with publicly available methods,” IEEE transactions on medical imaging, vol. 30, no. 9, pp. 1617–1634, 2011.<br>
[5] L. G. Nyúl, J. K. Udupa, and X. Zhang, “New variants of a method of mri scale standardization,” IEEE transactions on medical imaging, vol. 19, no. 2, pp. 143–150, 2000.<br>
[6] R. T. Shinohara, E. M. Sweeney, J. Goldsmith, N. Shiee, F. J. Mateen, P. A. Calabresi, S. Jarso, D. L. Pham, D. S. Reich, C. M. Crainiceanu, et al., “Statistical normalization techniques for magnetic resonance imaging,” NeuroImage: Clinical, vol. 6, pp. 9–19, 2014.<br>
[7] J.-P. Fortin, E. M. Sweeney, J. Muschelli, C. M. Crainiceanu, R. T. Shinohara, A. D. N. Initiative, et al., “Removing inter-subject technical variability in magnetic resonance imaging studies,” NeuroImage, vol. 132, pp. 198–212, 2016. <br>
