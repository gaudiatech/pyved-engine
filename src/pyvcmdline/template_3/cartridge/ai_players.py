import random


from .model import ChessPlayer, ChessRules, ChessBoard, C_WHITE_PLAYER, C_BLACK_PLAYER, C_EMPTY_SQUARE


class ChessAI(ChessPlayer):
    def __init__(self, name, color: str):
        super().__init__(name, color)
        self._type = 'AI'
        self.Rules = ChessRules()


class ChessAI_random(ChessAI):
    """
    randomly picks any legal move
    """

    def GetMove(self, refboard, color):
        myPieces = self.GetMyPiecesWithLegalMoves(refboard, color)

        # pick a random piece, then a random legal move for that piece
        fromTuple = myPieces[random.randint(0, len(myPieces) - 1)]
        legalMoves = self.Rules.get_valid_moves(refboard, color, fromTuple)
        toTuple = legalMoves[random.randint(0, len(legalMoves) - 1)]

        moveTuple = (fromTuple, toTuple)
        return moveTuple

    def GetMyPiecesWithLegalMoves(self, board_obj, color):
        # print "In ChessAI_random.GetMyPiecesWithLegalMoves"
        if color == C_BLACK_PLAYER:
            my_color_prefix = 'b'
        elif color == C_WHITE_PLAYER:
            my_color_prefix = 'w'
        else:
            raise ValueError('getMyPiecesWithLegalMoves received color=', color)

        # get list of my pieces
        my_pieces = list()
        for row in range(8):
            for col in range(8):
                piece = board_obj.state[row][col]
                if my_color_prefix in piece:
                    if len(self.Rules.get_valid_moves(board_obj, color, (row, col))) > 0:
                        my_pieces.append((row, col))
        return my_pieces


