from flask import Flask
#used to create instances of a web application
import socketio
import eventlet
import base64
import numpy as np
import keras
from keras.models import load_model
from io import BytesIO
from PIL import Image
import cv2

sio = socketio.Server()

@sio.on('telemetry')

def img_preprocess(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img,  (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img/255
    return img

def telemetry(sid, data):
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    send_control(steering_angle, 1.0)

model = load_model('model.h5')

app = Flask(__name__) #'main'

@sio.on('connect')
def connect(sid, environ):
    print('connected')
    send_control(0,0)

def send_control(steering_angle, throttle):
    sio.emit('steer', data ={
    'steering_angle': steering_angle.__str__(),
    'throttle': throttle.__str__()
    })
if __name__ == '__main__':
    app = socketio.Middleware(sio,app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
