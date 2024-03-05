# Instructions

1. `chmod +x /home/jetson/jetson-ml-client/services/install_services.sh && /home/jetson/jetson-ml-client/services/install_services.sh`
2. `chmod +x /home/jetson/jetson-ml-client/model-listener/install-listener.sh && /home/jetson/jetson-ml-client/model-listener/install-listener.sh`

# Useful Commands

`sudo journalctl -u enes100ml.service` to view docker boot service output, incluodng (TODO) VS comm debug outputs    
`sudo journalctl -u mlmodelpull.service` to view model listen / downloader service output.   
`sudo systemctl restart [enes100ml.service | mlmodel.service]` to restart either service.    

# Important Notes

- If adding a python ```print``` to the JetsonWSClient.py, add argument ```flush=True``` in order for print to show up in ```journalctl```.     
    - e.g. ```print('Hello World!', flush=True)```
- Jetson should auto connect to Vision System if Vision System gets reset. Check terminal output to make sure.
