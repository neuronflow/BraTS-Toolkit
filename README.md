                    ____           _____ ____      _____           _ _    _ _   
                   | __ ) _ __ __ |_   _/ ___|    |_   _|__   ___ | | | _(_) |_ 
                   |  _ \| '__/ _` || | \___ \      | |/ _ \ / _ \| | |/ / | __|
                   | |_) | | | (_| || |  ___) |     | | (_) | (_) | |   <| | |_ 
                   |____/|_|  \__,_||_| |____/      |_|\___/ \___/|_|_|\_\_|\__|
                                                                                
# BraTS Toolkit: What is it and what can I use it for?
Abstract:
>BraTS Toolkit is a holistic approach to brain tumor segmentation and consists out of out of three components:
    First, the BraTS Preprocessor facilitates data standardization and preprocessing for researchers and clinicians alike. It covers the entire image analysis workflow prior to tumor segmentation, from image conversion and registration to brain extraction. Second, BraTS Segmentor enables orchestration of BraTS brain tumor segmentation algorithms for generation of fully-automated segmentations. Finally, BraTS Fusionator can combine the resulting candidate segmentations into consensus segmentations using fusion methods such as majority voting and iterative SIMPLE fusion. The capabilities of our tools are illustrated with a practical example to enable easy translation to clinical and scientific practice.

## Citation
If you use BraTS Toolkit please cite:

Citation / Paper link

## Brats Preprocessor
BraTS Preprocessor facilitates data standardization and preprocessing for researchers and clinicians alike. It covers the entire image analysis workflow prior to tumor segmentation, from image conversion and registration to brain extraction.

### Processing Modi
### GPU skullstripping: "gpu"
### CPU skullstripping: "cpu"
### GPU defacing: "gpu_defacing"
### CPU defacing: "cpu_defacing"

### Graphical User Interface (GUI)
You can find instructions to use and download the GUI variant here: https://neuronflow.github.io/BraTS-Preprocessor/

### Python package
Please have a look at `0_preprocessing_batch.py` and `0_preprocessing_single.py` in this repository for a demo application.

### Command Line Interface (CLI)
TODO

## Brats Segmentor
BraTS Segmentor enables orchestration of BraTS brain tumor segmentation algorithms for generation of fully-automated segmentations.
### Python package
Please have a look at `1_segmentation.py` in this repository for a demo application.

### Command Line Interface (CLI)
TODO

## Brats Fusionator
BraTS Fusionator can combine the resulting candidate segmentations into consensus segmentations using fusion methods such as majority voting and iterative SIMPLE fusion.
### Python package
Please have a look at `2_fusion.py` in this repository for a demo application.

### Command Line Interface (CLI)
TODO

## Source code
The source code for BraTS Toolkit can be found here: https://github.com/neuronflow/BraTS-Toolkit-Source

## Contact / Feedback / Questions
Open an issue in this git repository or contact us per email.

Florian Kofler
florian.kofler [at] tum.de

Christoph Berger
c.berger [at] tum.de