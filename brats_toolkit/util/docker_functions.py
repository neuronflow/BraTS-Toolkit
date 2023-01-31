import shlex
import platform
import pathlib
import subprocess
import os


def start_docker(exam_import_folder=None,
                 exam_export_folder=None, dicom_import_folder=None, nifti_export_folder=None, mode="cpu", gpuid='0'):
    # deal with missing arguments
    if dicom_import_folder is None:
        dicom_import_folder = exam_import_folder
    if nifti_export_folder is None:
        nifti_export_folder = exam_export_folder
    if exam_import_folder is None:
        exam_import_folder = dicom_import_folder
    if exam_export_folder is None:
        exam_export_folder = nifti_export_folder

    # convert to absolute path
    exam_import_folder = os.path.abspath(exam_import_folder)
    exam_export_folder = os.path.abspath(exam_export_folder)
    dicom_import_folder = os.path.abspath(dicom_import_folder)
    nifti_export_folder = os.path.abspath(nifti_export_folder)
    print("exam_import_folder:", exam_import_folder)
    print("dicom_import_folder:", dicom_import_folder)

    print("exam_export_folder:", exam_export_folder)
    print("nifti_export_folder:", nifti_export_folder)

    # make sure directories exist
    os.makedirs(nifti_export_folder, exist_ok=True)
    os.makedirs(exam_export_folder, exist_ok=True)

    # start the right docker
    operatingSystem = platform.system()
    if operatingSystem == "Windows":
        bashscript = os.path.normpath(
            './backend_scripts/win_docker.cmd')
    else:
        if mode == "cpu":
            bashscript = os.path.normpath(
                './backend_scripts/unix_docker.sh')
        elif mode == "robex":
            bashscript = os.path.normpath(
                './backend_scripts/unix_docker.sh')
        elif mode == "gpu":
            bashscript = os.path.normpath(
                './backend_scripts/unix_docker_gpu.sh')
        elif mode == "gpu_hdbet":
            bashscript = os.path.normpath(
                './backend_scripts/unix_docker_gpu.sh')

    # generate subprocess call
    command = [bashscript, "3", dicom_import_folder,
               nifti_export_folder, exam_import_folder, exam_export_folder, gpuid]
    print(*command)

    cwd = pathlib.Path(__file__).resolve().parent
    print(cwd)

    print("starting docker!")
    subprocess.run(command, cwd=cwd)
    print("docker started!")


def stop_docker():
    # stop it
    readableCmd = "docker stop greedy_elephant"
    command = shlex.split(readableCmd)

    cwd = pathlib.Path(__file__).resolve().parent

    print("stopping docker with command:", readableCmd)
    subprocess.run(command, cwd=cwd)
    # remove it
    readableCmd = "docker rm greedy_elephant"
    command = shlex.split(readableCmd)

    cwd = pathlib.Path(__file__).resolve().parent

    print("stopping docker with command:", readableCmd)
    subprocess.run(command, cwd=cwd)


def update_docker():
    readableCmd = "docker pull projectelephant/server"
    print(readableCmd)
    command = shlex.split(readableCmd)

    cwd = pathlib.Path(__file__).resolve().parent

    subprocess.run(command, cwd=cwd)
