#!/opt/conda/bin/python

from os import system, getcwd, makedirs, walk, rename, remove
from os.path import exists, isfile, join, sep, splitext
import shutil
import sys
import getopt
import nibabel as nib
from multiprocessing import Process
from scipy.stats import mode
import numpy as np
from run_intensities import run_intensity_zscore, run_intensity_fcm, run_intensity_gmm, run_intensity_hm, run_intensity_kde, run_intensity_ws, run_intensity_ravel

#all_processes = []
#BATCH_SIZE = 1
DIRROBEX = join(sep, "ROBEX")
#DIRINPUT = getcwd()
ISMETHODS = ["zscore", "fcm", "gmm", "kde", "hm", "ws", "RAVEL"]
DIRSIENA = join(sep, "src", "siena2.1")
ALLOWED_EXTENSIONS = {'nii.gz', 'nii', 'nifti.hdr'}

# given the robex extraction get the binary mask of them

# robexmask: string, string, string -> void
# this function receive the current path, the directory of the input nifti image
# and the name of the output nifti image and calculate the binary mask of the input image
# this based on the minimum value of the input nifti image
# and move the output binary mask into the robex_masks folder


def robexmask(path, infile, outfile):

    image = nib.load(infile)
    minfile = image.get_fdata().min()
    mask = minfile < image.get_fdata()
    nib.save(nib.Nifti1Image(mask, image.affine,
                             image.header), join(path, outfile))
    if not exists(join(path, "robex_masks")):
        makedirs(join(path, "robex_masks"))
    try:
        shutil.move(outfile, join(path, 'robex_masks'))
    except:
        e = sys.exc_info()[0]
        print("Error: ", str(e))
        print("Error: moving robex masks")
        sys.exit(2)

# run_intensity: string, string, string -> void
# this method use the correspondent method for the input nifti image
# based on the string isMethod


def run_intensity(infile, outfolder, isMethod):
    if isMethod == "zscore":
        run_intensity_zscore(infile, outfolder)
    elif isMethod == "fcm":
        run_intensity_fcm(infile, outfolder)
    elif isMethod == "gmm":
        run_intensity_zscore(infile, outfolder)
    elif isMethod == "kde":
        run_intensity_kde(infile, outfolder)
    elif isMethod == "ws":
        run_intensity_ws(infile, outfolder)
    elif isMethod == "RAVEL":
        run_intensity_ravel(infile, outfolder)
    elif isMethod == "delis":
        rrun_intensity_delis(infile, outfolder)
    else:
        print("Error: incorrect selection of intensity standardisation method")
        sys.exit(2)

# perform the brain registration with the flirt tool from siena
# flirt: string, array -> void
# perform the flirt method to the list of nifti images
# move the originals images into IS folder
# and the .mat, output of flirt, into the flirt_mat folder


def flirt(path, files):

    if not exists(join(path, "IS")):
        makedirs(join(path, "IS"))

    if not exists(join(path, "flirt_mat")):
        makedirs(join(path, "flirt_mat"))

    for f in files:
        if (".nii.gz" in f):
            shutil.move(join(path, f), join(path, "IS"))
            commandMat = "flirt -bins 256 -cost mutualinfo -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear -in {} -ref /opt/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz -omat {}"
            system(commandMat.format(join(path, "IS", f),
                                     join(path, f.split(".")[0]+"_flirt.mat")))

            shutil.move(
                join(path, f.split(".")[0]+"_flirt.mat"), join(path, "flirt_mat"))

            command = "flirt -in {} -ref /opt/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz -omat {} -applyxfm -init {} -out {}"
            system(command.format(join(path, "IS", f),
                                  join(path, "flirt_mat", f.split(
                                      ".")[0]+"_flirt.mat"),
                                  join(path, "flirt_mat", f.split(
                                      ".")[0]+"_flirt.mat"),
                                  join(path, f.split(".")[0]+"_flirt.nii.gz")))

# createTmp: string, string, string -> void
# calculate the brain_mask and valid_mask for the nifti images received
# and save it into the tmp folder
# this for the modification on the siena file


