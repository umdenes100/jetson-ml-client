#!/bin/bash
#cd ~/model-listener/
#pm2 start listen.mjs --name "model-listener"
#cd ~
#./dockerautoboot.sh
sudo docker run --entrypoint /nvdli-nano/jetson-ml-client/client_handler/startup.sh --dns=192.168.1.1 --runtime nvidia --network host  --volume /home/jetson/:/nvdli-nano/ nvcr.io/nvidia/dli/dli-nano-ai:v2.0.2-r32.7.1

