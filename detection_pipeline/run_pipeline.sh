#!/bin/bash


url=$1

mitmweb -s analyzer.py --set url=$url -p 7778 --mode upstream:http://localhost:7890 &
mitmweb_pid=$!

python3 qrcode_handler.py $url

kill -9 $mitmweb_pid
