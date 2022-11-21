                    ____           _____ ____      _____           _ _    _ _   
                   | __ ) _ __ __ |_   _/ ___|    |_   _|__   ___ | | | _(_) |_ 
                   |  _ \| '__/ _` || | \___ \      | |/ _ \ / _ \| | |/ / | __|
                   | |_) | | | (_| || |  ___) |     | | (_) | (_) | |   <| | |_ 
                   |____/|_|  \__,_||_| |____/      |_|\___/ \___/|_|_|\_\_|\__|
                                                                                
# BraTS Toolkit: What is it and what can I use it for?
Abstract:
>BraTS Toolkit is a holistic approach to brain tumor segmentation and consists out of out of three components:
    First, the BraTS Preprocessor facilitates data standardization and preprocessing for researchers and clinicians alike. It covers the entire image analysis workflow prior to tumor segmentation, from image conversion and registration to brain extraction. Second, BraTS Segmentor enables orchestration of BraTS brain tumor segmentation algorithms for generation of fully-automated segmentations. Finally, BraTS Fusionator can combine the resulting candidate segmentations into consensus segmentations using fusion methods such as majority voting and iterative SIMPLE fusion. The capabilities of our tools are illustrated with a practical example to enable easy translation to clinical and scientific practice.

## Installation
To install the most up to date version from the master branch please use the following pip install command:
```
pip install -e git+https://github.com/neuronflow/BraTS-Toolkit-Source.git@master#egg=brats_toolkit
```

We recommended installation in a virtual environment based on Python 3.10

Further, NVIDIA Docker Toolkit needs to be installed. Further instructions here: https://neuronflow.github.io/BraTS-Preprocessor/#dockerinstallation

## Issues
When running into issues please use the issue tracker here on Github: https://github.com/neuronflow/BraTS-Toolkit/issues
So others can profit and contribute as well.

## Citation
If you use BraTS Toolkit please cite:

https://www.frontiersin.org/articles/10.3389/fnins.2020.00125/full

Kofler, F., Berger, C., Waldmannstetter, D., Lipkova, J., Ezhov, I., Tetteh, G., Kirschke, J., Zimmer, C., Wiestler, B., & Menze, B. H. (2020). BraTS Toolkit: Translating BraTS Brain Tumor Segmentation Algorithms Into Clinical and Scientific Practice. Frontiers in neuroscience, 14, 125. https://doi.org/10.3389/fnins.2020.00125

```
@article{kofler2020brats,
  title={BraTS toolkit: translating BraTS brain tumor segmentation algorithms into clinical and scientific practice},
  author={Kofler, Florian and Berger, Christoph and Waldmannstetter, Diana and Lipkova, Jana and Ezhov, Ivan and Tetteh, Giles and Kirschke, Jan and Zimmer, Claus and Wiestler, Benedikt and Menze, Bjoern H},
  journal={Frontiers in neuroscience},
  pages={125},
  year={2020},
  publisher={Frontiers}
}
```

Please also cite the following original authors of the algorithms who make this repository and tool possible:

