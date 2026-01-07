from tkinter import *
from tkinter import ttk,filedialog
from tkinter.simpledialog import askstring
import Core
import GUI
import yaml
import pyglet
from threading import Thread


class GUI:

    core:Core= None
    started=False
    status = False
    top = None
    frame = None
    frame1=None
    settings=None
    settings_frame=None
    settings_sizegrip=None
    host= None
    password = None
    port = None
    
    def __init__(self,core:Core,name) -> None:
        self.core=core
        self.name=name
        pyglet.font.add_file('./data/Retro Gaming.ttf')

    def refresh(self):
        self.frame1.destroy()
        self.frame.destroy()
        self.start(True)


    def send_start(self):
        self.started=True
        self.core.start_recorder()
        self.refresh()

        
    def send_stop(self):
        self.started=False
        self.core.stop_recorder()
        self.refresh()

    


    def update_status(self,status):
        self.status=status


    def get_params(self):
        self.host=self.core.params['host']
        self.password=self.core.params['password']
        self.port=self.core.params['port']


    
    def update_name(self,event):
        
        self.varItems.set(self.varItems.get().strip())
        self.name = self.varItems.get().strip()
        print("updating name to "+ self.name)
        self.core.name=self.name

    def update_settings(self):
        print("updating settings to "+self.host+" "+str(self.port)+" "+self.password)
        self.core.new_params['host']=self.host
        self.core.new_params['port']=self.port
        self.core.new_params['password']=self.password
        self.settings_frame.destroy()
        self.settings_sizegrip.destroy()
        self.settings.destroy()
        self.settings=None
        self.display_settings(True)
        
        

    



    def display_settings(self,saved:bool=False):

    

        self.get_params()
        
  

        self.settings = Tk()
        self.settings.geometry("600x350")
        self.settings.title("settings")
        self.settings.configure(background="Black")
        

        varItems = StringVar(self.settings, value=self.name)
        
        

        self.settings_frame = Frame(self.settings,highlightthickness=0)
        self.settings_frame.pack()

        
        string_variable = StringVar(self.settings_frame, "HOST:")
        string_variable1 = StringVar(self.settings_frame, "PORT:")
        string_variable2 = StringVar(self.settings_frame, "PASSWORD:")
        
        label = Label(self.settings_frame,bg="Black",foreground="White", textvariable=string_variable, font=('Retro Gaming',12))
        label.pack(anchor=NW)
        inputtxt = Text(self.settings_frame,font=('Retro Gaming',12),highlightcolor="White", height = 1, width = 50,highlightthickness=2) 
        label1 = Label(self.settings_frame,bg="Black",foreground="White", textvariable=string_variable1, font=('Retro Gaming',12))
        inputtxt1 = Text(self.settings_frame,font=('Retro Gaming',12),highlightcolor="White", height = 1, width = 50,highlightthickness=2) 
        label2 = Label(self.settings_frame,bg="Black",foreground="White", textvariable=string_variable2, font=('Retro Gaming',12))
        inputtxt2 = Text(self.settings_frame,font=('Retro Gaming',12),highlightcolor="White", height = 1, width = 50,highlightthickness=2) 
        
        inputtxt.insert("1.0",self.host)
        inputtxt1.insert("1.0",self.port)
        inputtxt2.insert("1.0",self.password)

        inputtxt.configure(background="Black",foreground="White") 
        typed_text=[]
        inputtxt.bind("<KeyPress>", lambda _: self.updateHost(_))
        inputtxt.pack()
        label1.pack(anchor=NW)

        inputtxt1.configure(background="Black",foreground="White")
        typed_text1=[]
        inputtxt1.bind("<KeyPress>", lambda _: self.updatePort(_))
        inputtxt1.pack() 
        label2.pack(anchor=NW)

        inputtxt2.configure(background="Black",foreground="White")
        typed_text2=[]
        inputtxt2.bind("<KeyPress>", lambda _: self.updatePwd(_))
        inputtxt2.pack() 


        
    
        B = Button(self.settings_frame,highlightthickness=0,highlightcolor="Black",text ="Save",font=('Retro Gaming',25), command = self.update_settings)
        B.configure(background="Yellow")
       
        B.pack(anchor=S,pady=10)

        
        string_variable_end = StringVar(self.settings_frame, "start the agent to update the settings")
            
        label = Label(self.settings_frame,bg="Black",foreground="Red", textvariable=string_variable_end, font=('Retro Gaming',8))

        if(saved): label.pack(anchor=S)
        

        
        self.settings_sizegrip = ttk.Sizegrip(self.settings)
        self.settings_sizegrip.pack( anchor = SE)
        
        self.settings_frame.configure(background="Black")
        
        self.settings_frame.pack(padx = 10, pady = 10, expand = True, fill = BOTH)
        

    def start(self,refresh=False):
        if self.top==None:
            self.top = Tk()
            self.top.geometry("200x185")
            self.top.title("Reactive OBS")
            self.top.configure(background="Black")
        else:
            self.sizegrip.destroy()

        self.varItems = StringVar(self.top, value=self.name)
        
        

        self.frame = Frame(self.top,highlightthickness=0)


        self.frame1=Frame(self.top,highlightthickness=0)
        self.frame1.configure(background="Black")
        

        set = Button(self.frame1,highlightthickness=0,highlightcolor="Black",text ="settings",font=('Retro Gaming',8), command = self.display_settings)
        set.configure(background="Grey")
        

        myCanvas = Canvas(self.frame1)
        myCanvas.config(width=15, height=15,background="Black",borderwidth=0)
        if self.status: myCanvas.create_oval(5, 5, 10, 10, fill="green")
        else: myCanvas.create_oval(5, 5, 10, 10, fill="red")
        
        set.pack(side=RIGHT,anchor=NE,padx=8,pady=8)
        myCanvas.pack(side=LEFT,anchor=NW,padx=8,pady=8)
        self.frame1.pack(fill=X)

        names = ["Rob", "Mike", "Eva",
        "Annah"]
        
        Combo = ttk.Combobox(self.frame, values = names, textvariable=self.varItems)
        Combo.configure(background="Black")
        Combo.configure(foreground="Black")
        Combo.set(self.name)
        Combo.bind("<Return>", self.update_name)
        Combo.bind('<<ComboboxSelected>>',self.update_name)
        Combo.pack(padx = 5,pady = 8)
        
    
        if not self.started: 
            B = Button(self.frame,highlightthickness=0,highlightcolor="Black",text ="Start",font=('Retro Gaming',25), command = self.send_start)
            B.configure(background="Green")
        else:
            B = Button(self.frame,highlightthickness=0,highlightcolor="Black",text ="Stop",font=('Retro Gaming',25), command = self.send_stop)
            B.configure(background="Red")
        B.pack(anchor=S,pady = 5)
        self.sizegrip = ttk.Sizegrip(self.top)
        
        
        self.frame.configure(background="Black")
        
        self.frame.pack( expand = True, fill = BOTH)
        self.sizegrip.pack( anchor = SE)

        

        # Code to add widgets will go here...
        if(not refresh): self.top.mainloop()
        
    def updateHost(self,event):
        if event.char=="\x08":
            if len(self.host)>=1:
                self.host=self.host[:-1]
        else: self.host+=event.char

    def updatePort(self,event):
        if event.char=="\x08":
            if len(str(self.port))>=1:
                self.port=int(str(self.port)[:-1])
        else: self.port=int(str(self.port)+event.char)
        print(str(self.port))

    def updatePwd(self,event):
        if event.char=="\x08":
            if len(self.password)>=1:
                self.password=self.password[:-1]
        else:self.password+=event.char