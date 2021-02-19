import cv2

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture('static\whatsapp.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        currentframe = 0
  
        while(True): 
            ret,frame = self.video.read() 
  
            if ret: 
        # if video is still left continue creating images 
                name = 'frames/' + str(currentframe) + '.jpg'
                print ('Creating...' + name) 
  
        
                cv2.imwrite(name, frame) 
  
        # increasing counter so that it will 
        # show how many frames are created 
                currentframe += 1
        return self