def createTmp(dir, fileA, fileB):

    if not exists(join(dir, "tmp")):
        makedirs(join(dir, "tmp"))

    A = nib.load(join(dir, fileA))
    B = nib.load(join(dir, fileB))

    minfileA = A.get_fdata().min()
    minfileB = B.get_fdata().min()

    maskA = minfileA < A.get_fdata()
    maskB = minfileB < B.get_fdata()

    nib.save(nib.Nifti1Image(maskA, A.affine, A.header),
             join(dir, "A_brain_mask.nii.gz"))
    nib.save(nib.Nifti1Image(maskB, B.affine, B.header),
             join(dir, "B_brain_mask.nii.gz"))

    commandvalidmasks = "cd {} && fslmaths {} -mul {} {} && cd .."
    system(commandvalidmasks.format(dir, "A_brain_mask.nii.gz",
                                    "B_brain_mask.nii.gz", "A_valid_mask_with_B.nii.gz"))
    system(commandvalidmasks.format(dir, "A_brain_mask.nii.gz",
                                    "B_brain_mask.nii.gz", "B_valid_mask_with_A.nii.gz"))
    try:
        shutil.move(join(dir, "A_brain_mask.nii.gz"),
                    join(dir, "tmp"))
        shutil.move(join(dir, "B_brain_mask.nii.gz"),
                    join(dir, "tmp"))
        shutil.move(join(dir, "A_valid_mask_with_B.nii.gz"),
                    join(dir, "tmp"))
        shutil.move(join(dir, "B_valid_mask_with_A.nii.gz"),
                    join(dir, "tmp"))
    except:
        e = sys.exc_info()[0]
        print("Error: ", str(e))
        print("Error: moving masks for siena")
        sys.exit(2)

# run_siena_command: string, string, tring, string -> void
# receive two nifti images and the path of the output folder
# and execute the siena command


def run_siena_command(dir, fileA, fileB, output):

    command = 'cd {} && {} {} {} -o {} -d'
    try:
        print(command.format(dir, DIRSIENA, fileA, fileB, output))
        system(command.format(dir, DIRSIENA, fileA, fileB, output))
    except:
        e = sys.exc_info()[0]
        print("Error: ", str(e))
        print("Error: during siena execution")
        sys.exit(2)

# run_robex: string, string, string -> void
# perform the ROBEX (brain extraction) to the infile images
# save the original infile nifti images in the Originals folder
# and return the brain nifti images with the outfile name


def run_robex(dir, infile, outfile):

    if not exists(join(dir, "Originals")):
        makedirs(join(dir, "Originals"))

    command = "cd {} && ./runROBEX.sh {} {}"
    system(command.format(DIRROBEX,
                          infile,
                          outfile))
    try:
        shutil.move(join(dir, infile), join(dir, "Originals"))

        if isfile(join(dir, infile.split(".")[0]+".nifti.img")):
            shutil.move(join(dir, infile.split(".")[
                        0]+".nifti.img"), join(dir, "Originals"))
    except:
        e = sys.exc_info()[0]
        print("Error: ", str(e))
        print("Error: moving files after robex execution")
        sys.exit(2)

# copyFiles: string, string, string -> void
# create the nameDir folder for the output files
# and copy the received files into the folder


def copyFiles(inputFile, outputDir, nameDir):

    if not exists(join(outputDir, nameDir)):
        makedirs(join(outputDir, nameDir))
    # DistUtilError possible if dir do not exist in DIRINPUT
    try:
        shutil.copy(inputFile, join(outputDir, nameDir))
        if "nifti.hdr" in inputFile:
            shutil.copy(inputFile.split(".")[
                        0]+".nifti.img", join(outputDir, nameDir))

    except:
        e = sys.exc_info()[0]
        print("Error: ", str(e))
        print("Error: making initial copy")
        sys.exit(2)

# allowed_files: string -> boolean
# check if the file path has the allowed extensions


def allowed_file(file):
    extension = ".".join(file.split(".")[1:])
    print(extension)
    return extension in ALLOWED_EXTENSIONS

# run_process: string, strig, string, string -> void
# given the args, two nifti images, the choosen methods
# and the given output direction and perform several steps
# 1. initial copy of the given nifti images
# 2. brain extraction with ROBEX
# 3. robex masks for the intensity standardisation method
# 4. intensity standardisation selected
# 5. registration of the images with FLIRT
# 6. masks for the siena execution
# 7. siena execution


