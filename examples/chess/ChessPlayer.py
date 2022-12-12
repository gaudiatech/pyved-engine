#! /usr/bin/env python
"""
 Project: Python Chess
 File name: ChessPlayer.py
 Description:  Stores info on human chess player.
	
 Copyright (C) 2009 Steve Osborne, srosborne (at) gmail.com
 http://yakinikuman.wordpress.com/
 """

class ChessPlayer:
	def __init__(self,name,color):
		self.name = name
		self.color = color
		self.type = 'human'
		
	def GetName(self):
		return self.name
		
	def GetColor(self):
		return self.color
	
	def GetType(self):
		return self.type
		
if __name__ == "__main__":
	
	p = ChessPlayer("Kasparov","black")
	
	print(p.GetName())
	print(p.GetColor())
	print(p.GetType())