class ChessAI_defense(ChessAI_random):
    """
    For each piece, find it's legal moves.
    Find legal moves for all opponent pieces.
    Throw out my legal moves that the opponent could get next turn.
    From remaining moves, if it puts opponent in check by performing the move, take it.
    Otherwise pick a random remaining move.

    Limitation(s):
    Doesn't include blocking or sacrificial moves of a lesser piece to protect better one.
    """

    def __init__(self, name, color, protectionPriority=("queen", "rook", "bishop", "knight", "pawn")):
        self.piecePriority = protectionPriority
        ChessAI.__init__(self, name, color)

    def GetMove(self, refboard, color):
        # print "In ChessAI_defense.GetMove"
        myPieces = self.GetMyPiecesWithLegalMoves(refboard, color)
        enemyPieces = self.GetEnemyPiecesWithLegalMoves(refboard, color)

        # Get "protected" moves - move piece such that opponent can't capture it next turn
        protectedMoveTuples = self.GetProtectedMoveTuples(refboard, color, myPieces, enemyPieces)

        # Top priority - pick a protected move that puts the enemy in check
        # print "Looking for move that puts enemy in check..."
        movesThatPutEnemyInCheck = self.GetMovesThatPutEnemyInCheck(refboard, color, protectedMoveTuples)
        if len(movesThatPutEnemyInCheck) > 0:
            # print "Picking move that puts enemy in check"
            return movesThatPutEnemyInCheck[random.randint(0, len(movesThatPutEnemyInCheck) - 1)]

        # Priority #2 - pick a protected move that will move one of player's pieces out of the line of fire
        # piecePriority set when class instantiated
        for pieceType in self.piecePriority:
            # print "Looking for move that protects my "+pieceType+"..."
            piecesProtectedMoves = self.GetMovesThatProtectPiece(refboard, color, pieceType, protectedMoveTuples)
            if len(piecesProtectedMoves) > 0:
                # print "Picking move that removes "+pieceType+" from danger"
                return piecesProtectedMoves[random.randint(0, len(piecesProtectedMoves) - 1)]

        # Priority #3 - pick a protected move that will capture one of the enemy's pieces
        for pieceType in self.piecePriority:
            # print "Looking for move that captures enemy "+pieceType+"..."
            capturePieceMoves = self.GetMovesThatCaptureEnemyPiece(refboard, color, pieceType, protectedMoveTuples)
            if len(capturePieceMoves) > 0:
                # print "Picking move that captures enemy "+pieceType
                return capturePieceMoves[random.randint(0, len(capturePieceMoves) - 1)]

        # If nothing from priority 1,2,and 3, then just pick any protected move
        if len(protectedMoveTuples) > 0:
            # print "Picking random protected move"
            return protectedMoveTuples[random.randint(0, len(protectedMoveTuples) - 1)]
        else:
            # If there aren't any protected moves, revert to random AI
            # print "No protected move exists; going to random's GetMove"
            return ChessAI_random.GetMove(self, refboard, color)

    def GetEnemyPiecesWithLegalMoves(self, board_obj, color):
        # print "In GetEnemyPiecesWithLegalMoves"
        if color == "black":
            myColor = 'b'
            enemyColor = 'w'
            enemyColor_full = 'white'
        else:
            myColor = 'w'
            enemyColor = 'b'
            enemyColor_full = 'black'

        # get list of opponent pieces that have legal moves
        enemyPieces = []
        for row in range(8):
            for col in range(8):
                piece = board_obj.state[row][col]
                if enemyColor in piece:
                    if len(self.Rules.get_valid_moves(board_obj, enemyColor_full, (row, col))) > 0:
                        enemyPieces.append((row, col))

        return enemyPieces

    def GetProtectedMoveTuples(self, board_obj, my_color, myPieces, enemyPieces):
        enemy_color = C_BLACK_PLAYER if my_color == C_WHITE_PLAYER else C_WHITE_PLAYER

        # Get possible moves that opponent can't get next turn
        safe_moves = list()
        risky_moves = set()

        for my_p in myPieces:
            risky_moves.clear()
            my_legalMoves = self.Rules.get_valid_moves(board_obj, my_color, my_p)

            for my_move in my_legalMoves:
                board_obj.move_piece(  # make an hypothetical move
                    (my_p, my_move)
                )

                for enemy_p in enemyPieces:
                    enemy_moves = self.Rules.get_valid_moves(board_obj, enemy_color, enemy_p)
                    for enemy_m in enemy_moves:
                        if enemy_m in my_legalMoves:
                            risky_moves.add(enemy_m)

                # undo the temporary move!
                board_obj.undo_move()

            for elt in my_legalMoves:
                if elt not in risky_moves:
                    safe_moves.append((my_p, elt))

        return safe_moves

    def GetMovesThatProtectPiece(self, board, color, pieceType, protectedMoveTuples):
        piecesProtectedMoves = []
        piecePositions = board.get_piece_positions(color, pieceType)
        if len(piecePositions) > 0:
            for p in piecePositions:
                if self.PieceCanBeCaptured(board, color, p):
                    piecesProtectedMoves.extend(self.GetPiecesMovesFromMoveTupleList(p, protectedMoveTuples))
        return piecesProtectedMoves

    def GetMovesThatCaptureEnemyPiece(self, board, my_color, pieceType, protectedMoveTuples):
        if my_color not in (C_BLACK_PLAYER, C_WHITE_PLAYER):
            raise ValueError('color non-valid')
        enemy_color = C_WHITE_PLAYER if my_color == C_BLACK_PLAYER else C_BLACK_PLAYER

        capturePieceMoves = []
        enemyPiecePositions = board.get_piece_positions(enemy_color, pieceType)
        if len(enemyPiecePositions) > 0:
            for p in enemyPiecePositions:
                if self.PieceCanBeCaptured(board, enemy_color, p):
                    capturePieceMoves.extend(self.GetCapturePieceMovesFromMoveTupleList(p, protectedMoveTuples))
        return capturePieceMoves

    def GetMovesThatPutEnemyInCheck(self, board, color, protectedMoveTuples):

        # print "In GetMovesThatPutEnemyInCheck"
        if color == C_BLACK_PLAYER:
            enemyColor_full = C_WHITE_PLAYER
        elif color == C_WHITE_PLAYER:
            enemyColor_full = C_BLACK_PLAYER
        else:
            raise ValueError()

        movesThatPutEnemyInCheck = list()
        for mt in protectedMoveTuples:
            if self.Rules.puts_player_in_check(board, enemyColor_full, mt[0], mt[1]):
                movesThatPutEnemyInCheck.append(mt)
        return movesThatPutEnemyInCheck

    def PieceCanBeCaptured(self, board, color, p):
        # true if opponent can capture the piece as board currently exists.
        if color == "black":
            myColor = 'b'
            enemyColor = 'w'
            enemyColorFull = 'white'
        else:
            myColor = 'w'
            enemyColor = 'b'
            enemyColorFull = 'black'

        for row in range(8):
            for col in range(8):
                piece = board.state[row][col]
                if enemyColor in piece:
                    if self.Rules.is_legal_move(board, enemyColorFull, (row, col), p):
                        return True
        return False

    def GetCapturePieceMovesFromMoveTupleList(self, p, possibleMoveTuples):
        # returns a subset of possibleMoveTuples that end with p
        moveTuples = []
        for m in possibleMoveTuples:
            if m[1] == p:
                moveTuples.append(m)
        return moveTuples

    def GetPiecesMovesFromMoveTupleList(self, p, possibleMoveTuples):
        # returns a subset of possibleMoveTuples that start with p
        moveTuples = []
        for m in possibleMoveTuples:
            if m[0] == p:
                moveTuples.append(m)
        return moveTuples


