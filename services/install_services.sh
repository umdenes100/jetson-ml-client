sudo systemctl enable enes100ml.service
sudo systemctl enable mlmodelpull.service
sudo systemctl start enes100ml.service
sudo systemctl start mlmodelpull.service
sudo cp /home/jetson/jetson-ml-client/services/* /etc/systemd/system/
sudo cp /home/jetson/jetson-ml-client/service_scripts/* /usr/bin/
