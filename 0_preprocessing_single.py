from brats_toolkit.preprocessor import Preprocessor

# instantiate
prep = Preprocessor()

# define inputs
examName = "TCGA-DU-7294"
t1File = "example_data/input_preprocessor_single_processing/TCGA-DU-7294/TCGA-DU-7294-T1.nii.gz"
t1cFile = "example_data/input_preprocessor_single_processing/TCGA-DU-7294/TCGA-DU-7294-T1c.nii.gz"
t2File = "example_data/input_preprocessor_single_processing/TCGA-DU-7294/TCGA-DU-7294-T2.nii.gz"
flaFile = "example_data/input_preprocessor_single_processing/TCGA-DU-7294/TCGA-DU-7294-FLAIR.nii.gz"

# define outputs
outputDir = "example_data/output_preprocessor_single/TCGA-DU-7294"

# execute it
prep.single_preprocess(t1File=t1File, t1cFile=t1cFile, t2File=t2File, flaFile=flaFile,
                       outputFolder=outputDir, mode="cpu", confirm=True, skipUpdate=False, gpuid='0')
