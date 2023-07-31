




class ChessRules:
	BLACK_PLAYER, WHITE_PLAYER = 'black', 'white'

	def is_checkmate(self, board, chesscolor: str):
		"""
		returns True if 'color' player is in checkmate, uses GetListOfValidMoves
		for each piece... If there aren't any valid moves, then return true
		"""

		if chesscolor == self.__class__.BLACK_PLAYER:
			my_color = 'b'
		elif chesscolor == self.__class__.WHITE_PLAYER:
			my_color = 'w'
		else:
			raise ValueError('ERR: invalid chesscolor arg. passed to ChessRules.is_checkmate!')

		myColorValidMoves = list()
		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if my_color in piece:
					myColorValidMoves.extend(self.GetListOfValidMoves(board, my_color, (row, col)))
		return not len(myColorValidMoves)

	def GetListOfValidMoves(self, board, color, fromTuple):
		legalDestinationSpaces = list()
		for row in range(8):
			for col in range(8):
				d = (row, col)
				if self.IsLegalMove(board, color, fromTuple, d):
					if not self.DoesMovePutPlayerInCheck(board, color, fromTuple, d):
						legalDestinationSpaces.append(d)
		return legalDestinationSpaces

	def IsLegalMove(self, board, color, fromTuple, toTuple):
		# print "IsLegalMove with fromTuple:",fromTuple,"and toTuple:",toTuple,"color = ",color
		fromSquare_r = fromTuple[0]
		fromSquare_c = fromTuple[1]
		toSquare_r = toTuple[0]
		toSquare_c = toTuple[1]
		fromPiece = board[fromSquare_r][fromSquare_c]
		toPiece = board[toSquare_r][toSquare_c]

		if color == "black":
			enemyColor = 'w'
		if color == "white":
			enemyColor = 'b'

		if fromTuple == toTuple:
			return False

		if "P" in fromPiece:
			# Pawn
			if color == "black":
				if toSquare_r == fromSquare_r + 1 and toSquare_c == fromSquare_c and toPiece == 'e':
					# moving forward one space
					return True
				if fromSquare_r == 1 and toSquare_r == fromSquare_r + 2 and toSquare_c == fromSquare_c and toPiece == 'e':
					# black pawn on starting row can move forward 2 spaces if there is no one directly ahead
					if self.is_clear_path(board, fromTuple, toTuple):
						return True
				if toSquare_r == fromSquare_r + 1 and (
						toSquare_c == fromSquare_c + 1 or toSquare_c == fromSquare_c - 1) and enemyColor in toPiece:
					# attacking
					return True

			elif color == "white":
				if toSquare_r == fromSquare_r - 1 and toSquare_c == fromSquare_c and toPiece == 'e':
					# moving forward one space
					return True
				if fromSquare_r == 6 and toSquare_r == fromSquare_r - 2 and toSquare_c == fromSquare_c and toPiece == 'e':
					# black pawn on starting row can move forward 2 spaces if there is no one directly ahead
					if self.is_clear_path(board, fromTuple, toTuple):
						return True
				if toSquare_r == fromSquare_r - 1 and (
						toSquare_c == fromSquare_c + 1 or toSquare_c == fromSquare_c - 1) and enemyColor in toPiece:
					# attacking
					return True

		elif "R" in fromPiece:
			# Rook
			if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (toPiece == 'e' or enemyColor in toPiece):
				if self.is_clear_path(board, fromTuple, toTuple):
					return True

		elif "T" in fromPiece:
			# Knight
			col_diff = toSquare_c - fromSquare_c
			row_diff = toSquare_r - fromSquare_r
			if toPiece == 'e' or enemyColor in toPiece:
				if col_diff == 1 and row_diff == -2:
					return True
				if col_diff == 2 and row_diff == -1:
					return True
				if col_diff == 2 and row_diff == 1:
					return True
				if col_diff == 1 and row_diff == 2:
					return True
				if col_diff == -1 and row_diff == 2:
					return True
				if col_diff == -2 and row_diff == 1:
					return True
				if col_diff == -2 and row_diff == -1:
					return True
				if col_diff == -1 and row_diff == -2:
					return True

		elif "B" in fromPiece:
			# Bishop
			if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
					toPiece == 'e' or enemyColor in toPiece):
				if self.is_clear_path(board, fromTuple, toTuple):
					return True

		elif "Q" in fromPiece:
			# Queen
			if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (toPiece == 'e' or enemyColor in toPiece):
				if self.is_clear_path(board, fromTuple, toTuple):
					return True
			if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
					toPiece == 'e' or enemyColor in toPiece):
				if self.is_clear_path(board, fromTuple, toTuple):
					return True

		elif "K" in fromPiece:
			# King
			col_diff = toSquare_c - fromSquare_c
			row_diff = toSquare_r - fromSquare_r
			if toPiece == 'e' or enemyColor in toPiece:
				if abs(col_diff) == 1 and abs(row_diff) == 0:
					return True
				if abs(col_diff) == 0 and abs(row_diff) == 1:
					return True
				if abs(col_diff) == 1 and abs(row_diff) == 1:
					return True

		return False  # if none of the other "True"s are hit above

	def DoesMovePutPlayerInCheck(self, board, color, fromTuple, toTuple):
		"""
		makes a hypothetical move,
		returns True if it puts current player into check
		"""

		fromSquare_r = fromTuple[0]
		fromSquare_c = fromTuple[1]
		toSquare_r = toTuple[0]
		toSquare_c = toTuple[1]
		fromPiece = board[fromSquare_r][fromSquare_c]
		toPiece = board[toSquare_r][toSquare_c]

		# make the move, then test if 'color' is in check
		board[toSquare_r][toSquare_c] = fromPiece
		board[fromSquare_r][fromSquare_c] = 'e'

		retval = self.IsInCheck(board, color)

		# undo temporary move
		board[toSquare_r][toSquare_c] = toPiece
		board[fromSquare_r][fromSquare_c] = fromPiece

		return retval

	def IsInCheck(self, board, color):
		# check if 'color' is in check
		# scan through squares for all enemy pieces; if there IsLegalMove to color's king, then return True.
		if color == "black":
			myColor = 'b'
			enemyColor = 'w'
			enemyColorFull = 'white'
		else:
			myColor = 'w'
			enemyColor = 'b'
			enemyColorFull = 'black'

		kingTuple = (0, 0)
		# First, get current player's king location
		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if 'K' in piece and myColor in piece:
					kingTuple = (row, col)

		# Check if any of enemy player's pieces has a legal move to current player's king
		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if enemyColor in piece:
					if self.IsLegalMove(board, enemyColorFull, (row, col), kingTuple):
						return True
		return False

	def is_clear_path(self, board, from_pos, to_pos):
		# Return true if there is nothing in a straight line between fromTuple and toTuple, non-inclusive
		# Direction could be +/- vertical, +/- horizontal, +/- diagonal
		fromSquare_r = from_pos[0]
		fromSquare_c = from_pos[1]
		toSquare_r = to_pos[0]
		toSquare_c = to_pos[1]
		fromPiece = board[fromSquare_r][fromSquare_c]

		if abs(fromSquare_r - toSquare_r) <= 1 and abs(fromSquare_c - toSquare_c) <= 1:
			# The base case: just one square apart
			return True
		else:
			if toSquare_r > fromSquare_r and toSquare_c == fromSquare_c:
				# vertical +
				newTuple = (fromSquare_r + 1, fromSquare_c)
			elif toSquare_r < fromSquare_r and toSquare_c == fromSquare_c:
				# vertical -
				newTuple = (fromSquare_r - 1, fromSquare_c)
			elif toSquare_r == fromSquare_r and toSquare_c > fromSquare_c:
				# horizontal +
				newTuple = (fromSquare_r, fromSquare_c + 1)
			elif toSquare_r == fromSquare_r and toSquare_c < fromSquare_c:
				# horizontal -
				newTuple = (fromSquare_r, fromSquare_c - 1)
			elif toSquare_r > fromSquare_r and toSquare_c > fromSquare_c:
				# diagonal "SE"
				newTuple = (fromSquare_r + 1, fromSquare_c + 1)
			elif toSquare_r > fromSquare_r and toSquare_c < fromSquare_c:
				# diagonal "SW"
				newTuple = (fromSquare_r + 1, fromSquare_c - 1)
			elif toSquare_r < fromSquare_r and toSquare_c > fromSquare_c:
				# diagonal "NE"
				newTuple = (fromSquare_r - 1, fromSquare_c + 1)
			elif toSquare_r < fromSquare_r and toSquare_c < fromSquare_c:
				# diagonal "NW"
				newTuple = (fromSquare_r - 1, fromSquare_c - 1)

		if board[newTuple[0]][newTuple[1]] == 'e':
			return self.is_clear_path(board, newTuple, to_pos)
		return False


if __name__ == "__main__":
	from ChessBoard import ChessBoard
	cb = ChessBoard()
	rules = ChessRules()
	print(rules.is_checkmate(cb.GetState(), ChessRules.WHITE_PLAYER))
	print(rules.is_clear_path(cb.GetState(), (0, 0), (5, 5)))
	print(rules.is_clear_path(cb.GetState(), (1, 1), (5, 5)))