| Docker Image                | Paper                                                                                                                                                                                                                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| econib    | Marcinkiewicz, M., Nalepa, J., Lorenzo, P., Dudzik, W., & Mrukwa, G. (2018). Segmenting brain tumors from MRI using cascaded multi-modal U-Nets. In International MICCAI Brainlesion Workshop (pp. 13–24).                                                                                     |
| mic-dkfz  | Isensee, F., Kickingereder, P., Wick, W., Bendszus, M., & Maier-Hein, K. (2018). No new-net. In International MICCAI Brainlesion Workshop (pp. 234–244).                                                                                                                                       |
| scan      | McKinley, R., Meier, R., & Wiest, R. (2018). Ensembles of densely-connected CNNs with label-uncertainty for brain tumor segmentation. In International MICCAI Brainlesion Workshop (pp. 456–465).                                                                                              |
| xfeng     | Feng, X., Tustison, N., & Meyer, C. (2019). Brain Tumor Segmentation Using an Ensemble of 3D U-Nets and Overall Survival Prediction Using Radiomic Features. In Brainlesion: Glioma, Multiple Sclerosis, Stroke and Traumatic Brain Injuries (pp. 279–288). Springer International Publishing. |
| lfb_rwth  | Weninger, L., Rippel, O., Koppers, S., & Merhof, D. (2019). Segmentation of Brain Tumors and Patient Survival Prediction: Methods for the BraTS 2018 Challenge. In Brainlesion: Glioma, Multiple Sclerosis, Stroke and Traumatic Brain Injuries (pp. 3–12). Springer International Publishing. |
| gbmnet    | Nuechterlein, N., & Mehta, S. (2019). 3D-ESPNet with Pyramidal Refinement for Volumetric Brain Tumor Image Segmentation. In Brainlesion: Glioma, Multiple Sclerosis, Stroke and Traumatic Brain Injuries (pp. 245–253). Springer International Publishing.                                     |
| xyz_2019  | Zhao, Y.X., Zhang, Y.M., Song, M., & Liu, C.L. (2019). Multi-view Semi-supervised 3D Whole Brain Segmentation with a Self-ensemble Network. In Medical Image Computing and Computer Assisted Intervention – MICCAI 2019 (pp. 256–265). Springer International Publishing.                      |
| scan_2019 | McKinley, R., Rebsamen, M., Meier, R., & Wiest, R. (2020). Triplanar Ensemble of 3D-to-2D CNNs with Label-Uncertainty for Brain Tumor Segmentation. In Brainlesion: Glioma, Multiple Sclerosis, Stroke and Traumatic Brain Injuries (pp. 379–387). Springer International Publishing.          |
| isen-20 | upcoming publication          |
| hnfnetv1-20 | upcoming publication          |
| yixinmpl-20 | upcoming publication          |
| sanet0-20 | upcoming publication          |
| scan-20 | upcoming publication          |
| scan_lite-20 | upcoming publication          |



## Brats Preprocessor
BraTS Preprocessor facilitates data standardization and preprocessing for researchers and clinicians alike. It covers the entire image analysis workflow prior to tumor segmentation, from image conversion and registration to brain extraction.

### Processing Modi
BraTS Preprocessor offers the following preprocessing modes:
#### GPU brain extraction: "gpu"
Activates HD-BET in CUDA mode. Only supported when using NVIDIA docker (Linux operating systems only for the moment).
#### CPU brain extraction: "cpu"
Activates HD-BET or ROBEX in CPU mode depending on available RAM.
#### ROBEX brain extraction: "robex"
Activates Robex brain extraction.
#### GPU defacing: "gpu_defacing"
Activates GPU defacing - not implemented yet falls back to `cpu_defacing` for the moment. 
#### CPU defacing: "cpu_defacing"
Activates mri-deface to deface using CPU. Use this mode for further processing on the Kraken (https://neuronflow.github.io/kraken/)

### Single vs. batch processing
 BraTS preprocessor offers processing files in `batch` or `single` mode. Please have a look at the respective example scripts / CLI commands for information how to use them.
 
 For faster computation we strictly recommend the `batch` processing mode, which avoids additional overhead of spawning and shutting down multiple docker containers and instead does all the processing in one container.  

### Graphical User Interface (GUI)
You can find instructions to use and download the GUI variant here: https://neuronflow.github.io/BraTS-Preprocessor/

### Python package
Please have a look at `0_preprocessing_batch.py` and `0_preprocessing_single.py` in this repository for a demo application.

### Command Line Interface (CLI)
#### single file processing
Type `brats-preprocess -h` after installing the python package to see available options.
#### batch file processing
Type `brats-batch-preprocess -h` after installing the python package to see available options.


## Brats Segmentor
BraTS Segmentor enables orchestration of BraTS brain tumor segmentation algorithms for generation of fully-automated segmentations.
### Python package
Please have a look at `1_segmentation.py` in this repository for a demo application.

### Command Line Interface (CLI)
Type `brats-segment -h` after installing the python package to see available options.

## Brats Fusionator
BraTS Fusionator can combine the resulting candidate segmentations into consensus segmentations using fusion methods such as majority voting and iterative SIMPLE fusion.
### Python package
Please have a look at `2_fusion.py` in this repository for a demo application.

### Command Line Interface (CLI)
Type `brats-fuse -h` after installing the python package to see available options.

## Source code
The source code for BraTS Toolkit can be found here: https://github.com/neuronflow/BraTS-Toolkit-Source

## Contact / Feedback / Questions
Open an issue in this git repository or contact us per email.

Florian Kofler
florian.kofler [at] tum.de

Christoph Berger
c.berger [at] tum.de
