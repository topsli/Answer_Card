import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

import os
import cv2
import numpy as np
import logging

class wordPicture():
    
    def __init__(self, font_size=75): 
        self.font_size = font_size
        self.image_size = (self.font_size*3, self.font_size*3)
        self.font = ImageFont.truetype("unicode.ttf", self.font_size, encoding="unic")
        self.image = None 

    # From  https://stackoverflow.com/questions/32504246/draw-ellipse-in-python-pil-with-line-thickness
    def draw_circle(self, image, bounds, width=1, outline='white', antialias=4):
        """Improved ellipse drawing function, based on PIL.ImageDraw."""    
        mask = Image.new(
            size=[int(dim * antialias) for dim in image.size],
            mode='L', color='black')
        draw = ImageDraw.Draw(mask)
        for offset, fill in (width/-2.0, 'white'), (width/2.0, 'black'):
            left, top = [(value + offset) * antialias for value in bounds[:2]]
            right, bottom = [(value - offset) * antialias for value in bounds[2:]]
            draw.ellipse([left, top, right, bottom], fill=fill)
        mask = mask.resize(image.size, Image.LANCZOS)
        image.paste(outline, mask=mask)

    def draw_init(self, character):
        self.image = Image.new("RGBA", self.image_size ,(255,255,255,0))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.text( (self.font_size, int(self.font_size/2)) ,character,(0,0,0),font = self.font)
        
    def findHeart(self):
        assert self.image != None , "Draw a letter before find the center of letter."
        open_cv_image = np.array(self.image.convert('L'))
        ret,thresh = cv2.threshold(open_cv_image,0,100,cv2.THRESH_BINARY_INV)
        _,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt = contours[0]
        
        ### By Moments
        # M = cv2.moments(cnt)
        # cx = int(M['m10']/M['m00'])
        # cy = int(M['m01']/M['m00'])
        
        ### By Center
        x,y,w,h = cv2.boundingRect(cnt)
        cx = int(x+w/2)
        cy = int(y+h/2)
        return (cx,cy)
    
    def place_circle(self, heart, radius=45, width=5, padding=10) :
        cx,cy = heart
        circle = [int(cx)-radius,int(cy)-radius,int(cx)+radius,int(cy)+radius]
        self.draw_circle(self.image,circle, outline =(0,0,0),width=width)
        bound = (int(cx)-radius-width-padding,int(cy)-radius-width-padding,int(cx)+radius+width+padding,int(cy)+radius+width+padding)
        self.image = self.image.crop(bound)


    def setColor(self,color = (255,255,255)):
        assert self.image != None , "Draw a letter before setColor."
        R,G,B = color
        data = np.array(self.image)
        # Clear, make all black pixel
        for i,alpha in enumerate(data[:,:,3]) :
            for j,v in enumerate(alpha) :
                if v != 0 :
                    data[:,:,0],  data[:,:,1], data[:,:,2] =  0, 0, 0
        red, green, blue = data[:,:,0], data[:,:,1], data[:,:,2]
        mask = (red == 0) & (green == 0) & (blue == 0)
        data[:,:,:3][mask] = [R, G, B]
        self.image = Image.fromarray(data)

    def save(self,path='./'):
        try : 
            self.image.save(path)
            print('{} saved'.format(path))
        except : 
            logging.warning('Directory not found, try to build \"{}\"'.format(path))
            folder = os.path.basename(path)
            os.mkdir(folder)
            self.image.save(path)
        self.image = None

    def draw_word_in_circle(self, letter, color=(190,190,190), path='./'):
        if not path.endswith('/') :
            path += '/'
        letter = str(letter)
        file_name = path + letter + '.png'
        self.draw_init(letter)
        self.place_circle(self.findHeart(),radius=45, width=5, padding=10)
        self.setColor(color)
        self.save(file_name)


# Usage
# wp = wordPicture()
# for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890+-' :
#     wp.draw_word_in_circle(c,path='./icon')
        