# Purpose
In Enes100, students have the ability to use Machine Learning on their robots. They can use their WiFiCams to capture an image and evalulate a model. This model is uploaded to the enes100 model uploader that is on the enes100 website. The images + models are evaluated on a Jetson nano that lives near the Vision System computer. This is the code that runs on that jetson, including the code to download the model and the code to connect to the vision system and execute it.

# Instructions
Clone this repository into the home directory when signed in as jetson.

This will install the required libraries for the model downloader.
1. `chmod +x /home/jetson/jetson-ml-client/model-listener/install-listener.sh && /home/jetson/jetson-ml-client/model-listener/install-listener.sh`

This will install the services to that these programs will start on startup.
1. `chmod +x /home/jetson/jetson-ml-client/services/install_services.sh && /home/jetson/jetson-ml-client/services/install_services.sh`


# Useful Commands

`sudo journalctl -u enes100ml.service` to view docker boot service output, incluodng (TODO) VS comm debug outputs    
`sudo journalctl -u mlmodelpull.service` to view model listen / downloader service output.   
`sudo systemctl restart [enes100ml.service | mlmodel.service]` to restart either service.    

# Important Notes

- If adding a python ```print``` to the JetsonWSClient.py, add argument ```flush=True``` in order for print to show up in ```journalctl```.     
    - e.g. ```print('Hello World!', flush=True)```
- Jetson should auto connect to Vision System if Vision System gets reset. Check terminal output to make sure.
