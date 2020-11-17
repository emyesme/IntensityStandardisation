from os import system, getcwd, makedirs, walk, rename, remove
from os.path import exists, isfile, join, sep
import shutil

# run_synthseg: string, string -> void
# execute the synthseg tools from https://github.com/BBillot/SynthSeg
# use the posterior nifti output (probability maps) to fill the gaps
# gaps present in the lesions area of the infile nifti image
# and save the new segmentation labelled map


def run_synthseg(infile, outfolder):
    import subprocess
    import time

    subprocess.call(["python", DIRSYNTHSEG, infile, outfolder + sep,
                     "--out_posteriors", outfolder + sep + "posteriors.nii.gz"])

    name = infile.split(sep)[-1]

    if isfile(join(outfolder, name.split(".")[0]+'_seg.nii.gz')):
        seg_vol = nib.load(join(outfolder, name.split(".")
                                [0]+'_seg.nii.gz')).get_data()
    else:
        namefile = name.split(".")[0]+'_seg.nii.gz'
        raise ValueError("Error: %s was not created", namefile)

    # filling gaps of lesions
    posteriors = nib.load(join(outfolder, "posteriors.nii.gz"))
    data = posteriors.get_fdata()
    mask = nib.load(infile).get_fdata() != 0
    # here the gaps are fill
    Acor = np.multiply(np.argmax(data[:, :, :, 1:], axis=3), mask)
    # delete innecesary files
    remove(join(outfolder, "posteriors.nii.gz"))
    remove(join(outfolder, name.split(".")[0]+'_seg.nii.gz'))
    # save output
    nib.save(nib.Nifti1Image(Acor, posteriors.affine), join(
        outfolder, name.split(".")[0]+'_seg.nii.gz'))

# run_intensity_delis: string, string -> void
# return the synthseg tool, create the white matter mask based on the labelled map
# erode the mask, get the last mode and compute a normalisation
# save the original image into robex folder


def run_intensity_delis(infile, outfolder):
    from scipy.ndimage import binary_erosion, generate_binary_structure
    from intensity_normalization.utilities import hist

    # get the segmentation mask with synthseg tool
    run_synthseg(infile, outfolder)

    name = infile.split(sep)[-1]

    # load the image and segmentation mask
    in_vol = nib.load(infile)

    if isfile(join(outfolder, name.split(".")[0]+'_seg.nii.gz')):
        seg_vol = nib.load(join(outfolder, name.split(".")
                                [0]+'_seg.nii.gz')).get_data()
    else:
        namefile = name.split(".")[0]+'_seg.nii.gz'
        raise ValueError("Error: %s was not created" % namefile)

    # 2.get the white matter from the mask
    mask = np.logical_or(seg_vol == 18, seg_vol == 3)

    header = in_vol.header
    affine = in_vol.affine
    in_vol = in_vol.get_data()

    # 3. erode the mask
    mask = binary_erosion(mask, generate_binary_structure(3, 1))

    # 4. get the points on the data of the tails at 5% and 95%
    # min_p = np.percentile(in_vol[mask], 5)
    # max_p = np.percentile(in_vol[mask], 95)

    # 5. get the data between with no tails(outliers)
    values = in_vol[mask].flatten()
    # values = values[values > min_p]
    # values = values[values < max_p]

    # 6. get the mean and standard deviation
    # from scipy.stats import mode
    # wm_peak = mode(values)[0]
    wm_peak = hist.get_last_mode(values)
    # std = values.std()
    # 7. perform the zscore formula and save the data in a image format
    normalised = nib.Nifti1Image(in_vol/wm_peak, affine, header)
    # 8. save the normalized image
    nib.save(normalised, join(
        outfolder, name.split(".")[0]+"_delis.nii.gz"))

    if not exists(join(outfolder, "robex")):
        makedirs(join(outfolder, "robex"))

    shutil.move(join(outfolder, name), join(outfolder, "robex"))

# run_intensity_zscore: string, string -> void
# execute the z-score method to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_zscore(infile, outfolder):

    from intensity_normalization.normalize import zscore
    from intensity_normalization.utilities import io

    filename = infile.split(sep)[-1].split(".")[0]
    i = io.open_nii(infile)
    b_mask = io.open_nii(
        join(outfolder, "robex_masks", filename+"_mask.nii.gz"))

    if not exists(join(outfolder, "Robex")):
        makedirs(join(outfolder, "Robex"))

    print('running intensity zscore...')
    normalized = zscore.zscore_normalize(i, b_mask)
    io.save_nii(normalized, join(outfolder, filename + "_zscore.nii.gz"))
    shutil.move(join(infile), join(outfolder, "Robex"))


# run_intensity_kde: string, string -> void
# execute the kernel density estimation method  based white matter segmentation to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder

def run_intensity_kde(infile, outfolder):
    from intensity_normalization.normalize import kde
    from intensity_normalization.utilities import io

    filename = infile.split(sep)[-1].split(".")[0]
    i = io.open_nii(join(outfolder, infile))
    b_mask = io.open_nii(
        join(outfolder, "robex_masks", filename+"_mask.nii.gz"))

    if not exists(join(outfolder, "Robex")):
        makedirs(join(outfolder, "Robex"))

    normalized = kde.kde_normalize(i, b_mask)
    io.save_nii(normalized, join(outfolder, filename+"_kde.nii.gz"))
    shutil.move(join(outfolder, infile), join(outfolder, "Robex"))

