import socketio
from brats_toolkit.util.docker_functions import start_docker, stop_docker, update_docker
import os
import tempfile
from pathlib import Path

from brats_toolkit.util.prep_utils import tempFiler
import sys


class Preprocessor(object):
    def __init__(self, noDocker=False):
        # settings
        self.clientVersion = "0.0.1"
        self.confirmationRequired = True
        self.mode = "cpu"
        self.gpuid = "0"

        # init sio client
        self.sio = socketio.Client()

        # set docker usage
        self.noDocker = noDocker

        @self.sio.event
        def connect():
            print("connection established! sid:", self.sio.sid)
            # client identification
            self.sio.emit("clientidentification", {
                "brats_cli": self.clientVersion, "proc_mode": self.mode})

        @self.sio.event
        def connect_error():
            print("The connection failed!")

        @self.sio.event
        def disconnect():
            print('disconnected from server')

        @self.sio.on('message')
        def message(data):
            print('message', data)

        @self.sio.on('status')
        def on_status(data):
            print('status reveived: ', data)
            if data['message'] == "client ID json generation finished!":
                self.inspect_input()
            elif data['message'] == "input inspection finished!":
                if "data" in data:
                    print("input inspection found the following exams: ",
                          data['data'])
                    if self.confirmationRequired:
                        confirmation = input(
                            "press \"y\" to continue or \"n\" to scan the input folder again.").lower()
                    else:
                        confirmation = "y"

                    if confirmation == "n":
                        self.inspect_input()

                    if confirmation == "y":
                        self.process_start()

            elif data['message'] == "image processing successfully completed.":
                self.sio.disconnect()
                stop_docker()
                sys.exit(0)

        @self.sio.on('client_outdated')
        def outdated(data):
            print("Your client version", self.clientVersion, "is outdated. Please download version", data,
                  "from:")
            print("https://neuronflow.github.io/brats-preprocessor/")
            self.sio.disconnect()
            stop_docker()
            sys.exit(0)

        @self.sio.on('ipstatus')
        def on_ipstatus(data):
            print("image processing status reveived:")
            print(data['examid'], ": ", data['ipstatus'])

    def single_preprocess(self, t1File, t1cFile, t2File, flaFile, outputFolder, mode, confirm=False, skipUpdate=False, gpuid='0'):
        # assign name to file
        print("basename:", os.path.basename(outputFolder))
        outputPath = Path(outputFolder)
        dockerOutputFolder = os.path.abspath(outputPath.parent)

        # create temp dir
        storage = tempfile.TemporaryDirectory()
        # TODO this is a potential security hazzard as all users can access the files now, but currently it seems the only way to deal with bad configured docker installations
        os.chmod(storage.name, 0o777)
        dockerFolder = os.path.abspath(storage.name)
        tempFolder = os.path.join(dockerFolder, os.path.basename(outputFolder))

        os.makedirs(tempFolder, exist_ok=True)
        print("tempFold:", tempFolder)

        # create temp Files
        tempFiler(t1File, "t1", tempFolder)
        tempFiler(t1cFile, "t1c", tempFolder)
        tempFiler(t2File, "t2", tempFolder)
        tempFiler(flaFile, "fla", tempFolder)

        self.batch_preprocess(exam_import_folder=dockerFolder, exam_export_folder=dockerOutputFolder, mode=mode,
                              confirm=confirm, skipUpdate=skipUpdate, gpuid=gpuid)

    def batch_preprocess(self, exam_import_folder=None, exam_export_folder=None, dicom_import_folder=None,
                         nifti_export_folder=None,
                         mode="cpu", confirm=True, skipUpdate=False, gpuid='0'):
        if confirm != True:
            self.confirmationRequired = False
        self.mode = mode
        self.gpuid = gpuid

        if self.noDocker != True:
            stop_docker()
            if skipUpdate != True:
                update_docker()
            start_docker(exam_import_folder=exam_import_folder, exam_export_folder=exam_export_folder,
                         dicom_import_folder=dicom_import_folder, nifti_export_folder=nifti_export_folder, mode=self.mode, gpuid=self.gpuid)

        # setup connection
        # TODO do this in a more elegant way and somehow check whether docker is up and running before connect
        self.sio.sleep(5)  # wait 5 secs for docker to start
        self.connect_client()
        self.sio.wait()

    def connect_client(self):
        self.sio.connect('http://localhost:5000')
        print('sid:', self.sio.sid)

    def inspect_input(self):
        print("sending input inspection request!")
        self.sio.emit("input_inspection", {'hurray': 'yes'})

    def process_start(self):
        print("sending processing request!")
        self.sio.emit("brats_processing", {'hurray': 'yes'})
