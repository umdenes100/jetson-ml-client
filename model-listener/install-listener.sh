# Run this script by calling wget -qO- https://raw.githubusercontent.com/ForrestFire0/enes100-ml-client/master/install-listener.sh | bash
# RUN IT IN THE ROOT DIRECTORY
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
source ~/.bashrc
nvm install 16
npm init
npm install firebase
npm install node-fetch
sudo cp /home/jetson/jetson-ml-client/services/* /etc/systemd/system/
sudo cp /home/jetson/jetson-ml-client/service_scripts/* /usr/bin/
