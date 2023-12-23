import os
import shutil
from pathlib import Path


def tempFiler(orgFilePath, modality, tempFolder):
    stemName = Path(orgFilePath).stem
    stemName = stemName.rsplit(".", 2)[0]
    stemName = stemName + "_" + modality + ".nii.gz"

    tempFile = os.path.join(tempFolder, stemName)
    # print("tempFile:", tempFile)
    shutil.copyfile(orgFilePath, tempFile)
    return tempFile
