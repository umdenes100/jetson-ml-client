import time
import websocket
import json
import os
import random
import numpy as np
import cv2
import threading
from time import sleep
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn.functional as F
import queue

from utils import preprocess

model_dir = '/nvdli-nano/jetson-ml-client/model-listener/models/'


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class JetsonClient:

    def processor(self):
        """
        This function runs forever, checking the queue and looking for jobs.
        """
        while True:
            # Check the queue
            request = self.task_queue.get(block=True, timeout=None)
            ip = request["ip"]
            team_name = request["team_name"]
            model_index = request["model_index"]
            print(f'Handling message from team {team_name}', flush=True)

            start = time.perf_counter()
            try:
                cap = cv2.VideoCapture('http://' + ip + "/cam.jpg")
                if cap.isOpened():
                    ret, frame = cap.read()
                else:
                    print("failed capture", flush=True)
                    raise Exception("Could not get image from WiFiCam (cv2)")

                try:
                    cv2.imwrite('/nvdli-nano/img_curr.jpg', frame)
                except:
                    print('failed to save image :(', flush=True)

                print('Entering preprocess...', flush=True)
                picture = preprocess(frame)
                results = self.handler(picture, team_name, model_index)
                print('Results: ' + str(results), flush=True)

                self.ws.send(json.dumps({
                    "op": "prediction_results",
                    "teamName": team_name,
                    "prediction": results,
                    "executionTime": time.perf_counter() - start
                }, cls=NpEncoder))
                print('sent :)',flush=True)
            except Exception as e:
                self.ws.send(json.dumps({
                    "op": "prediction_results",
                    "teamName": team_name,
                    "error": str(e)
                }, cls=NpEncoder))

    def on_message(self, _, message):
        print(message, flush=True)
        message = json.loads(message)
        if not message['op'] == 'prediction_request':
            return
        
        ip = message['ESPIP'][0]
        team_name = message['team_name']
        model_index = message["model_index"]
        self.task_queue.put({
            'team_name': team_name,
            'ip': ip,
            'model_index' : model_index
        })
        print(f'queued message from team {team_name}, model index {model_index}', flush=True)

    def on_open(self, _):
        print("Opened!", flush=True)

    def on_error(self, _, error):
        print(error, flush=True)

    # def on_close(self, _):
    #     sleep(5)
    #     self.connect()

    def run(self):
        while True:
            self.ws = websocket.WebSocketApp("ws://192.168.1.2:7756", on_message=self.on_message, on_open=self.on_open, on_error=self.on_error)#, on_close=self.on_close)
            self.ws.run_forever()
            sleep(5)

    def __init__(self):
        self.task_queue = queue.Queue()
        # websocket.enableTrace(True)
        self.model = torchvision.models.resnet18(pretrained=True)

        print('Running 5 images - dummy data on startup...', flush=True)
        dummy_data_dir = '/nvdli-nano/jetson-ml-client/dummy_data/'
        for i in range(5):
            random_image_path = random.choice(os.listdir(dummy_data_dir))
            print(f'Random image: {random_image_path}', flush=True)
            random_image = preprocess(cv2.imread(dummy_data_dir+random_image_path))
            self.handler(random_image, 'STARTUP_alextest')
        threading.Thread(name='task queue handler', args=(), target=self.processor).start()
        self.run()
        
    def handler(self, image, team_name, model_index):
        model_fi = None
        if not team_name == 'STARTUP_alextest':
            for entry in os.scandir(model_dir):
                if entry.name.startswith(team_name) and int(entry.name.split('_')[1]) == model_index:
                    model_fi = entry.name
                    break

            if model_fi is None:
                print("model file not found", flush=True)
                raise Exception(f"Cound not find model for team: {team_name} with model index: {model_index} 
                                \n Available models: {', '.join([entry.name for entry in os.scandir(model_dir)])}")
                
            num_str = model_fi.split('_')[-1] # get last segment "#.pth"
            num_str = os.path.splitext(num_str)[0] # get rid of ".pth"
            dim = int(num_str)
        else:
            dim = 3
            
        self.model.fc = torch.nn.Linear(512, dim)
        self.model = self.model.to(torch.device('cuda'))

        if team_name == 'STARTUP_alextest':
            self.model.load_state_dict(torch.load('/nvdli-nano/jetson-ml-client/dummy_data/alextest_3.pth'))
        else:
            self.model.load_state_dict(torch.load(model_dir + model_fi))

        self.model.eval()
        output = self.model(image)
        output = F.softmax(output, dim=1).detach().cpu().numpy().flatten()

        return output.argmax()


print('Imports finished. Starting websocket.', flush=True)
client = JetsonClient()
