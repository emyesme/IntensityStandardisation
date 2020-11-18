from os import system, getcwd, makedirs, walk, rename, remove
from os.path import exists, isfile, join, sep
import nibabel as nib
import sys
import shutil

# run_intensity_zscore: string, string -> void
# execute the z-score method to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_zscore(infile, outfolder):

    from intensity_normalization.normalize import zscore
    from intensity_normalization.utilities import io
    try:
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
    except:
        e = sys.exc_info()
        print("Error: ", str(e[0]))
        print("Error: ", str(e[1]))
        print("Error: executing z-score method")
        sys.exit(2)

# run_intensity_kde: string, string -> void
# execute the kernel density estimation method  based white matter segmentation to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_kde(infile, outfolder):
    from intensity_normalization.normalize import kde
    from intensity_normalization.utilities import io

    try:
        filename = infile.split(sep)[-1].split(".")[0]
        i = io.open_nii(join(outfolder, infile))
        b_mask = io.open_nii(
            join(outfolder, "robex_masks", filename+"_mask.nii.gz"))

        if not exists(join(outfolder, "Robex")):
            makedirs(join(outfolder, "Robex"))

        normalized = kde.kde_normalize(i, b_mask)
        io.save_nii(normalized, join(outfolder, filename+"_kde.nii.gz"))
        shutil.move(join(outfolder, infile), join(outfolder, "Robex"))
    except:
        e = sys.exc_info()
        print("Error: ", str(e[0]))
        print("Error: ", str(e[1]))
        print("Error: executing kde method")
        sys.exit(2)
# run_intensity_fcm: string, string -> void
# execute the fuzzy c-means  based white matter segmentation to the infile nifti image
# use the robex_masks images, create white matter masks and use infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_fcm(infile, outfolder):

    from intensity_normalization.normalize import fcm
    from intensity_normalization.utilities import io

    try:
        if not exists(join(outfolder, "Robex")):
            makedirs(join(outfolder, "Robex"))

        if not exists(join(outfolder, "wm_masks")):
            makedirs(join(outfolder, "wm_masks"))

        filename = infile.split(sep)[-1].split(".")[0]
        i = io.open_nii(infile)
        b_mask = io.open_nii(
            join(outfolder, "robex_masks", filename+"_mask.nii.gz"))
        wm_mask = fcm.find_tissue_mask(i, b_mask)
        normalized = fcm.fcm_normalize(i, wm_mask)
        io.save_nii(wm_mask, join(
            outfolder, "wm_masks", filename+"_wmmask.nii.gz"))
        io.save_nii(normalized, join(outfolder, filename+"_fcm.nii.gz"))
        shutil.move(join(infile), join(outfolder, "Robex"))
    except:
        e = sys.exc_info()
        print("Error: ", str(e[0]))
        print("Error: ", str(e[1]))
        print("Error: executing fcm method")
        sys.exit(2)

# run_intensity_gmm: string, string -> void
# execute the gaussian mixture model  based white matter segmentation to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_gmm(infile, outfolder):
    from intensity_normalization.normalize import gmm
    from intensity_normalization.utilities import io
    try:
        if not exists(join(outfolder, "Robex")):
            makedirs(join(outfolder, "Robex"))

        filename = infile.split(sep)[-1].split(".")[0]
        i = io.open_nii(join(outfolder, infile))
        b_mask = io.open_nii(
            join(outfolder, "robex_masks", filename+"_mask.nii.gz"))
        normalized = gmm.gmm_normalize(i, b_mask)
        io.save_nii(normalized, join(outfolder, filename+"_gmm.nii.gz"))
        shutil.move(join(outfolder, infile), join(outfolder, "Robex"))
    except:
        e = sys.exc_info()
        print("Error: ", str(e[0]))
        print("Error: ", str(e[1]))
        print("Error: executing gmm method")
        sys.exit(2)

# run_intensity_ws: string, string -> void
# execute white stripe method to the infile nifti image
# use the robex_masks images and infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_ws(infile, outfolder):

    from intensity_normalization.normalize import whitestripe
    from intensity_normalization.utilities import io

    try:
        filename = infile.split(sep)[-1].split(".")[0]

        if not exists(join(outfolder, "Robex")):
            makedirs(join(outfolder, "Robex"))

        print('running intensity white stripe...')
        mask = whitestripe.whitestripe(io.open_nii(infile),  "T1")
        normalized = whitestripe.whitestripe_norm(io.open_nii(infile), mask)
        io.save_nii(normalized, join(outfolder, filename + "_ws.nii.gz"))
        shutil.move(infile, join(outfolder, "Robex"))
    except:
        e = sys.exc_info()
        print("Error: ", str(e[0]))
        print("Error: ", str(e[1]))
        print("Error: executing white stripe method")
        sys.exit(2)

# run_intensity_ravel: string, string -> void
# execute RAVEL method to the infile nifti image
# use the robex_masks images, create csf masks and use infile with
# intensity standardisation package from https://github.com/jcreinhold/intensity-normalization
# save the infile into the Robex folder


def run_intensity_ravel(outfolder):
    from intensity_normalization.normalize import ravel
    from intensity_normalization.utilities import io, csf

    try:
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

        print("creating csf masks...")
        for image, brainMask, f in zip(images, brainMasks, filenames):
            filename = f.split(sep)[-1].split(".")[0]
            csfMask = csf.csf_mask(image, brainMask, contrast='T1',
                                   csf_thresh=0.9, return_prob=False, mrf=0.25, use_fcm=False)
            output = nib.Nifti1Image(csfMask, None)
            io.save_nii(output, join(outfolder, 'csf_masks',
                                     filename+"_csfmask.nii.gz"))
            shutil.move(join(outfolder, f.split(
                sep)[-1]), join(outfolder, "Robex"))

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
                outfolder, i.split(sep)[-1].split(".")[0]+"_RAVEL.nii.gz"))
    except:
        e = sys.exc_info()
        print("Error: ", str(e[0]))
        print("Error: ", str(e[1]))
        print("Error: executing ravel method")
        sys.exit(2)

# run_intensity_ravel: string, string, string -> void
# execute histogram matching method to followup image
# given the standard scale from the baseline image


def run_intensity_hm(baselinedir, followupdir, outfolder):

    import SimpleITK as sitk
    try:
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
        if not exists(join(outfolder, "Robex")):
            makedirs(join(outfolder, "Robex"))

        shutil.move(followupdir, join(outfolder, 'Robex'))

        sitk.WriteImage(matched_followup, followupdir)

        rename(join(outfolder, baselinedir), join(
            outfolder, baselinedir.split(".")[0]+"_hm.nii.gz"))
        rename(join(outfolder, followupdir), join(
            outfolder, followupdir.split(".")[0]+"_hm.nii.gz"))
    except:
        e = sys.exc_info()
        print("Error: ", str(e[0]))
        print("Error: ", str(e[1]))
        print("Error: executing histogram matching method")
        sys.exit(2)
