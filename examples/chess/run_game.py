import time
from optparse import OptionParser

import katagames_engine as kengi
from ChessAI import ChessAI_random, ChessAI_defense, ChessAI_offense
from ChessBoard import ChessBoard
from ChessGUI_pygame import ChessGameView
from ChessPlayer import ChessPlayer
from ChessRules import ChessRules


# - pour switcher sur le mode jeu via console (sans pygame)
# import sys
# sys.argv = [sys.argv[0], "-t" ] #"small.txt"]

# if debug mode:
# self.Board = ChessBoard(2)

# 0 for normal board setup; see ChessBoard class for other options (for testing purposes)
board = ChessBoard(0)
rules = ules = ChessRules()
player = None
Gui = None
AIvsAI = False
AIpause = False
AIpauseSeconds = 0.0


def SetUp(options):
	global player, Gui, AIpause, AIvsAI, AIpauseSeconds
	# gameSetupParams: Player 1 and 2 Name, Color, Human/AI level
	# if self.debugMode:
	# 	player1Name = 'Kasparov'
	# 	player1Type = 'human'
	# 	player1Color = 'white'
	# 	player2Name = 'Light Blue'
	# 	player2Type = 'randomAI'
	# 	player2Color = 'black'

	default_config = ('Player1', 'white', 'human', 'AI', 'black', 'defenseAI')
	(player1Name, player1Color, player1Type, player2Name, player2Color, player2Type) = default_config

	player = [0, 0]
	if player1Type == 'human':
		player[0] = ChessPlayer(player1Name, player1Color)
	elif player1Type == 'randomAI':
		player[0] = ChessAI_random(player1Name, player1Color)
	elif player1Type == 'defenseAI':
		player[0] = ChessAI_defense(player1Name, player1Color)
	elif player1Type == 'offenseAI':
		player[0] = ChessAI_offense(player1Name, player1Color)

	if player2Type == 'human':
		player[1] = ChessPlayer(player2Name, player2Color)
	elif player2Type == 'randomAI':
		player[1] = ChessAI_random(player2Name, player2Color)
	elif player2Type == 'defenseAI':
		player[1] = ChessAI_defense(player2Name, player2Color)
	elif player2Type == 'offenseAI':
		player[1] = ChessAI_offense(player2Name, player2Color)

	if 'AI' in player[0].GetType() and 'AI' in player[1].GetType():
		AIvsAI = True
	else:
		AIvsAI = False

	if options.pauseSeconds > 0:
		AIpause = True
		AIpauseSeconds = int(options.pauseSeconds)
	else:
		AIpause = False

	# create the gui object - didn't do earlier because pygame conflicts with any gui manager (Tkinter, WxPython...)
	# if options.text:
	# 	guitype = 'text'
	# 	Gui = ChessGUI_text()
	# else:
	# 	guitype = 'pygame'
	Gui = ChessGameView(kengi.get_surface())


def loop():
	currentPlayerIndex = 0
	turnCount = 0
	gameover = False
	while not gameover:
		board_st = board.GetState()
		currentColor = player[currentPlayerIndex].GetColor()
		# hardcoded so that player 1 is always white
		if currentColor == 'white':
			turnCount = turnCount + 1
		Gui.PrintMessage("")
		baseMsg = "TURN %s - %s (%s)" % (str(turnCount), player[currentPlayerIndex].GetName(), currentColor)
		Gui.PrintMessage("-----%s-----" % baseMsg)

		# refresh GFX
		Gui.do_paint(board_st)
		kengi.flip()

		if rules.IsInCheck(board_st, currentColor):
			suffx = '{} ({}) is in check'.format(
				player[currentPlayerIndex].GetName(), player[currentPlayerIndex].GetColor()
			)
			Gui.PrintMessage("Warning..." + suffx)

		if player[currentPlayerIndex].GetType() == 'AI':
			moveTuple = player[currentPlayerIndex].GetMove(board.GetState(), currentColor)
		else:
			moveTuple = Gui.GetPlayerInput(board_st, currentColor)

		moveReport = board.move_piece(
			moveTuple)  # moveReport = string like "White Bishop moves from A1 to C3" (+) "and captures ___!"
		Gui.PrintMessage(moveReport)
		# this will cause the currentPlayerIndex to toggle between 1 and 0
		currentPlayerIndex = (currentPlayerIndex + 1) % 2
		if AIvsAI and AIpause:
			time.sleep(AIpauseSeconds)
		if rules.IsCheckmate(board.GetState(), player[currentPlayerIndex].color):
			gameover = True

	Gui.PrintMessage("CHECKMATE!")
	winnerIndex = (currentPlayerIndex + 1) % 2
	Gui.PrintMessage(
		player[winnerIndex].GetName() + " (" + player[winnerIndex].GetColor() + ") won the game!")
	Gui.EndGame(board_st)


parser = OptionParser()
parser.add_option(
	"-d", dest="debug",
	action="store_true", default=False, help="Enable debug mode (different starting board configuration)"
)
parser.add_option(
	"-t", dest="text",
	action="store_true", default=False, help="Use text-based GUI"
)
parser.add_option(
	"-o", dest="old",
	action="store_true", default=False, help="Use old graphics in pygame GUI"
)
parser.add_option(
	"-p", dest="pauseSeconds", metavar="SECONDS",
	action="store", default=0, help="Sets time to pause between moves in AI vs. AI games (default = 0)"
)

(options, args) = parser.parse_args()

if __name__ == '__main__':
	# before calling SetUp, need to init pygame etc.
	kengi.init(1)
	# -
	# pygame.init()
	# pygame.display.init()
	# pygame.display.set_mode(W_SIZE)
	SetUp(options)
	loop()
	kengi.quit()