class ChessAI_offense(ChessAI_defense):
    """
    same as defense AI, except capturing enemy piece is higher priority than protecting own pieces
    """

    def __init__(self, name, color):
        super().__init__(name, color)
        self._opening = None

    def _move_from_opening(self, refboard):
        if refboard.turn == 0:
            return ChessAI.conv_move('e2e4')

        if self._opening == 'smith-morra':
            if refboard.turn == 2:
                return ChessAI.conv_move('d2d4')
            if refboard.turn == 4:
                return ChessAI.conv_move('b1c3')

        elif self._opening == 'gp-attack':
            if refboard.turn == 2:
                return ChessAI.conv_move('b1c3')
            if refboard.turn == 4:
                return ChessAI.conv_move('f2f4')

    def GetMove(self, refboard, color):
        # Tom's add-on. If AI player is playing white -> select one opening amongst:
        # - the grand prix attack
        # - the smith-morra gambit
        if refboard.turn == 0 and color == C_WHITE_PLAYER:
            self._opening = random.choice(('smith-morra', 'gp-attack'))
        if self._opening is not None:
            tmp = self._move_from_opening(refboard)
            if tmp is not None:
                return tmp

        # print "In ChessAI_offense.GetMove"
        myPieces = self.GetMyPiecesWithLegalMoves(refboard, color)
        enemyPieces = self.GetEnemyPiecesWithLegalMoves(refboard, color)

        # Get "protected" moves - move piece such that opponent can't capture it next turn
        protectedMoveTuples = self.GetProtectedMoveTuples(refboard, color, myPieces, enemyPieces)

        # Priority #1
        # pick a protected move that will capture one of the enemy's pieces
        # +-------------------------------------------------
        for pieceType in self.piecePriority:
            # print "Looking for move that captures enemy "+pieceType+"..."
            capturePieceMoves = self.GetMovesThatCaptureEnemyPiece(refboard, color, pieceType, protectedMoveTuples)
            if len(capturePieceMoves) > 0:
                # print "Picking move that captures enemy "+pieceType
                return capturePieceMoves[random.randint(0, len(capturePieceMoves) - 1)]

        # Priority #2
        # pick a protected move that puts the enemy in check
        # +-------------------------------------------------
        movesThatPutEnemyInCheck = self.GetMovesThatPutEnemyInCheck(refboard, color, protectedMoveTuples)
        if len(movesThatPutEnemyInCheck) > 0:
            # print "Picking move that puts enemy in check"
            return movesThatPutEnemyInCheck[random.randint(0, len(movesThatPutEnemyInCheck) - 1)]

        # Priority #3
        # pick a protected move that will move one of player's pieces out of the line of fire
        # piecePriority set when class instantiated
        # +-------------------------------------------------
        for pieceType in self.piecePriority:
            # print "Looking for move that protects my "+pieceType+"..."
            piecesProtectedMoves = self.GetMovesThatProtectPiece(refboard, color, pieceType, protectedMoveTuples)
            if len(piecesProtectedMoves) > 0:
                # print "Picking move that removes "+pieceType+" from danger"
                return piecesProtectedMoves[random.randint(0, len(piecesProtectedMoves) - 1)]

        # If nothing from priority 1,2,and 3, then just pick any protected move
        if len(protectedMoveTuples) > 0:
            return protectedMoveTuples[random.randint(0, len(protectedMoveTuples) - 1)]
        # If there aren't any protected moves, revert to random AI
        return ChessAI_random.GetMove(self, refboard, color)


if __name__ == "__main__":
    scr_size = (800, 766)
    import pygame

    pygame.init()
    scr = pygame.display.set_mode(scr_size)
    cb = ChessBoard(3)
    board = cb.state
    c_color = C_BLACK_PLAYER

    from chessmatch import ChessGameView
    gui = ChessGameView(cb)
    gui.drawboard(scr, board)#, highlight=[])
    pygame.display.flip()

    defense = ChessAI_defense('Bob', 'black')
    myPieces = defense.GetMyPiecesWithLegalMoves(cb, c_color)
    enemyPieces = defense.GetEnemyPiecesWithLegalMoves(cb, c_color)
    protectedMoveTuples = defense.GetProtectedMoveTuples(cb, c_color, myPieces, enemyPieces)
    movesThatPutEnemyInCheck = defense.GetMovesThatPutEnemyInCheck(cb, c_color, protectedMoveTuples)

    print("MyPieces = ", cb.ConvertSquareListToAlgebraicNotation(myPieces))
    print("enemyPieces = ", cb.ConvertSquareListToAlgebraicNotation(enemyPieces))
    print("protectedMoveTuples = ", cb.ConvertMoveTupleListToAlgebraicNotation(protectedMoveTuples))
    print("movesThatPutEnemyInCheck = ", cb.ConvertMoveTupleListToAlgebraicNotation(movesThatPutEnemyInCheck))

    stop = False
    while not stop:
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                stop=True
        gui.drawboard(scr, board)# highlight=[])
        pygame.display.flip()

    pygame.quit()
