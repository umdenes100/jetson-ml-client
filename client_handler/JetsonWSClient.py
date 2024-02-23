import websocket
import json
import os
import PIL.Image
import numpy as np
import io
import cv2
from time import sleep
import torch
import torchvision
import torch.nn.functional as F
#import rel

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
from utils import preprocess

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()

class JetsonClient:
    def on_message(self, _, message):
        print(message)
        message = json.loads(message)
        if not message['op'] == 'prediction_request':
            return
        
        IP = message['ESPIP'][0]
        team_name = message['team_name']
        try:
            print(IP)
            print(team_name)
            cap = cv2.VideoCapture('http://' + IP + ":81/stream")
            if cap.isOpened():
                print("captured")
                ret, frame = cap.read()
            else:
                print("failed capture")
                raise Exception("Could not get image from WiFiCam (cv2)")
            
            try:
                cv2.imwrite('imcurr.jpg', frame)
            except:
                print('failed to save image :(')
            
            print('entering preprocess...')
            picture = preprocess(frame)
            results = self.handler(picture, team_name)
            print(results)
            print('sending')
            self.ws.send(json.dumps({
                "op": "prediction_results",
                "teamName": team_name,
                "prediction": results
            }, cls=NpEncoder))
            print('sent :)')
        except Exception as e:
             self.ws.send(json.dumps({
                "op": "prediction_results",
                "teamName": team_name,
                "error": str(e)
            }, cls=NpEncoder))

    def on_open(self, _):
        print("Opened!")

    def on_error(self, _, error):
        print(error)

    # def on_close(self, _):
    #     sleep(5)
    #     self.connect()

    def run(self):
        while True:
            self.ws = websocket.WebSocketApp("ws://192.168.1.2:7756", on_message=self.on_message, on_open=self.on_open, on_error=self.on_error)#, on_close=self.on_close)
            self.ws.run_forever() # can we do this?
            sleep(5)

    def __init__(self):
        # websocket.enableTrace(True)
        self.run()
        
    def handler(self, image, team_name):
        
        model_fi = None
        for entry in os.scandir('/model-listener/models/'):
            if entry.name.startswith(team_name):
                model_fi = entry.name
                break
        if model_fi is None:
            print("model file not found")
            raise Exception(f"Cound not find model for team: {team_name} \n Available models: {', '.join([entry.name for entry in os.scandir('/model-listener/models/')])}")
        
        num_str = model_fi.split('_')[-1]
        num_str = os.path.splitext(num_str)[0]
        print(num_str)
        dim = int(num_str)
        
        # TODO figure out what of these can be declared outisde of the handler possibly
        device = torch.device('cuda')
        model = torchvision.models.resnet18(pretrained=True)
        model.fc = torch.nn.Linear(512, dim)
        model = model.to(device)
        model.load_state_dict(torch.load('/model-listener/models/' + model_fi))
        model.eval()
        output = model(image)
        output = F.softmax(output, dim=1).detach().cpu().numpy().flatten()
        for i, score in enumerate(list(output)):
            print(str(i) + " " + str(score))
        return output.argmax()


client = JetsonClient()
