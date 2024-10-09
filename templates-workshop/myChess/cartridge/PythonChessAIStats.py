"""
Project: Python Chess AI Stats Collection
File name: PythonChessAIStats.py
Description: Performs Monte Carlo runs to test Chess AI methods (found
in ChessAI.py).
Run with the "-h" option to get full listing of available options.

Example command line:
PythonChessAIStats.py -w offense -b defense -r 100 -s random_seeds_100.txt -o results.txt

Copyright (C) 2009 Steve Osborne, srosborne (at) gmail.com
https://yakinikuman.wordpress.com/

*******
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/
*******
"""

from __future__ import division  # so it turns integer division results into floats
import datetime
import random
from optparse import OptionParser
from model import ChessRules, ChessBoard, ChessPlayer
from ai_players import ChessAI_random, ChessAI_defense, ChessAI_offense


class PythonChessAIStats:
    def __init__(self):
        self.Rules = ChessRules()
        self.seeds = None

    def SetUp(self, whiteType, blackType):
        """
        types accepted are only in [offense, defense, random]
        """
        self.player = [0, 0]
        if whiteType == "defense":
            self.player[0] = ChessAI_defense("Defense AI - white", "white")
        elif whiteType == "offense":
            self.player[0] = ChessAI_offense("Offense AI - white", "white")
        else:
            self.player[0] = ChessAI_random("Random AI - white", "white")

        if blackType == "defense":
            self.player[1] = ChessAI_defense("Defense AI - black", "black")
        elif blackType == "offense":
            self.player[1] = ChessAI_offense("Offense AI - black", "black")
        else:
            self.player[1] = ChessAI_random("Random AI - black", "black")

    def Run(self, numRuns, useExternalSeed, seedFileName):
        self.seeds = []
        if useExternalSeed:
            # read seeds from seedFileName
            seedFile = open(seedFileName)
            for line in seedFile:
                if line != "":
                    self.seeds.append(int(line))

        self.results = []
        for r in range(numRuns):
            print()
            # load seed
            if r < len(self.seeds):
                random.seed(self.seeds[r])  # use file specified seed if available
                print("Using seed {}".format(self.seeds[r]))
            else:
                random.seed()  # otherwise, use the system clock (default action for random.seed())

            print("Playing Match #{}".format(r + 1), end='')
            self.results.append(self.PlaySingleMatch())

    def PlaySingleMatch(self):
        self.Board = ChessBoard(0)  # reset board
        currentPlayerIndex = 0
        turnCount = 0

        while not self.Rules.is_checkmate(self.Board, self.player[currentPlayerIndex].color):

            currentColor = self.player[currentPlayerIndex].color
            # hardcoded so that player 1 is always white
            if currentColor == 'white':
                turnCount = turnCount + 1
                if turnCount % 10 == 0:
                    print(" {}".format(turnCount), end='')
                if turnCount > 200:
                    return (turnCount, -1)  # Call it a draw... otherwise some games can go on forever.
            moveTuple = self.player[currentPlayerIndex].GetMove(self.Board, currentColor)
            moveReport = self.Board.move_piece(moveTuple)
            # moveReport = string like "White Bishop moves from A1 to C3" (+) "and captures ___!"
            # print moveReport
            currentPlayerIndex = (currentPlayerIndex + 1) % 2  # cause the currentPlayerIndex toggle between 1 and 0

        winnerIndex = (currentPlayerIndex + 1) % 2

        return (turnCount, winnerIndex)

    def PrintResults(self, writeToFile, outFileName, useExternalSeed, seedFileName):
        numRuns = len(self.results)
        whiteWins = 0
        whiteLosses = 0
        whiteTurnsToWin = 0
        whiteTurnsToLoss = 0
        blackWins = 0
        blackLosses = 0
        blackTurnsToWin = 0
        blackTurnsToLoss = 0
        draws = 0

        # winnerIndex: 0 for white, 1 for black, -1 for draw
        for m in self.results:
            turns = m[0]
            winner = m[1]
            if winner == 0:
                whiteWins = whiteWins + 1
                blackLosses = blackLosses + 1
                whiteTurnsToWin = whiteTurnsToWin + turns
                blackTurnsToLoss = blackTurnsToLoss + turns
            elif winner == 1:
                blackWins = blackWins + 1
                whiteLosses = whiteLosses + 1
                blackTurnsToWin = blackTurnsToWin + turns
                whiteTurnsToLoss = whiteTurnsToLoss + turns
            else:
                draws = draws + 1

        whiteWinPct = 100 * whiteWins / numRuns
        whiteAveTurnsToWin = whiteTurnsToWin / numRuns
        blackWinPct = 100 * blackWins / numRuns
        blackAveTurnsToWin = blackTurnsToWin / numRuns
        drawPct = 100 * draws / numRuns
        time = str(datetime.datetime.now())
        print()
        print("Final results: ")
        print("  " + time)
        print(" {}runs".format(numRuns))
        if useExternalSeed:
            print("  {} random seeds used from {}".format(len(self.seeds), seedFileName))
        print("  {} win pct = {}".format(self.player[0].name, whiteWinPct))
        print("  {} average number of turns to win = {}".format(self.player[0].name, whiteAveTurnsToWin))
        print("  {} win pct = {}".format(self.player[1].name, blackWinPct))
        print("  {} average number of turns to win = {}".format(self.player[1].name, blackAveTurnsToWin))
        print("  Draw pct = {}".format(drawPct))

        if writeToFile:
            f = open(outFileName, 'a')
            f.write("\n")
            f.write(time + "\n")
            f.write(str("%d runs" % numRuns) + "\n")
            if useExternalSeed:
                f.write(str("{} random seeds used from {}".format(len(self.seeds), seedFileName)) + "\n")
            f.write(str("{} win pct = {}".format(self.player[0].name, whiteWinPct)) + "\n")
            f.write(str("{} average number of turns to win = {}".format(self.player[0].name,
                                                                        whiteAveTurnsToWin)) + "\n")
            f.write(str("{} win pct = {}".format(self.player[1].name, blackWinPct)) + "\n")
            f.write(str("{} average number of turns to win = {}".format(self.player[1].name,
                                                                        blackAveTurnsToWin)) + "\n")
            f.write(str("Draw pct = {}".format(drawPct) + "\n"))


