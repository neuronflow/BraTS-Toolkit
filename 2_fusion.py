import os
from path import Path
import datetime

from brats_toolkit.fusionator import Fusionator

# log
starttime = str(datetime.datetime.now().time())
print("*** starting at", starttime, "***")

# instantiate
fus = Fusionator(verbose=True)

# input
SOURCEDIR = Path("example_data/output_segmentor/TCGA-DU-7294/")
# output
OUTPUTDIR = "example_data/output_fusionator/TCGA-DU-7294/"

# cids of the algorithms we want to fuse
cids = ['mic-dkfz', 'scan', 'xfeng', 'lfb_rwth', 'zyx_2019', 'scan_2019']

# segmentation file paths
segs = [SOURCEDIR + s + ".nii.gz" for s in cids]

# execution
# mav
mavPath = OUTPUTDIR + "mav.nii.gz"
fus.fuse(segmentations=segs, outputPath=mavPath, method='mav', weights=None)

# simple
simplePath = OUTPUTDIR + "simple.nii.gz"
fus.fuse(segmentations=segs, outputPath=simplePath,
         method='simple', weights=None)

# log
endtime = str(datetime.datetime.now().time())
print("*** finished at:", endtime, "***")
