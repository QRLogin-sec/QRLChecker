#!/bin/bash


url=$1

mitmweb -s initialization.py --set url=$url -p 7778 --mode upstream:http://localhost:7890 &
mitmweb_pid=$!


# Press enter after the QRLogin process is done to start detection
python3 qrlogin_process.py $url


kill -9 $mitmweb_pid