parser = OptionParser()
parser.add_option("-w", "--white", dest="whiteType",
                  help="Set white player AI('random','defense')", metavar="AITYPE")
parser.add_option("-b", "--black", dest="blackType",
                  help="Set black player AI('random','defense')", metavar="AITYPE")
parser.add_option("-r", "--runs", dest="numRuns",
                  help="Set number of runs", metavar="NUMRUNS")
parser.add_option("-s", "--seed", dest="seedFileName",
                  help="Optional seed input file", metavar="SEEDFILE")
parser.add_option("-o", "--out", dest="outFileName",
                  help="Optional results output file", metavar="OUTFILE")
(options, args) = parser.parse_args()

if options.whiteType:
    whiteType = options.whiteType
else:
    whiteType = "defense"

if options.blackType:
    blackType = options.blackType
else:
    blackType = "offense"

if options.numRuns:
    numRuns = int(options.numRuns)
else:
    numRuns = 5

if options.seedFileName:
    useExternalSeed = True
    seedFileName = options.seedFileName
else:
    useExternalSeed = False
    seedFileName = ""

if options.outFileName:
    writeToFile = True
    outFileName = options.outFileName
else:
    writeToFile = False
    outFileName = ""

stats = PythonChessAIStats()
stats.SetUp(whiteType, blackType)
stats.Run(numRuns, useExternalSeed, seedFileName)
stats.PrintResults(writeToFile, outFileName, useExternalSeed, seedFileName)