def run_process(baselineFile, followupFile, isMethod, outputDir):

    # 1. inicial copy

    print("1. Start initial copy")

    nameDir = "output_siena_"+isMethod

    copyFiles(baselineFile, outputDir, nameDir)
    copyFiles(followupFile, outputDir, nameDir)

    print("End initial copy")

    # 2. robex
    print("2. Start robex")

    for f in [baselineFile, followupFile]:
        if allowed_file(f):
            run_robex(join(outputDir, nameDir),
                      join(outputDir, nameDir, f),
                      join(outputDir, nameDir, f.split(".")[0]+"_robex.nii.gz"))
        else:
            print("Error: Not allowed extension of ", f)
            sys.exit(2)

    print("End robex")

    # 3. masks for intensity standardisation
    robexFiles = []

    _, _, files = next(walk(join(outputDir, nameDir)))
    for f in files:
        if ("_robex.nii.gz" in f):
            robexFiles.append(f)

    print("3. Masks for intensity standardisation")

    for robexFile in robexFiles:
        robexmask(join(outputDir, nameDir),
                  join(outputDir, nameDir, robexFile),
                  join(outputDir, nameDir, robexFile.split(".")[0]+"_mask.nii.gz"))

    print("End masks for intensity standardisation")
    # 4. intensity standardisation
    print("4. Start intensity standardisation")

    if isMethod == "hm":
        run_intensity_hm(join(outputDir, nameDir, baselineFile.split(".")[0] + "_robex.nii.gz"),
                         join(outputDir, nameDir, followupFile.split(".")[0] + "_robex.nii.gz"),
                         join(outputDir, nameDir))
    else:
        for robexFile in robexFiles:
            run_intensity(join(outputDir, nameDir, robexFile),
                          join(outputDir, nameDir),
                          isMethod)

    print("End intensity standardisation")

    # 5. flirt
    print("5. Start flirt")

    isFiles = []
    _, _, files = next(walk(join(outputDir, nameDir)))
    for f in files:
        if ("_" + isMethod + ".nii.gz" in f):
            isFiles.append(f)

    flirt(join(outputDir, nameDir), isFiles)

    print("End flirt")

    # 6. masks for siena
    print("6. Start masks siena")

    flirtFiles = []
    _, _, files = next(walk(join(outputDir, nameDir)))
    for f in files:
        if ("_flirt.nii.gz" in f):
            flirtFiles.append(f)

    baselineFilePreprocessed = baselineFile.split(
        ".")[0]+"_robex_"+isMethod+"_flirt.nii.gz"
    followupFilePreprocessed = followupFile.split(
        ".")[0]+"_robex_"+isMethod+"_flirt.nii.gz"

    _, _, files = next(walk(join(outputDir, nameDir)))

    if ((baselineFilePreprocessed in files) and (followupFilePreprocessed in files)):

        createTmp(join(outputDir, nameDir),
                  baselineFilePreprocessed,
                  followupFilePreprocessed)

        print("End masks siena")

        # 7. siena execution
        print("7. Start siena")

        run_siena_command(join(outputDir, nameDir),
                          baselineFilePreprocessed,
                          followupFilePreprocessed,
                          "output_siena")
    else:
        print("Error: not found preprocessed files")
        sys.exit(2)
    print("End siena")

# array, int -> void
# create batches of the given size


def create_batches(iterable, n=1):
    current_batch = []
    for item in iterable:
        current_batch.append(item)
        if len(current_batch) == n:
            yield current_batch
            current_batch = []
    if current_batch:
        yield current_batch

# string -> void
# prepare processes to run process


def prepare_processes(DIRINPUT):
    for root, dirs, files in walk(DIRINPUT):
        for dir in dirs:
            if "0" in dir:
                p = Process(target=run_process, args=(dir, ))
                all_processes.append(p)

    for batch in create_batches(all_processes, BATCH_SIZE):
        for process in batch:
            process.start()
        for process in batch:
            process.join()


def main():
    # prepare_processes(DIRINPUT)
    baselineFile = ''
    followupFile = ''
    isMethod = ''
    outputDir = ''

    try:
        myopts, args = getopt.getopt(sys.argv[1:], "b:f:s:o:")
    except getopt.GetoptError as e:
        print(str(e))
        print("""Usage: %s 
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
        -o output directory""" % sys.argv[0])
        sys.exit(2)

    for option, argument in myopts:
        if ((option == "-b") and isfile(argument)):
            baselineFile = argument
        elif ((option == "-f") and isfile(argument)):
            followupFile = argument
        elif ((option == "-s") and (argument in ISMETHODS)):
            isMethod = argument
        elif ((option == "-o") and exists(argument)):
            outputDir = argument
        else:
            print("""Usage: %s 
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
        -o output directory""" % sys.argv[0])
            sys.exit(2)

    # print("base: ", baselineFile)
    # print("followup: ", followupFile)
    # print("method: ", isMethod)
    # print("output: ", outputDir)
    run_process(baselineFile, followupFile, isMethod, outputDir)


if __name__ == "__main__":
    main()
