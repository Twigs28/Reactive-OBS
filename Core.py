from difflib import SequenceMatcher

from obswebsocket import requests
from Actuator import Actuator
import yaml
import Listener
import GUI
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread


class Core:
    res_x = None
    res_y = None
    host = None
    port = None
    password=None
    rec=None
    act=None
    gui=None
    params=None
    new_params=None
    status=True
    p:Thread=None
    #COMMANDS
    listen=['start listening','listen', 'start the replay buffer']
    stop_listen=['stop listening','stop the replay buffer']
    record=['start recording','start video recording']
    stop_record=['stop recording','stop video recording']
    resolution=['set the resolution to','resolution to ']
    fps = ['set the fps to','set the framerate to']
    save = ['save the replay', 'save replay']

    name = 'rob'
    name_orig='rob'
    alternative_activation = 'hello robert'


    def __init__(self) -> None:
        self.read_params()
        self.rec=Listener.Recorder(self)
        self.act = Actuator(self.host,self.port,self.password)
        self.gui = GUI.GUI(self,self.name) 
        self.gui.start()
        self.status=self.gui.status


    def read_activation(self,command:str):
        if(self.name!=self.name_orig):
            self.update_name(self.name)
        self.activation = 'hello '+self.name
        print(command)
        command=command.lower()

        words = command.split(" ")
        for x in range(len(words)-1):
            if SequenceMatcher(None,words[x],"hello").ratio()>0.85:
                if SequenceMatcher(None,words[x]+' '+words[x+1],self.activation).ratio()>0.8 or SequenceMatcher(None,words[x]+' '+words[x+1],self.alternative_activation).ratio()>0.95:
                    new_command = ''
                    for y in range(x+2,x+10):
                        if y<len(words):
                            new_command+=" "+words[y]
                    self.read_command(new_command)
    
    def read_command(self,command:str):
        command=command.lower()


        words = command.split(" ")

        if self.understand_save(words): print("saving replay buffer")
        elif self.understand_record(words): print("recording status updated")
        elif self.understand_listen(words): print("listening status updated")


    
    def understand_save(self, words:list):
        for cmd in self.save:
            for x in range(len(words)):
                potential = ""
                for length in range(len(cmd.split(" "))):
                    if x+length<len(words):
                        potential+=words[x+length]+" "
                if SequenceMatcher(None,potential,cmd).ratio()>0.85:
                    print("match found: "+cmd)
                    print(self.save_buffer())
                    return True
        return False
    
    def understand_listen(self, words:list):
        a=0
        b=0
        for cmd in self.listen:
            for x in range(len(words)):
                potential = ""
                for length in range(len(cmd.split(" "))):
                    if x+length<len(words):
                        potential+=words[x+length]+" "
                value_pos = SequenceMatcher(None,potential,cmd).ratio()
                if value_pos>0.85:
                    print("potential match found: "+cmd+" "+str(value_pos))
                    if value_pos>a: a=value_pos
        for cmd in self.stop_listen:
            for x in range(len(words)):
                potential = ""
                for length in range(len(cmd.split(" "))):
                    if x+length<len(words):
                        potential+=words[x+length]+" "
                value_pos = SequenceMatcher(None,potential,cmd).ratio()
                if value_pos>0.85:
                    print("potential match found: "+cmd+" "+str(value_pos))
                    if value_pos>b: b=value_pos
        if(a>b and a!=0):
            print(self.start_listening())
            return True
        if(a<b and b!=0):
            print(self.stop_listening())
            return True
        return False
    
    def understand_record(self, words:list):
        a=0
        b=0
        for cmd in self.record:
            for x in range(len(words)):
                potential = ""
                for length in range(len(cmd.split(" "))):
                    if x+length<len(words):
                        potential+=words[x+length]+" "
                value_pos = SequenceMatcher(None,potential,cmd).ratio()
                if value_pos>0.85:
                    print("potential match found: "+cmd+" "+str(value_pos))
                    if value_pos>a: a=value_pos
        for cmd in self.stop_record:
            for x in range(len(words)):
                potential = ""
                for length in range(len(cmd.split(" "))):
                    if x+length<len(words):
                        potential+=words[x+length]+" "
                value_pos = SequenceMatcher(None,potential,cmd).ratio()
                if value_pos>0.85:
                    print("potential match found: "+cmd+" "+str(value_pos))
                    if value_pos>b: b=value_pos
        if(a>b and a!=0):
            print(self.start_recording())
            return True
        if(a<b and b!=0):
            print(self.stop_recording())
            return True
        return False
                    

    def start_recording(self):
        try:
            self.act.record()
            song = AudioSegment.from_wav("./data/start.wav")
            play(song)
            self.gui.update_status(True)
            self.gui.refresh()
            return True
        except Exception:
            song = AudioSegment.from_wav("./data/error.wav")
            play(song)
         
    
    def stop_recording(self):
        try:
            self.act.stopRecord()
            song = AudioSegment.from_wav("./data/stop.wav")
            play(song)
            self.gui.update_status(False)
            self.gui.refresh()
            return True
        except Exception:
            song = AudioSegment.from_wav("./data/error.wav")
            play(song)

        
    
    def start_listening(self):
        try:
            self.act.start_buffer()
            song = AudioSegment.from_wav("./data/listen.wav")
            play(song)
            return True
        except Exception:
            song = AudioSegment.from_wav("./data/error.wav")
            play(song)
        
    
    def stop_listening(self):
        try:
            self.act.stop_buffer()
            song = AudioSegment.from_wav("./data/stop_listening.wav")
            play(song)
            self.gui.update_status(False)
            return True
        except Exception:
            song = AudioSegment.from_wav("./data/error.wav")
            play(song)
            
    
    def save_buffer(self):
        try:
            self.act.save_buffer()
            song = AudioSegment.from_wav("./data/save.wav")
            play(song)
            return True
        except Exception:
            song = AudioSegment.from_wav("./data/error.wav")
            play(song)
        
    
    def update_settings(self,command:str):
        return self.act.updateSettings()
    
    def read_params(self):
        # Read YAML file
        with open("./config.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            self.password=data_loaded['password']
            self.host=data_loaded['host']
            self.port=data_loaded['port']
            self.name=data_loaded['name']
            self.name_orig=data_loaded['name']
        self.params=data_loaded
        self.new_params=data_loaded.copy()
        return data_loaded

    
    def start_recorder(self):
        for x in self.new_params:
            if self.new_params[x]!=self.params[x]:
                print("change detected")
                self.update_params(self.new_params)
        print("started")
        self.act.disconnect()
        self.act.connect(self.host,self.port,self.password)
        p = Thread(target = self.rec.listen)
        p.setDaemon(True)
        p.start()
        


    def stop_recorder(self):
        self.status=False
        self.gui.status=False
        print("stopped")
        self.gui.refresh()

    def getStatus(self):
        return self.status
    
    def update_name(self,name):
        print("updating name")
        data=self.params
        data['name']=name
        with open('./config.yaml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
        self.name=name
        self.name_orig=self.name
        return self.name
    
    def update_params(self,params):
        print("updating parameters")
        with open('./config.yaml', 'w') as outfile:
            yaml.dump(params, outfile, default_flow_style=False)
        self.params=params.copy()
        self.host=self.params['host']
        self.port=self.params['port']
        self.password=self.params['password']
        self.act.host=self.params['host']
        self.act.port=self.params['port']
        self.act.password=self.params['password']
        return self.name
    




if __name__=="__main__":
    c = Core()

