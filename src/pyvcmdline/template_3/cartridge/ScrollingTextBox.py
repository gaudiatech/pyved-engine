#! /usr/bin/env python
"""
 Project: Python Chess
 File name: ScrollingTextBox.py
 Description:  Uses pygame to draw a scrolling text box, which is 
	incorporated in the ChessGUI_pygame class.

 Copyright (C) 2009 Steve Osborne, srosborne (at) gmail.com
 http://yakinikuman.wordpress.com/
 """
 
import pygame
from pygame.locals import *

class ScrollingTextBox:
	def __init__(self,screen,xmin,xmax,ymin,ymax):
		self.screen = screen
		pygame.font.init()
		self.fontDefault = pygame.font.Font( None, 20 )
		
		self.xmin = xmin
		self.xmax = xmax
		self.xPixLength = xmax - xmin
		self.ymin = ymin
		self.ymax = ymax
		self.yPixLength = ymax - ymin
		
		#max lines in text box is a function of ymin..ymax
		(width,height) = self.fontDefault.size('A')#width seems variable, but height is constant for most fonts (true?)
		self.lineHeight = height
		self.maxLines = self.yPixLength / self.lineHeight
		#print "Height is",height, "so maxLines is", self.maxLines

		#list of lines starts out empty
		self.lines = []
	
	def AddLine(self,newLine):
		#outside functions shouldn't call this...call Add instead (appropriately breaks up message string into lines)
		#there can only be "self.maxLines" in the self.lines array
		#  if textbox is not full, just append the newLine
		#  if textbox is full, pop a line off from the front and add newLine to the back
		if len(self.lines)+1 > self.maxLines:
			self.lines.pop(0) #pop(0) pops off beginning; pop() pops off end
		self.lines.append(newLine)
	
	def Add(self,message):
		#Break up message string into multiple lines, if necessary
		(width,height) = self.fontDefault.size(message)
		remainder = ""
		if width > self.xPixLength:
			while width > self.xPixLength:
				remainder = message[-1] + remainder
				message = message[0:-1] #chop off last character
				(width,height) = self.fontDefault.size(message)
		
		if len(remainder) > 0:
			if message[-1].isalnum() and remainder[0].isalnum():
				remainder = message[-1] + remainder
				message = message[0:-1] + '-'
				if message[-2] == ' ':
					message = message[0:-1] #remove the '-'
			
		self.AddLine(message)

		if len(remainder) > 0:
			#remove leading spaces
			while remainder[0] == ' ':
				remainder = remainder[1:len(remainder)]
			self.Add(remainder)

		
	def Draw(self):
		#Draw all lines
		xpos = self.xmin
		ypos = self.ymin
		color = (255,255,255)#white
		antialias = 1 #evidently, for some people rendering text fails when antialiasing is off
		for line in self.lines:
			renderedLine = self.fontDefault.render(line,antialias,color)
			self.screen.blit(renderedLine,(xpos,ypos))
			ypos = ypos + self.lineHeight
		

		

if __name__ == "__main__":
#testing stuff (if this file is run directly)
	pygame.init()
	pygame.display.init()
	screen = pygame.display.set_mode((800,500))
	screen.fill( (0,0,0) )
	xmin = 400
	xmax = 750
	ymin = 100
	ymax = 400
	textbox = ScrollingTextBox(screen,xmin,xmax,ymin,ymax)
	
	textbox.Add("hello")
	textbox.Add("When requesting fullscreen display modes, sometimes an exact match for the requested resolution cannot be made. In these situations pygame will select the closest compatable match. The returned surface will still always match the requested resolution.")
	textbox.Add("Soup for me!")
	textbox.Add("Another data structure for which a list works well in practice, as long as the structure is reasonably small, is an LRU (least-recently-used) container. The following statements moves an object to the end of the list:")
	textbox.Add("Set the current alpha value fo r the Surface. When blitting this Surface onto a destination, the pixels will be drawn slightly transparent. The alpha value is an integer from 0 to 255, 0 is fully transparent and 255 is fully opaque. If None is passed for the alpha value, then the Surface alpha will be disabled.")
	textbox.Add("All pygame functions will automatically lock and unlock the Surface data as needed. If a section of code is going to make calls that will repeatedly lock and unlock the Surface many times, it can be helpful to wrap the block inside a lock and unlock pair.")
	textbox.Draw()
	pygame.display.flip()
	
	while 1:
		for e in pygame.event.get():
			if e.type is KEYDOWN:
				pygame.quit()
				exit()
			if e.type is MOUSEBUTTONDOWN:
				(mouseX,mouseY) = pygame.mouse.get_pos()
				textbox.Add("Mouse clicked at ("+str(mouseX)+","+str(mouseY)+")")
				textbox.Draw()
				pygame.display.flip()


