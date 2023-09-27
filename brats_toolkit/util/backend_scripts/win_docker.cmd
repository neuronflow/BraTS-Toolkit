SETLOCAL ENABLEEXTENSIONS
SET me=%~n0
SET parent=%~dp0
REM get container ID and stop it (rm is automatic)
docker stop greedy_elephant
docker run --rm -d --name=greedy_elephant -p 5000:5000 -p 9181:9181 -v %2:"/data/import/dicom_import" -v %3:"/data/export/nifti_export" -v %4:"/data/import/exam_import" -v %5:"/data/export/exam_export" projectelephant/server redis-server
docker exec -d greedy_elephant /bin/bash -c "source ~/.bashrc; Xorg -noreset +extension GLX +extension RANDR +extension RENDER -logfile ./etc/10.log -config ./etc/X11/xorg.conf :0;"
docker exec -d greedy_elephant python3 elephant_server.py
docker exec -d greedy_elephant /bin/bash -c "source ~/.bashrc; rq-dashboard;"
docker exec -d greedy_elephant /bin/bash -c "source ~/.bashrc; ./start_workers.sh;"
@REM del temp.txt
