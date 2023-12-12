import os
import sys
import tempfile
from pathlib import Path

import socketio

from brats_toolkit.util.citation_reminder import (
    citation_reminder,
    deprecated_preprocessor,
)
from brats_toolkit.util.docker_functions import start_docker, stop_docker, update_docker
from brats_toolkit.util.prep_utils import tempFiler


class Preprocessor:
    """
    Class for preprocessing medical imaging data.
    """

    @citation_reminder
    @deprecated_preprocessor
    def __init__(self, noDocker: bool = False):
        """
        Initialize the Preprocessor instance.

        Parameters:
        - noDocker (bool): Flag indicating whether Docker is used.
        """
        # settings
        self.clientVersion: str = "0.0.1"
        self.confirmationRequired: bool = True
        self.mode: str = "cpu"
        self.gpuid: str = "0"

        # init sio client
        self.sio: socketio.Client = socketio.Client()

        # set docker usage
        self.noDocker: bool = noDocker

        @self.sio.event
        def connect() -> None:
            """
            Event handler for successful connection.
            """
            print("connection established! sid:", self.sio.sid)
            self.sio.emit(
                "clientidentification",
                {"brats_cli": self.clientVersion, "proc_mode": self.mode},
            )

        @self.sio.event
        def connect_error() -> None:
            """
            Event handler for connection error.
            """
            print("The connection failed!")

        @self.sio.event
        def disconnect() -> None:
            """
            Event handler for disconnection.
            """
            print("disconnected from server")

        @self.sio.on("message")
        def message(data: dict) -> None:
            """
            Event handler for incoming message.
            """
            print("message", data)

        @self.sio.on("status")
        def on_status(data: dict) -> None:
            """
            Event handler for status update.
            """
            print("status received: ", data)
            if data["message"] == "client ID json generation finished!":
                self._inspect_input()
            elif data["message"] == "input inspection finished!":
                if "data" in data:
                    print("input inspection found the following exams: ", data["data"])
                    if self.confirmationRequired:
                        confirmation = input(
                            'press "y" to continue or "n" to scan the input folder again.'
                        ).lower()
                    else:
                        confirmation = "y"

                    if confirmation == "n":
                        self._inspect_input()

                    if confirmation == "y":
                        self._process_start()

            elif data["message"] == "image processing successfully completed.":
                self.sio.disconnect()
                stop_docker()
                sys.exit(0)

        @self.sio.on("client_outdated")
        def outdated(data: dict) -> None:
            """
            Event handler for outdated client version.
            """
            print(
                "Your client version",
                self.clientVersion,
                "is outdated. Please download version",
                data,
                "from:",
            )
            print("https://neuronflow.github.io/brats-preprocessor/")
            self.sio.disconnect()
            stop_docker()
            sys.exit(0)

        @self.sio.on("ipstatus")
        def on_ipstatus(data: dict) -> None:
            """
            Event handler for image processing status.
            """
            print("image processing status received:")
            print(data["examid"], ": ", data["ipstatus"])

    def single_preprocess(
        self,
        t1File: str,
        t1cFile: str,
        t2File: str,
        flaFile: str,
        outputFolder: str,
        mode: str,
        confirm: bool = False,
        skipUpdate: bool = False,
        gpuid: str = "0",
    ) -> None:
        """
        Process a single set of input files.

        Parameters:
        - t1File (str): Path to T1 file.
        - t1cFile (str): Path to T1c file.
        - t2File (str): Path to T2 file.
        - flaFile (str): Path to FLAIR file.
        - outputFolder (str): Output folder path.
        - mode (str): Processing mode (e.g., "cpu", "gpu").
        - confirm (bool): Whether confirmation is required.
        - skipUpdate (bool): Whether to skip Docker update.
        - gpuid (str): GPU ID.

        Returns:
        - None
        """
        # assign name to file
        print("basename:", os.path.basename(outputFolder))
        outputPath: Path = Path(outputFolder)
        dockerOutputFolder: str = os.path.abspath(outputPath.parent)

        # create temp dir
        storage: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
        # TODO this is a potential security hazzard as all users can access the files now, but currently it seems the only way to deal with bad configured docker installations
        os.chmod(storage.name, 0o777)
        dockerFolder: str = os.path.abspath(storage.name)
        tempFolder: str = os.path.join(dockerFolder, os.path.basename(outputFolder))

        os.makedirs(tempFolder, exist_ok=True)
        print("tempFold:", tempFolder)

        # create temp Files
        tempFiler(t1File, "t1", tempFolder)
        tempFiler(t1cFile, "t1c", tempFolder)
        tempFiler(t2File, "t2", tempFolder)
        tempFiler(flaFile, "fla", tempFolder)

        self.batch_preprocess(
            exam_import_folder=dockerFolder,
            exam_export_folder=dockerOutputFolder,
            mode=mode,
            confirm=confirm,
            skipUpdate=skipUpdate,
            gpuid=gpuid,
        )

    def batch_preprocess(
        self,
        exam_import_folder: str,
        exam_export_folder: str,
        dicom_import_folder: str = None,
        nifti_export_folder: str = None,
        mode: str = "cpu",
        confirm: bool = True,
        skipUpdate: bool = False,
        gpuid: str = "0",
    ) -> None:
        """
        Process multiple sets of input files, potentially using Docker.

        Parameters:
        - exam_import_folder (str): Import folder path.
        - exam_export_folder (str): Export folder path.
        - dicom_import_folder (Optional[str]): DICOM import folder path.
        - nifti_export_folder (Optional[str]): NIfTI export folder path.
        - mode (str): Processing mode (e.g., "cpu", "gpu").
        - confirm (bool): Whether confirmation is required.
        - skipUpdate (bool): Whether to skip Docker update.
        - gpuid (str): GPU ID.

        Returns:
        - None
        """
        if confirm != True:
            self.confirmationRequired = False
        self.mode = mode
        self.gpuid = gpuid

        if self.noDocker != True:
            stop_docker()
            if skipUpdate != True:
                update_docker()
            start_docker(
                exam_import_folder=exam_import_folder,
                exam_export_folder=exam_export_folder,
                dicom_import_folder=dicom_import_folder,
                nifti_export_folder=nifti_export_folder,
                mode=self.mode,
                gpuid=self.gpuid,
            )

        # setup connection
        # TODO do this in a more elegant way and somehow check whether docker is up and running before connect
        self.sio.sleep(8)  # wait 8 secs for docker to start
        self._connect_client()
        self.sio.wait()

    def _connect_client(self) -> None:
        """
        Connect to the server using SocketIO.
        """
        self.sio.connect("http://localhost:5000")
        print("sid:", self.sio.sid)

    def _inspect_input(self) -> None:
        """
        Send input inspection request to the server.
        """
        print("sending input inspection request!")
        self.sio.emit("input_inspection", {"hurray": "yes"})

    def _process_start(self) -> None:
        """
        Send processing request to the server.
        """
        print("sending processing request!")
        self.sio.emit("brats_processing", {"hurray": "yes"})
