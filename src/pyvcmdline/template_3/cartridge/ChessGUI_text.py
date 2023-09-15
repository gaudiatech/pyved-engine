#! /usr/bin/env python
"""
 Project: Python Chess
 File name: ChessGUI_text.py
 Description:  Draws a text based chess board in the console window.
	Gets user input through text entry.
	
 Copyright (C) 2009 Steve Osborne, srosborne (at) gmail.com
 http://yakinikuman.wordpress.com/
 """
 
from ChessRules import ChessRules

class ChessGUI_text:
	def __init__(self):
		self.Rules = ChessRules()
		
	# def GetGameSetupParams(self):
	#MOVED FUNCTIONALITY TO CHESSGAMEPARAMS.PY
		# player1Name = raw_input("Player 1 name: ")
		# player1Color = 'red'
		# while not player1Color == 'black' and not player1Color == 'white':
			# player1Color = raw_input("  Player 1 color ('white' or 'black'): ")
		# if player1Color == 'white':
			# player2Color = 'black'
		# else:
			# player2Color = 'white'
		# player1Type = 'monkey'
		# while not player1Type == 'human' and not player1Type == 'AI':
			# player1Type = raw_input("  Is player 1 'human' or 'AI'? ")

		# player2Name = raw_input("Player 2 name: ");
		# player2Type = 'monkey'
		# while not player2Type == 'human' and not player2Type == 'AI':
			# player2Type = raw_input("  Is player 2 'human' or 'AI'? ")

		# print "Setting up game..."
		# print "Player 1:", player1Name, player1Color, player1Type
		# print "Player 2:", player2Name, player2Color, player2Type

		# return (player1Name,player1Color,player1Type,player2Name,player2Color,player2Type)

	def Draw(self,board):
		print("    c0   c1   c2   c3   c4   c5   c6   c7 ")
		print("  ----------------------------------------")
		for r in range(8):
			print( "r"+str(r)+"|",end='')
			for c in range(8):
				if board[r][c] != 'e':
					print(  str(board[r][c]), "|",end='')
				else:
					print( "   |", end='')
				if c == 7:
					print() #to get a new line
			print ("  ----------------------------------------")

	def EndGame(self,board):
		self.Draw(board)
	
	def GetPlayerInput(self,board,color):
		fromTuple = self.GetPlayerInput_SquareFrom(board,color)
		toTuple = self.GetPlayerInput_SquareTo(board,color,fromTuple)
		return (fromTuple,toTuple)


	def GetPlayerInput_SquareFrom(self,board,color):
		ch = "?"
		cmd_r = 0
		cmd_c = 0
		while (ch not in board[cmd_r][cmd_c] or self.Rules.get_valid_moves(board, color, (cmd_r, cmd_c)) == []):
			print("Player", color)
			cmd_r = int(input("  From row: "))
			cmd_c = int(input("  From col: "))
			if color == "black":
				ch = "b"
			else:
				ch = "w"
			if (board[cmd_r][cmd_c] == 'e'):
				print( "  Nothing there!")
			elif (ch not in board[cmd_r][cmd_c]):
				print ("  That's not your piece!")
			elif self.Rules.get_valid_moves(board, color, (cmd_r, cmd_c)) == []:
				print ("  No valid moves for that piece!")

		return (cmd_r,cmd_c)


	def GetPlayerInput_SquareTo(self,board,color,fromTuple):
		toTuple = ('x','x')
		validMoveList = self.Rules.get_valid_moves(board, color, fromTuple)
		print ("List of valid moves for piece at",fromTuple,": ", validMoveList)

		while (not toTuple in validMoveList):
			cmd_r = int(input("  To row: "))
			cmd_c = int(input("  To col: "))
			toTuple = (cmd_r,cmd_c)
			if not toTuple in validMoveList:
				print( "  Invalid move!")

		return toTuple


	def PrintMessage(self,message):
		print (message)
		
if __name__ == "__main__":
	from ChessBoard import ChessBoard
	
	cb = ChessBoard(0)
	
	gui = ChessGUI_text()
	gui.Draw(cb.state)
