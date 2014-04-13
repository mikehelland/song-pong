import alsaaudio, time, audioop
from collections import deque
from Tkinter import *
import numpy
import analyse

class App(object):
    def __init__(self, **kwargs):

        self.setupMics()

        self.audioSetup = False

        self.master = Tk()             
        
        self.w = self.master.winfo_screenwidth()
        self.h = self.master.winfo_screenheight()
        
        self.maxSize = min(self.w, self.h)
        
        self.canvas = Canvas(self.master, width=self.w, height=self.h)
        self.canvas.pack()
        self.canvas.configure(bg="black", highlightthickness=0, cursor='none')

        self.running = True
        
        self.master.overrideredirect(1)
        
        self.highLevel = 0

        self.setHighLevelAt = 0                            

        self.frames = deque()

        self.master.configure(bg="red", borderwidth=0)
        self.master.update()

        self.lastWidth = 0
        self.pitch = 0
        
        self.current_rectangle = False
        
        self.canvas.create_text(self.w/2, 15, text="OpenMusicGallery.net", fill="#0000FF", font="Helvetica 16", )        

        self.highest_shape = self.canvas.create_oval(self.w/2 - self.lastWidth /2,  self.h/2 - self.lastWidth /2, 
            self.w/2 + self.lastWidth /2,  self.h/2 + self.lastWidth /2, outline="#DDDD00", width=3)        

        self.current_shape = self.canvas.create_oval(self.w/2 - self.lastWidth /2,  self.h/2 - self.lastWidth /2, 
            self.w/2 + self.lastWidth /2,  self.h/2 + self.lastWidth /2, fill="blue")        

    
    def animation(self):
        
        caption = "level " + str(self.highLevel)
        pitchCaption = "pitch " + str(self.pitch)

        self.canvas.coords(self.highest_shape, self.w/2 - self.highLevel /2,  self.h/2 - self.highLevel /2, 
            self.w/2 + self.highLevel /2,  self.h/2 + self.highLevel /2)        
        self.canvas.tag_raise(self.highest_shape)

        self.canvas.coords(self.current_shape, self.w/2 - self.lastWidth /2,  self.h/2 - self.lastWidth /2, 
            self.w/2 + self.lastWidth /2,  self.h/2 + self.lastWidth /2)        
        self.canvas.tag_raise(self.current_shape)

        for i in range(len(self.frames)):
            frame = self.frames[i]
            if frame.width > 1:
                frame.width = frame.width - 1
                width = frame.width
                self.canvas.coords(frame.rectangle, self.w/2 - width /2,  self.h/2 - width /2, 
                    self.w/2 + width /2,  self.h/2 + width /2)


             
        #self.canvas.create_text(15, 35, text=pitchCaption, fill="purple", font="Helvetica 16", anchor="nw")
        self.master.update()


    def checkLevels2(self):        

        if not self.audioSetup:
            self.pyaud = pyaudio.PyAudio()
        
            self.stream = self.pyaud.open(
                format = pyaudio.paInt16,
                channels = 1,
                rate = 44100,
                input_device_index = 2,
                input = True)
                
            self.audioSetup = True


        #try:        
        rawsamps = self.stream.read(1024)
        samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
        self.pitch = analyse.musical_detect_pitch(samps)
        #except:
        #    print "error reading"
        
    def checkLevels(self):        
        l = False
        
        try:
            l,data = self.mics[0].read()
        except:
            print "error"
            
        print len(data)        

        if not l or len(data) < 2048:
            return

        samps = numpy.fromstring(data, dtype=numpy.int16)

        self.pitch = analyse.musical_detect_pitch(samps)
        loudness = min(0, max(-32, analyse.loudness(samps))) + 32
                                    
        colorWidth = loudness / 32 * self.maxSize

        self.lastWidth = colorWidth

        rect = self.canvas.create_oval(self.w/2 - colorWidth /2,  self.h/2 - colorWidth /2, 
            self.w/2 + colorWidth /2,  self.h/2 + colorWidth /2, fill="#000080")


        frame = SoundFrame(colorWidth, rect, colorWidth)
        self.frames.append(frame)

        if len(self.frames) > 60:
            self.canvas.delete(self.frames.popleft().rectangle)
                        
        if self.highLevel < colorWidth:
            self.highLevel = colorWidth
        else:
            self.highLevel = self.highLevel - 6


    def setupMics (self):

        cards = alsaaudio.cards()
        print cards

        # the first card is internal Intel
        # we need the rest
        self.mics = []
        for i in range(len(cards) - 1):
            
            inp  = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, "hw:CARD=" + cards[1 + i])
            
            inp.setchannels(1)
            inp.setrate(44100)
            inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            inp.setperiodsize(1024)
            
            self.mics.append(inp)


class SoundFrame(object):
    def __init__(self, value, rectangle, width, **kwargs):
        self.value = value
        self.rectangle = rectangle
        self.width = width
        

app = App()
loop = 0
while app.running:
    
    app.checkLevels()
    if loop == 0:
        app.animation()
        loop = 0
    else:
        loop = loop + 1
    
    #time.sleep(.001)
