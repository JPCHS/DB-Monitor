import pygame
import pyaudio
import numpy as np
import win32con
import win32gui
import win32process
from win32api import GetMonitorInfo, MonitorFromPoint
from pystray import MenuItem, Menu,Icon
from PIL import Image,ImageTk,ImageSequence
import tkinter as tk
import sys
import os
import threading
import psutil
import json
import time
import random
import argparse
import socketserver
import socket
class server(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        if data==b"Show":
            menu.show_window()
        self.request.sendall(b"Exit")
class MultiThreadTcpServer(socketserver.ThreadingMixIn,socketserver.TCPServer):
    pass
class dir:
    def __init__(self):
        self.current_dir=os.path.abspath(sys.argv[0])
        self.current_dir=self.current_dir[:self.current_dir.rfind("\\")+1]
    def __call__(self):
        return self.current_dir
class dB:
    def __init__(self,delta,multi,save_size):
        try:
            self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            self.fail=False
        except:
            self.fail=True
        self.delta=delta
        self.save_size=save_size
        self.save_size = save_size
        self.multi = multi
        self.save = [1]* self.save_size
        for i in range(self.save_size):
            self.__call()
    def __call(self):
        if self.fail:
            try:
                self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=44100, input=True,frames_per_buffer=1024)
                self.fail=False
            except:
                return None
        try:
            n=np.frombuffer(self.stream.read(1024),dtype=np.int16)
            f=np.fft.fft(n)
            fq=np.fft.fftfreq(len(n),1)**2
            p=np.abs(f)**2/len(f)
            self.save.append((10 * np.log10(max(np.sum(p * fq) / 1e-12, 1)))*self.multi + self.delta)
            self.save = self.save[1:]
            return self.save[-1]
        except:
            self.fail=True
            return None
    def __call__(self):
        if self.fail:
            try:
                self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=44100, input=True,frames_per_buffer=1024)
                self.fail=False
                self.save = [1]* self.save_size
                for i in range(self.save_size):
                    self.__call()
            except:
                return None
        self.__call()
        return np.average(np.array(self.save))
