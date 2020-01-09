import os
from path import Path

from brats_toolkit.preprocessor import Preprocessor

# instantiate
prep = Preprocessor()

# define inputs and outputs
inputDir = "example_data/input_preprocessor_batch_processing/exams_to_preprocess"
outputDir = "example_data/output_preprocessor_batch"


# execute it
prep.batch_preprocess(exam_import_folder=inputDir,
                      exam_export_folder=outputDir, mode="gpu", confirm=True, skipUpdate=False)
