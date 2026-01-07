import obswebsocket.exceptions
import obsws_python as obs
import websocket
import json
import base64 
import hashlib 
from websocket import WebSocketConnectionClosedException
import builtins as exceptions
from websocket import WebSocket
import obswebsocket
from obswebsocket import requests
import time

class Actuator:


    recording:bool = False
    listening:bool = False
    client=None
    
    #For reference
    doc = 'https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md'

    def __init__(self,host,port,password):
        self.host=host
        self.port=port
        self.password=password
    
    def _auth(self):
            message = self.ws.recv()
            result = json.loads(message)

            if result.get('op') != 0:
                raise exceptions.ConnectionFailure(result.get('error', "Invalid Hello message."))
            self.server_version = result['d'].get('obsWebSocketVersion')

            if result['d'].get('authentication'):
                auth = self._build_auth_string(result['d']['authentication']['salt'], result['d']['authentication']['challenge'])
            else:
                auth = ''

            payload = {
                "op": 1,
                "d": {
                    "rpcVersion": 1,
                    "authentication": auth,
                    "eventSubscriptions": 1023  # EventSubscription::All
                }
            }
            self.ws.send(json.dumps(payload))

            message = self.ws.recv()
            if not message:
                raise exceptions.ConnectionFailure("Empty response to Identify, password may be inconnect.")
            result = json.loads(message)
            if result.get('op') != 2:
                raise exceptions.ConnectionFailure(result.get('error', "Invalid Identified message."))
            if result['d'].get('negotiatedRpcVersion') != 1:
                raise exceptions.ConnectionFailure(result.get('error', "Invalid RPC version negotiated."))


    def _build_auth_string(self, salt, challenge):
            secret = base64.b64encode(
                hashlib.sha256(
                    (self.password + salt).encode('utf-8')
                ).digest()
            )
            auth = base64.b64encode(
                hashlib.sha256(
                    secret + challenge.encode('utf-8')
                ).digest()
            ).decode('utf-8')
            return auth

    def connect(self,host=None,port=None,password=None) -> bool :
        if host==None: host = self.host
        if port==None: port = self.port
        if password==None: password = self.password

        self.client = obswebsocket.obsws(host,port,password)
        try:
            self.client.connect()
        except obswebsocket.exceptions.ConnectionFailure as e:
            print("unable to connect")
            print(e)
            return False
        print("connected")
        return True
    
    def disconnect(self):
        if self.client!=None: 
            self.client.disconnect()

    def record(self):
        
        if(self.listening): self.save_buffer()
        self.client.call(requests.StartRecord())
        print("starting video recording")

    def stopRecord(self):
        print("stopping video recording")
        self.client.call(requests.StopRecord())


    def start_buffer(self):
        self.listening=True
        self.toggle_buffer()
        self.client.call(requests.StartReplayBuffer())
        print("starting buffer")

        
    def toggle_buffer(self):
        
        self.client.call(requests.ToggleReplayBuffer())
        print("toggling buffer")

    def stop_buffer(self):
        print("stopping buffer")
        self.listening=False
        self.client.call(requests.StopReplayBuffer())

    def save_buffer(self):
        
        self.client.call(requests.SaveReplayBuffer())
        print("saving replay buffer")


    def getSettings(self):
        return self.client.call(requests.GetVideoSettings())
    
    


    def updateSettings(self,base_x,base_y,fps,out_x,out_y):
        res = {self.getSettings()}
        if base_x!=None: 
            res['baseWidth'] = base_x
        if base_y!=None: 
            res['baseHeight'] = base_y
        if fps!=None: 
            res['fpsNumerator'] = fps
        if out_x!=None: 
            res['outputWidth'] = out_x
        if out_y!=None: 
            res['outputHeight'] = out_y

        self.client.call(requests.SetVideoSettings(res))
        return self.getSettings()
    
    def getSurces(self):
        return self.client.call(requests.GetSourceActive())

if __name__ == "__main__":
    a = Actuator()
    a.connect()
    print(a.updateSettings(None,None,None,None,None))
    a.toggle_buffer()
    a.start_buffer()
    time.sleep(30)
    print(a.save_buffer())
    a.record()
    time.sleep(2)
    a.stop_buffer()
    time.sleep(5)
    a.stopRecord()
    


    