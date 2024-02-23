#!/bin/bash
cd /home/jetson/model-listener/
/home/jetson/.nvm/versions/node/v16.20.2/bin/node listen.mjs #--name "model-listener"
#which node
#/home/jetson/.nvm/versions/node/v16.20.2/bin/pm2 start listen.mjs --interpreter=/home/jetson/.nvm/versions/node/v16.20.2/bin/node --name "model-listener"
#echo "Started surely"
#sudo docker run  --volume /home/jetson/model-listener/:/listener/ --entrypoint  /listener/modellisten.sh 0ba9f73feb91

