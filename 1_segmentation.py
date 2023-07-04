import os
import datetime

from brats_toolkit.segmentor import Segmentor


# log
starttime = str(datetime.datetime.now().time())
print("*** starting at", starttime, "***")

# instantiate
seg = Segmentor(verbose=True)

# input files
t1File = "example_data/output_preprocessor_single/TCGA-DU-7294/hdbet_brats-space/TCGA-DU-7294_hdbet_brats_t1.nii.gz"
t1cFile = "example_data/output_preprocessor_single/TCGA-DU-7294/hdbet_brats-space/TCGA-DU-7294_hdbet_brats_t1c.nii.gz"
t2File = "example_data/output_preprocessor_single/TCGA-DU-7294/hdbet_brats-space/TCGA-DU-7294_hdbet_brats_t2.nii.gz"
flaFile = "example_data/output_preprocessor_single/TCGA-DU-7294/hdbet_brats-space/TCGA-DU-7294_hdbet_brats_fla.nii.gz"

# output
outputFolder = "example_data/output_segmentor/TCGA-DU-7294/"

# algorithms we want to select for segmentation

# 2019 algorithms
# cids = ["mic-dkfz", "scan", "xfeng", "lfb_rwth", "zyx_2019", "scan_2019"]

# 2020 algorithms
cids = ["isen-20", "hnfnetv1-20", "yixinmpl-20", "sanet0-20", "scan-20"]

# execute it
for cid in cids:
    try:
        outputFile = outputFolder + cid + ".nii.gz"
        seg.segment(
            t1=t1File,
            t2=t2File,
            t1c=t1cFile,
            fla=flaFile,
            cid=cid,
            outputPath=outputFile,
        )

    except Exception as e:
        print("error:", str(e))
        print("error occured for:", cid)

# log
endtime = str(datetime.datetime.now().time())
print("*** finished at:", endtime, "***")
