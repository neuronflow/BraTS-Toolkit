#!/usr/bin/env bash
# check if parameter is present
if [ $# -eq 0 ]; then
  echo "You must enter the number of desired workers and 5 paths!, e.g. docker_run.sh 2 /setting /dicom_import /nifti_export /exam_import /exam_export"
  exit 1
fi

docker stop greedy_elephant
# TODO set gpu
docker run --rm -d --name=greedy_elephant --gpus device=$6 -p 5000:5000 -p 9181:9181 -v "$2":"/data/import/dicom_import" -v "$3":"/data/export/nifti_export" -v "$4":"/data/import/exam_import" -v "$5":"/data/export/exam_export" projectelephant/server redis-server
#wait until everything is started up
sleep 10
#start x-server for non-gui gui
docker exec -d greedy_elephant /bin/bash -c "source ~/.bashrc; Xorg -noreset +extension GLX +extension RANDR +extension RENDER -logfile ./etc/10.log -config ./etc/X11/xorg.conf :0;"
docker exec -d greedy_elephant python3 elephant_server.py
docker exec -d greedy_elephant /bin/bash -c "source ~/.bashrc; rq-dashboard;"
#ugly format to set correct path variable every time! (as .bashrc doesn't want to work)
docker exec -d greedy_elephant /bin/bash -c "source ~/.bashrc; ./start_workers.sh;"

# TODO fix user thing, also need to add user on exec
# userid=$(id -u)
# usergroup=$(id -g)
# echo $userid:$usergroup
# --user $userid:$usergroup