class wave:
    def __init__(self,x,y,size,color,limit,limit_color,range_,bg_color,line_color,base_color,font_color,warning,window):
        self.font_color=font_color
        self.font=pygame.font.SysFont("times",12)
        self.x=x+1
        self.y=y+1
        self.width,self.height=size
        self.width-=38
        self.height-=18
        self.base = pygame.surface.Surface([self.width + 38, self.height + 18])
        self.base_color=base_color
        self.bg=pygame.surface.Surface([self.width+2, self.height+2])
        self.bottom, self.top = range_
        self.surface_a = pygame.surface.Surface([self.width+1, self.height])
        self.surface_a.set_colorkey([0,0,0])
        self.surface_b = pygame.surface.Surface([self.width+1, self.height])
        self.surface_b.set_colorkey([0,0,0])
        self.t=0
        self.current_dB = get_dB()
        self.surface="a"
        self.color=color
        self.limit=limit
        self.limit_color=limit_color
        self.line_color=line_color
        self.bg_color = bg_color
        self.window=window
        self.over = 0
        self.warning = warning
        self.save=[]
        self.sound_list=[]
        try:
            with open(dir_()+"warning.wav","r"):
                pass
            self.sound_list.append(dir_()+"warning.wav")
        except:
            pass
        try:
            with open(dir_()+"warning.mp3","r"):
                pass
            self.sound_list.append(dir_()+"warning.mp3")
        except:
            pass
        for root, dirs, files in os.walk("warning"):
            for i in files:
                if i[-4:]==".mp3"or i[-4:]==".wav":
                   self.sound_list.append(dir_()+"warning/"+i)
    def get_y(self,n):
        return (self.height * (self.top - n)) / (self.top - self.bottom)
    def update(self,val=None,reset=False):
        last_dB = self.current_dB
        x_b=-self.width-1
        surface_2=None
        if self.t<self.width:
            if not reset:
                self.save.append(self.current_dB)
            t=self.t
            x_a=self.x
            surface=self.surface_a
        elif self.t == self.width:
            if not reset:
                self.save.append(self.current_dB)
                self.save=self.save[1:]
            t = self.t - self.width
            x_a = self.x - self.t + self.width - 1
            x_b = self.x - self.t + 2 * self.width - 1
            surface = self.surface_b
            surface_2 = self.surface_a
        elif self.t<self.width*2:
            if not reset:
                self.save.append(self.current_dB)
                self.save=self.save[1:]
            t=self.t-self.width
            if self.surface=="a":
                x_a=self.x-self.t+self.width-1
                x_b = self.x - self.t + 2*self.width - 1
                surface=self.surface_b
            elif self.surface=="b":
                x_b=self.x-self.t+self.width-1
                x_a = self.x - self.t + 2*self.width - 1
                surface=self.surface_a
        elif self.t == self.width * 2:
            if not reset:
                self.save.append(self.current_dB)
                self.save=self.save[1:]
            self.t -= self.width
            if self.surface == "a":
                self.surface_a.fill([0,0,0])
                self.surface = "b"
            elif self.surface == "b":
                self.surface_b.fill([0,0,0])
                self.surface = "a"
            t = self.t - self.width
            if self.surface == "a":
                x_a = self.x - self.t + self.width - 1
                x_b = self.x - self.t + 2 * self.width - 1
                surface = self.surface_b
                surface_2 = self.surface_a
            elif self.surface == "b":
                x_b = self.x - self.t + self.width - 1
                x_a = self.x - self.t + 2 * self.width - 1
                surface = self.surface_a
                surface_2 = self.surface_b
        if val==None:
            self.current_dB = get_dB()
        else:
            self.current_dB = val
        font_color=self.font_color
        try:
            if self.current_dB>=self.limit:
                self.over+=1
                font_color = self.limit_color
            else:
                if self.over>0:
                    self.over-=waring//10
                    if self.over<0:
                        self.over=0
        except:
            pass
        if self.over>self.warning and not reset:
            try:
                self.over=0
                pygame.mixer.music.load(random.choice(self.sound_list))
                pygame.mixer.music.set_volume(1)
                pygame.mixer.music.play()
            except:
                pass
        try:
            if self.current_dB>=self.limit:
                font_color = self.limit_color
        except:
            pass
        if self.current_dB!=None and last_dB!=None:
            pygame.draw.line(surface, self.color, (t, self.get_y(last_dB)),(t + 1, self.get_y(self.current_dB)), 1)
        pygame.draw.line(surface, self.limit_color, (t, self.get_y(self.limit)),(t + 1, self.get_y(self.limit)), 1)
        if surface_2 !=None:
            if self.current_dB != None and last_dB!=None:
                pygame.draw.line(surface_2, self.color, (t+self.width, self.get_y(last_dB)),(t+self.width + 1, self.get_y(self.current_dB)), 1)
            pygame.draw.line(surface_2, self.limit_color, (t+self.width, self.get_y(self.limit)), (t +self.width+ 1, self.get_y(self.limit)), 1)
        self.bg.fill(self.line_color)
        bg_ = pygame.surface.Surface([self.width, self.height])
        bg_.fill(self.bg_color)
        i=(self.bottom%10+1)*10
        self.base.fill(self.base_color)
        while i<self.top:
            text = self.font.render(str(i), True, self.font_color)
            self.base.blit(text,(14 - (text.get_size()[0]) / 2, self.get_y(i) + 9 - (text.get_size()[1]) / 2))
            pygame.draw.line(bg_, self.line_color, (0, self.get_y(i)), (self.width, self.get_y(i)), 1)
            i+=10
        text=self.font.render(str(self.bottom),True,self.font_color)
        self.base.blit(text,(14-(text.get_size()[0])/2,self.get_y(self.bottom)+9-(text.get_size()[1])/2))
        text = self.font.render(str(self.top), True, self.font_color)
        self.base.blit(text, (14 - (text.get_size()[0]) / 2, self.get_y(self.top) + 9 - (text.get_size()[1]) / 2))
        self.bg.blit(bg_, [1, 1])
        if self.surface == "a":
            bg_.blit(self.surface_a, [x_a-self.x, 0])
            bg_.blit(self.surface_b, [x_b-self.x, 0])
        if self.surface == "b":
            bg_.blit(self.surface_b, [x_b-self.x, 0])
            bg_.blit(self.surface_a, [x_a-self.x, 0])
        try:
            text = self.font.render("Current dB: {:.4f}dB".format(self.current_dB), True, font_color)
        except:
            text = self.font.render("Error: Microphone not available.", True, font_color)
        pygame.draw.rect(bg_,self.line_color,[10,10,(text.get_size()[0]+35)//2*2,30])
        pygame.draw.rect(bg_, self.base_color, [11, 11, (text.get_size()[0]+33)//2*2, 28])
        pygame.draw.rect(bg_, [i-20 for i in self.color], [17, 17, 16, 16])
        pygame.draw.rect(bg_, self.color, [18, 18, 14, 14])
        bg_.blit(text,(38,25-(text.get_size()[1])/2))
        self.bg.blit(bg_, [1, 1])
        self.base.blit(self.bg, [28, 8])
        self.window.blit(self.base, [self.x-1, self.y-1])
        self.t+=1
    def reset(self,delta,multi,roll,limit,warning):
        self.save=[(i-get_dB.delta)/get_dB.multi*multi+delta for i in self.save]
        try:
            value_.max=(value_.max-get_dB.delta)/get_dB.multi*multi+delta
            value_.sum = (value_.sum - get_dB.delta*value_.num) / get_dB.multi * multi + delta*value_.num
            value_.average=value_.sum / value_.num
        except:
            pass
        self.warning=warning
        self.limit=limit
        get_dB.delta=delta
        get_dB.multi=multi
        get_dB.save_size=roll
        get_dB.save=[self.save[-1]]*get_dB.save_size
        self.t=len(self.save)
        self.t=0
        self.surface_a.fill([0,0,0])
        self.surface_b.fill([0,0,0])
        self.current_dB=self.save[0]
        for i in self.save[1:]:
            self.update(i,True)
class value:
    def __init__(self,x,y,size,color,bd_color,font_color,limit,limit_color,window):
        self.max=None
        self.sum=0
        self.num=0
        self.average=None
        self.font_1 = pygame.font.SysFont("times", 40)
        self.font_2 = pygame.font.SysFont("times", 300)
        self.x = x
        self.y = y
        self.font_color=font_color
        self.width, self.height = size
        self.base = pygame.surface.Surface([self.width, self.height])
        self.color = color
        self.bd_color = bd_color
        self.last_dB=0
        self.use_last_dB=0
        self.limit_color=limit_color
        self.limit=limit
        self.window=window
    def update(self):
        current_dB=get_dB()
        try:
            self.sum+=current_dB
            try:
                self.max=max(self.max,current_dB)
            except:
                self.max=current_dB
            self.num+=1
            self.average = self.sum/self.num
        except:
            pass
        self.base.fill(self.bd_color)
        color_1=self.font_color
        color_2 = self.font_color
        color_3 = self.font_color
        try:
            if current_dB>=self.limit:
                color_1=self.limit_color
        except:
            pass
        try:
            if self.max>=self.limit:
                color_2=self.limit_color
        except:
            pass
        try:
            if self.average>=self.limit:
                color_3=self.limit_color
        except:
            pass
        pygame.draw.rect(self.base,self.color,[1,1,self.width-2,self.height-2])
        if current_dB!=None:
            text=self.font_2.render(str(int(current_dB)),True,color_1)
        else:
            text=self.font_2.render("-",True,color_1)
        if self.max!=None:
            text_2=self.font_1.render("Max: "+str(int(self.max)),True,color_2)
        else:
            text_2=self.font_1.render("Max: -",True,color_2)
        if self.average!=None:
            text_3 = self.font_1.render("Average: "+str(int(self.average)), True, color_3)
        else:
            text_3=self.font_1.render("Average: -",True,color_3)
        self.base.blit(text, ((self.width - text.get_size()[0]) / 2, (self.height - text.get_size()[1]-text_2.get_size()[1]-30) / 2))
        self.base.blit(text_2, ((self.width - text_2.get_size()[0]-text_3.get_size()[0]-30) / 2, (self.height + text.get_size()[1]-text_2.get_size()[1]+30) / 2-50))
        self.base.blit(text_3, ((self.width + text_2.get_size()[0] - text_3.get_size()[0] + 30) / 2, (self.height + text.get_size()[1]-text_2.get_size()[1]+30) / 2-50))
        self.window.blit(self.base,(self.x,self.y))
class task_menu:
    def __init__(self,hide_=False):
        if hide_:
            self.hide_or_show = MenuItem('Show', self.show_window, default=True)
        else:
            self.hide_or_show = MenuItem('Hide', self.hide_window, default=True)
        self.menu = (self.hide_or_show, Menu.SEPARATOR, MenuItem('Exit', self.quit_window))
        image = Image.open(dir_()+"icon.ico")
        self.tray_icon = Icon("DB Monitor", image, "DB Monitor", self.menu)
        self.tray_icon.tooltip = "DB Monitor"
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    def quit_window(self):
        self.tray_icon.stop()
        hwnd = win32gui.FindWindow(None, "DB Monitor")
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        for i in psutil.process_iter():
            if i.pid == os.getpid():
                continue
            if i.name() == "DB Monitor.exe":
                i.kill()
        pygame.font.quit()
        pygame.quit()
    def show_window(self):
        hwnd = win32gui.FindWindow(None, "DB Monitor")
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
        self.hide_or_show.__init__('Hide', self.hide_window, default=True)
    def hide_window(self):
        hwnd = win32gui.FindWindow(None, "DB Monitor")
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        self.hide_or_show.__init__('Show', self.show_window, default=True)
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hide", dest='hide', action='store_const', const=True, default=False)
    args = parser.parse_args()
    dir_=dir()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('localhost', 1201))
            sock.sendall(b"Show")
            received_data = sock.recv(1024)
            if received_data==b"Exit":
                sys.exit()
    except:
        pass
    try:
        server_ip = ('localhost', 1201)
        serve=MultiThreadTcpServer(server_ip, server)
        s_thread = threading.Thread(target=serve.serve_forever)
        s_thread.daemon = True
        s_thread.start()
    except:
        sys.exit()
    with open(dir_()+"setting.json", "r+") as f:
        setting = json.load(f)
    win = tk.Tk()
    monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
    work_area = monitor_info.get("Work")
    ts = 3
    try:
        try:
            img = Image.open(dir_()+"launch.gif")
            img = ImageSequence.Iterator(img)
            win.attributes("-alpha", 0.0)
            win.overrideredirect(True)
            size = '{}x{}+{}+{}'.format(960, 540, (work_area[2] - 960) // 2, (work_area[3] - 540) // 2)
            win.geometry(size)
            can = tk.Canvas(win, width=960, height=540, bg='white', bd=0, highlightthickness=0)
            can.pack(side="left", ipadx=0, ipady=0, padx=0, pady=0)
            size = 0
            for image in img:
                size += 1
            t = 20
            delt = size / (t * (ts + 2) + 2)
            for i in range(t + 1):
                win.attributes("-alpha", i / t)
                image = img[int(i * delt) % (size + 1)]
                image = image.resize((960, round(960 / image.size[0] * image.size[1])))
                if image.size[1] < 540:
                    image = image.resize((round(540 / image.size[1] * image.size[0]), 540))
                x, y = (image.size[0] - 960) // 2, (image.size[1] - 540) // 2
                image = image.crop(box=(x, y, x + 960, y + 540))
                p = ImageTk.PhotoImage(image)
                can.create_image((480, 270), image=p)
                win.update()
            for i in range(t + 1, t * (ts + 1) + 1):
                image = img[int(i * delt) % (size + 1)]
                image = image.resize((960, round(960 / image.size[0] * image.size[1])))
                if image.size[1] < 540:
                    image = image.resize((round(540 / image.size[1] * image.size[0]), 540))
                x, y = (image.size[0] - 960) // 2, (image.size[1] - 540) // 2
                image = image.crop(box=(x, y, x + 960, y + 540))
                p = ImageTk.PhotoImage(image)
                can.create_image((480, 270), image=p)
                win.update()
            for i in range(t * (ts + 1) + 1, t * (ts + 2) + 2):
                win.attributes("-alpha", 1 - (i - t * (ts + 1) - 1) / t)
                image = img[int(i * delt) % (size + 1)]
                image = image.resize((960, round(960 / image.size[0] * image.size[1])))
                if image.size[1] < 540:
                    image = image.resize((round(540 / image.size[1] * image.size[0]), 540))
                x, y = (image.size[0] - 960) // 2, (image.size[1] - 540) // 2
                image = image.crop(box=(x, y, x + 960, y + 540))
                p = ImageTk.PhotoImage(image)
                can.create_image((480, 270), image=p)
                win.update()
        except:
            try:
                image = Image.open(dir_()+"launch.jpg")
            except:
                image = Image.open(dir_()+"launch.png")
            image = image.resize((960, round(960 / image.size[0] * image.size[1])))
            if image.size[1] < 540:
                image = image.resize((round(540 / image.size[1] * image.size[0]), 540))
            x, y = (image.size[0] - 960) // 2, (image.size[1] - 540) // 2
            image = image.crop(box=(x, y, x + 960, y + 540))
            p = ImageTk.PhotoImage(image)
            win.attributes("-alpha", 0.0)
            win.overrideredirect(True)
            size = '{}x{}+{}+{}'.format(960, 540, (work_area[2] - 960) // 2, (work_area[3] - 540) // 2)
            win.geometry(size)
            can = tk.Canvas(win, width=960, height=540, bg='white', bd=0, highlightthickness=0)
            can.pack(side="left", ipadx=0, ipady=0, padx=0, pady=0)
            t = 20
            size = 49
            img = [image] * (size + 1)
            delt = size / (t * (ts + 2) + 2)
            for i in range(t + 1):
                win.attributes("-alpha", i / t)
                image = img[int(i * delt) % (size + 1)]
                image = image.resize((960, round(960 / image.size[0] * image.size[1])))
                if image.size[1] < 540:
                    image = image.resize((round(540 / image.size[1] * image.size[0]), 540))
                x, y = (image.size[0] - 960) // 2, (image.size[1] - 540) // 2
                image = image.crop(box=(x, y, x + 960, y + 540))
                p = ImageTk.PhotoImage(image)
                can.create_image((480, 270), image=p)
                win.update()
            for i in range(t + 1, t * (ts + 1) + 1):
                image = img[int(i * delt) % (size + 1)]
                image = image.resize((960, round(960 / image.size[0] * image.size[1])))
                if image.size[1] < 540:
                    image = image.resize((round(540 / image.size[1] * image.size[0]), 540))
                x, y = (image.size[0] - 960) // 2, (image.size[1] - 540) // 2
                image = image.crop(box=(x, y, x + 960, y + 540))
                p = ImageTk.PhotoImage(image)
                can.create_image((480, 270), image=p)
                win.update()
            for i in range(t * (ts + 1) + 1, t * (ts + 2) + 2):
                win.attributes("-alpha", 1 - (i - t * (ts + 1) - 1) / t)
                image = img[int(i * delt) % (size + 1)]
                image = image.resize((960, round(960 / image.size[0] * image.size[1])))
                if image.size[1] < 540:
                    image = image.resize((round(540 / image.size[1] * image.size[0]), 540))
                x, y = (image.size[0] - 960) // 2, (image.size[1] - 540) // 2
                image = image.crop(box=(x, y, x + 960, y + 540))
                p = ImageTk.PhotoImage(image)
                can.create_image((480, 270), image=p)
                win.update()
    except:
        pass
    win.destroy()
    get_dB = dB(setting["delta"], setting["multi"], setting["roll"])
    pygame.init()
    pygame.font.init()
    menu=task_menu(args.hide)
    window = pygame.display.set_mode((900, 400),pygame.HIDDEN)
    wave_ = wave(0, 0, [500, 400], [50, 70, 200], setting["limit"], [200, 70, 50], [40, 75], [200, 200, 200], [150, 150, 150],[225, 225, 225], [70, 70, 70],setting["warning"],window)
    value_ = value(500, 0, [400, 400], [210, 210, 210], [180, 180, 180], [70, 70, 70], setting["limit"], [200, 70, 50],window)
    pygame.display.set_caption("DB Monitor")
    pygame.display.set_icon(pygame.image.load(dir_()+"icon.ico"))
    clock = pygame.time.Clock()
    time_step = 0.1
    hwnd = win32gui.FindWindow(None, "DB Monitor")

    if args.hide:
        menu.hide_window()
    else:
        menu.show_window()
    monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
    work_area = monitor_info.get("Work")
    rect=win32gui.GetWindowRect(hwnd)
    win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,(work_area[2]-(rect[2]-rect[0]))//2, (work_area[3]-(rect[3]-rect[1]))//2,rect[2]-rect[0],rect[3]-rect[1],0)
    while True:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu.hide_window()
            try:
                with open(dir_()+"setting.json", "r+") as f:
                    setting2 = json.load(f)
                if setting2!=setting:
                    setting=setting2
                    try:
                        wave_.reset(setting["delta"], setting["multi"], setting["roll"], setting["limit"], setting["warning"])
                    except:
                        pass
            except PermissionError:
                pass
            wave_.update()
            value_.update()
            pygame.display.flip()
            clock.tick(30)
        except:
            serve.server_close()
            serve.shutdown()
            sys.exit()
