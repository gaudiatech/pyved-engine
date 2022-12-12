#! /usr/bin/env python
"""
 Project: Python Chess
 File name: ChessBoard.py
 Description:  Board layout; contains what pieces are present
    at each square.
    
 Copyright (C) 2009 Steve Osborne, srosborne (at) gmail.com
 http://yakinikuman.wordpress.com/
 """
 
import string

class ChessBoard:
    def __init__(self,setupType=0):
        self.squares = [['e','e','e','e','e','e','e','e'],\
                        ['e','e','e','e','e','e','e','e'],\
                        ['e','e','e','e','e','e','e','e'],\
                        ['e','e','e','e','e','e','e','e'],\
                        ['e','e','e','e','e','e','e','e'],\
                        ['e','e','e','e','e','e','e','e'],\
                        ['e','e','e','e','e','e','e','e'],\
                        ['e','e','e','e','e','e','e','e']]
                        
        if setupType == 0:
            self.squares[0] = ['bR','bT','bB','bQ','bK','bB','bT','bR']
            self.squares[1] = ['bP','bP','bP','bP','bP','bP','bP','bP']
            self.squares[2] = ['e','e','e','e','e','e','e','e']
            self.squares[3] = ['e','e','e','e','e','e','e','e']
            self.squares[4] = ['e','e','e','e','e','e','e','e']
            self.squares[5] = ['e','e','e','e','e','e','e','e']
            self.squares[6] = ['wP','wP','wP','wP','wP','wP','wP','wP']
            self.squares[7] = ['wR','wT','wB','wQ','wK','wB','wT','wR']

        #Debugging set-ups
        #Testing IsLegalMove
        if setupType == 1:
            self.squares[0] = ['bR','bT','bB','bQ','bK','bB','bT','bR']
            self.squares[1] = ['e','e','e','e','e','e','e','e']
            self.squares[2] = ['e','e','e','e','e','e','e','e']
            self.squares[3] = ['e','e','e','e','e','e','e','e']
            self.squares[4] = ['e','e','e','e','e','e','e','e']
            self.squares[5] = ['e','e','e','e','e','e','e','e']
            self.squares[6] = ['wP','wP','wP','wP','wP','wP','wP','wP']
            self.squares[7] = ['wR','wT','wB','wQ','wK','wB','wT','wR']

        #Testing IsInCheck, Checkmate
        if setupType == 2:
            self.squares[0] = ['e','e','e','e','e','e','e','e']
            self.squares[1] = ['e','e','e','e','e','e','e','e']
            self.squares[2] = ['e','e','e','e','bK','e','e','e']
            self.squares[3] = ['e','e','e','e','bR','e','e','e']
            self.squares[4] = ['e','e','bB','e','e','e','wR','e']
            self.squares[5] = ['e','e','e','e','e','e','e','e']
            self.squares[6] = ['wB','e','e','e','e','e','e','e']
            self.squares[7] = ['e','e','e','wK','wQ','e','wT','e']

        #Testing Defensive AI
        if setupType == 3:
            self.squares[0] = ['e','e','e','e','e','e','e','e']
            self.squares[1] = ['e','e','e','e','e','e','e','e']
            self.squares[2] = ['e','e','e','e','bK','e','e','e']
            self.squares[3] = ['e','e','e','e','bR','e','e','e']
            self.squares[4] = ['e','e','bB','e','e','e','wR','e']
            self.squares[5] = ['e','e','e','e','e','e','e','e']
            self.squares[6] = ['e','e','e','e','e','e','e','e']
            self.squares[7] = ['e','e','e','wK','wQ','e','wT','e']          
            
    def GetState(self):
        return self.squares
        
    def ConvertMoveTupleListToAlgebraicNotation(self,moveTupleList):    
        newTupleList = []
        for move in moveTupleList:
            newTupleList.append((self.ConvertToAlgebraicNotation(move[0]),self.ConvertToAlgebraicNotation(move[1])))
        return newTupleList
    
    def ConvertSquareListToAlgebraicNotation(self,list):
        newList = []
        for square in list:
            newList.append(self.ConvertToAlgebraicNotation(square))
        return newList

    def ConvertToAlgebraicNotation(self, coords):
        row,col = coords
        #Converts (row,col) to algebraic notation
        #(row,col) format used in Python Chess code starts at (0,0) in the upper left.
        #Algebraic notation starts in the lower left and uses "a..h" for the column.
        return  self.ConvertToAlgebraicNotation_col(col) + self.ConvertToAlgebraicNotation_row(row)
    
    def ConvertToAlgebraicNotation_row(self,row):
        #(row,col) format used in Python Chess code starts at (0,0) in the upper left.
        #Algebraic notation starts in the lower left and uses "a..h" for the column.    
        B = ['8','7','6','5','4','3','2','1']
        return B[row]
        
    def ConvertToAlgebraicNotation_col(self,col):
        #(row,col) format used in Python Chess code starts at (0,0) in the upper left.
        #Algebraic notation starts in the lower left and uses "a..h" for the column.    
        A = ['a','b','c','d','e','f','g','h']
        return A[col]

        
    def GetFullString(self,p):
        if 'b' in p:
            name = "black "
        else:
            name = "white "
            
        if 'P' in p:
            name = name + "pawn"
        if 'R' in p:
            name = name + "rook"
        if 'T' in p:
            name = name + "knight"
        if 'B' in p:
            name = name + "bishop"
        if 'Q' in p:
            name = name + "queen"
        if 'K' in p:
            name = name + "king"
            
        return name
    
    def MovePiece(self,moveTuple):
        fromSquare_r = moveTuple[0][0]
        fromSquare_c = moveTuple[0][1]
        toSquare_r = moveTuple[1][0]
        toSquare_c = moveTuple[1][1]

        fromPiece = self.squares[fromSquare_r][fromSquare_c]
        toPiece = self.squares[toSquare_r][toSquare_c]

        self.squares[toSquare_r][toSquare_c] = fromPiece
        self.squares[fromSquare_r][fromSquare_c] = 'e'

        fromPiece_fullString = self.GetFullString(fromPiece)
        toPiece_fullString = self.GetFullString(toPiece)
        
        if toPiece == 'e':
            messageString = fromPiece_fullString+ " moves from "+self.ConvertToAlgebraicNotation(moveTuple[0])+\
                            " to "+self.ConvertToAlgebraicNotation(moveTuple[1])
        else:
            messageString = fromPiece_fullString+ " from "+self.ConvertToAlgebraicNotation(moveTuple[0])+\
                        " captures "+toPiece_fullString+" at "+self.ConvertToAlgebraicNotation(moveTuple[1])+"!"
        
        #capitalize first character of messageString
        tmp = messageString[0].upper() + messageString[1:len(messageString)]
        messageString = tmp
        
        return messageString

if __name__ == "__main__":
    
    cb = ChessBoard(0)
    board1 = cb.GetState()
    for r in range(8):
        for c in range(8):
            print(board1[r][c], end='')
        print("")
        
    print("Move piece test...")
    cb.MovePiece(((0,0),(4,4)))
    board2 = cb.GetState()
    for r in range(8):
        for c in range(8):
            print(board2[r][c], end='' )
        print("")