# run_intensity_fcm: string, string -> void
# execute the fuzzy c-means  based white matter segmentation to the infile nifti image
# use the robex_masks images, create white matter masks and use infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_fcm(infile, outfolder):

    from intensity_normalization.normalize import fcm
    from intensity_normalization.utilities import io

    if not exists(join(outfolder, "Robex")):
        makedirs(join(outfolder, "Robex"))

    if not exists(join(outfolder, "wm_masks")):
        makedirs(join(outfolder, "wm_masks"))

    filename = infile.split(sep)[-1].split(".")[0]
    i = io.open_nii(infile)
    b_mask = io.open_nii(
        join(outfolder, "robex_masks", filename+"_mask.nii.Wgz"))
    wm_mask = fcm.find_wm_mask(i, b_mask)
    normalized = fcm.fcm_normalize(i, wm_mask)
    io.save_nii(wm_mask, join(
        outfolder, "wm_masks", filename+"_wmmask.nii.gz"))
    io.save_nii(normalized, join(outfolder, filename+"_fcm.nii.gz"))
    shutil.move(join(infile), join(outfolder, "Robex"))

# run_intensity_gmm: string, string -> void
# execute the gaussian mixture model  based white matter segmentation to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_gmm(infile, outfolder):
	from intensity_normalization.normalize import gmm
	from intensity_normalization.utilities import io

	if not exists(join(outfolder, "Robex")):
		makedirs(join(outfolder, "Robex"))

	filename = infile.split(sep)[-1].split(".")[0]
	i = io.open_nii(join(outfolder, infile))
	b_mask = io.open_nii(join(outfolder, "robex_masks", filename+"_mask.nii.gz"))
	normalized = gmm.gmm_normalize(i, b_mask)
	io.save_nii(normalized,join(outfolder,filename+"_gmm.nii.gz"))
    shutil.move(join(outfolder, infile), join(outfolder, "Robex"))

# run_intensity_ws: string, string -> void
# execute white stripe method to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_ws(infile, outfolder):

    from intensity_normalization.normalize import whitestripe
    from intensity_normalization.utilities import io

    filename = infile.split(sep)[-1].split(".")[0]

    if not exists(join(outfolder, "Robex")):
        makedirs(join(outfolder, "Robex"))

    print('running intensity white stripe...')
    mask = whitestripe.whitestripe(io.open_nii(infile),  "T1")
    normalized = whitestripe.whitestripe_norm(io.open_nii(infile), mask)
    io.save_nii(normalized, join(outfolder, filename + "_ws.nii.gz"))
    shutil.move(join(infile), join(outfolder, "Robex"))

# run_intensity_ravel: string, string -> void
# execute RAVEL method to the infile nifti image
# use the robex_masks images, create csf masks and use infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder

def run_intensity_ravel(outfolder):
    from intensity_normalization.normalize import ravel
    from intensity_normalization.utilities import io, csf

    images = []
    brainMasks = []
    csfMasks = []
    _, _, filenames = next(walk(outfolder))
    for f in filenames:
        filename = f.split(sep)[-1].split(".")[0]
        images.append(io.open_nii(join(outfolder, f.split(sep)[-1])))
        brainMasks.append(io.open_nii(
            join(outfolder, 'robex_masks', filename+"_mask.nii.gz")))

    if not exists(join(outfolder, "Robex")):
        makedirs(join(outfolder, "Robex"))

    if not exists(join(outfolder, "csf_masks")):
        makedirs(join(outfolder, "csf_masks"))

    print("csf masks...")
    for image, brainMask, f in zip(images, brainMasks, filenames):
        filename = f.split(sep)[-1].split(".")[0]
        csfMask = csf.csf_mask(image, brainMask, contrast='T1',
                               csf_thresh=0.9, return_prob=False, mrf=0.25, use_fcm=False)
        output = nib.Nifti1Image(csfMask, None)
        io.save_nii(output, join(outfolder, 'csf_masks',
                                 filename+"_csfmask.nii.gz"))
        shutil.move(join(outfolder, f.split(sep)[-1]), join(outfolder, "Robex"))

    print('running intensity ravel...')
    ravel.ravel_normalize(join(outfolder, 'Robex'),
                          join(outfolder, 'csf_masks'),
                          'T1',
                          output_dir=outfolder,
                          write_to_disk=True,
                          do_whitestripe=True,
                          b=1,
                          membership_thresh=0.99,
                          segmentation_smoothness=0.25,
                          do_registration=False,
                          use_fcm=True,
                          sparse_svd=False,
                          csf_masks=True)

    for i in filenames:
        rename(join(outfolder, i.split(sep)[-1]), join(
            outfolder, i.split(sep)[-1].split(".")[0]+"_ravel.nii.gz"))


# run_intensity_ravel: string, string, string -> void
# execute histogram matching method to followup image
# using 15 landmarks, 

def run_intensity_hm(baselinedir,followupdir, outfolder):

	import SimpleITK as sitk

	HISTOGRAM_LEVELS = 1024
	NO_LANDMARKS = 15

	baseline = sitk.ReadImage(baselinedir)
	followup = sitk.ReadImage(followupdir)

	matcher = sitk.HistogramMatchingImageFilter()
	matcher.SetNumberOfHistogramLevels(HISTOGRAM_LEVELS)
	matcher.SetNumberOfMatchPoints(NO_LANDMARKS)
	matcher.ThresholdAtMeanIntensityOn()

	matched_followup = matcher.Execute(followup, baseline)

	print("moving...")
	if not exists(join(outfolder,"Robex")):
		makedirs(join(outfolder,"Robex"))

	shutil.move(followupdir, join(outfolder,'Robex'))

	sitk.WriteImage(matched_followup, followupdir)

    rename(baselinedir, baselinedir.split("."[0]+"_hm.nii.gz"))
    rename(followupdir, followupdir.split("."[0]+"_hm.nii.gz"))
