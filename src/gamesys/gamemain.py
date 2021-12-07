from ..gameobject import board, box, piece
from . import gameplayer
from . import gameplayerinfo
from ..gameutil import util

import time
import numpy as np

class GameMain:
    def __init__(self, player1, player2):
        self.board = board.HiTechBoard([])
        self.box = box.Box(board=self.board) 
        self.choicepiece = None 
        self.call = "Non"
        self.playerlist =[\
            gameplayer.GamePlayer(player1),\
            gameplayer.GamePlayer(player2),\
        ]
        self.gameEnd = False
        self.turn = 0
        self.phase = "choice"
        self.winner = None
        self.turncounter = 0
        self.display = util.Display()

    def run(self):
        while not self.gameEnd:
            self.gameLoop()

        print("=" * 60)
        util.p.print('Game Over')
        self.drawBoard()

        if self.winner is None:
            util.p.print('Draw')
        else:
            util.p.print('player'+str(self.winner+1)+" is winner!")

        return self.winner
    
    def gameLoop(self):
        self.display.UpdateDisplay(self.board, self.choicepiece, self.box, self.turn, self.phase)
        if self.choicepiece is not None:
            util.p.print(str(self.turncounter)+' player' + str(self.turn+1)+ ' put')
            self.putPhase()
            self.drawPutPos()
            self.drawBoard()
            self.turncounter += 1
            self.display.UpdateDisplay(self.board, self.choicepiece, self.box, self.turn, self.phase)
            self.phase = "choice"
            if self.gameEnd: return
        
        self.display.UpdateDisplay(self.board, self.choicepiece, self.box, self.turn, self.phase)
        if len(self.box.piecelist) != 0:
            self.drawBox()
            util.p.print(str(self.turncounter)+ ' Player' + str(self.turn+1)+ ' choice')
            self.choicePhase()
            self.drawChoicePiece()
            self.drawBoard()
            self.display.UpdateDisplay(self.board, self.choicepiece, self.box, self.turn, self.phase)
            self.phase = "put"
            if self.gameEnd: return

        else:
            self.gameEnd = True
            return

        self.turn = (self.turn + 1) % 2

    def putPhase(self):
        ts = time.time()

        presult = self.playerlist[self.turn].put(self.board.toJsonObject(),\
                                                 self.choicepiece.toDict())

        util.p.print('Player'+ str(self.turn*1)+" put time : {0}".format(time.time()-ts)+"[sec]")

        self.column = presult['column']
        self.row = presult['row']
        self.board.setBoard(self.column, self.row, self.choicepiece)
        self.call = presult['call']

        self.checkCall()

    def choicePhase(self):
        ts = time.time()
        cresult = self.playerlist[self.turn].choice(self.board.toJsonObject(), self.box.toJsonObject())
        util.p.print('Player'+str(self.turn+1)+" choice time : {0}".format(time.time() - ts)+"[sec]")
        self.choicepiece = piece.Piece.getInstance(cresult['piece'])
        self.box.remove(self.choicepiece)
        self.call = cresult['call']
        self.checkCall()

    def checkCall(self):
        if self.call == "Quarto":
            util.p.print('Player'+str(self.turn+1)+' Quarto')
            if self.board.isQuarto():
                self.winner = self.turn
                self.gameEnd = True

            else:
                util.p.print("Error Call")
                self.winner = (self.turn+1)%2
                self.gameEnd = True

    def drawBoard(self):
        drawstrarray = np.full((4,4),None)
        for column in range(4):
            for row in range(4):
                p = self.board.getBoard(column,row)
                p = self.nonePiece() if p is None else str(p.toNumList())
                drawstrarray[column, row] = p
        util.p.print(drawstrarray)
        util.p.print('')

    def nonePiece(self):
        return '[0 0 0 0]'

    def drawBox(self):
        s = len(self.box.piecelist)
        for i in range(s):
            space = '  ' if i<10 else ' '
            util.p.print(str(i)+space+str(self.box.piecelist[i].toNumList()))
        util.p.print('')

    def drawChoicePiece(self):
        util.p.print('choice '+str(self.choicepiece.toNumList()))
        util.p.print('')
    
    def drawPutPos(self):
        util.p.print('put '+str(self.column)+','+str(self.row))
        util.p.print('')

def winningPercentageRun(gamenum, p1=None, p2=None):
    start = time.time()
    if(p1 is None):p1 = gameplayerinfo.playerAiList[0]
    if(p2 is None):p2 = gameplayerinfo.playerAiList[1]

    player1 = p1
    player2 = p2

    score = {
        player1:0,
        player2:0,
        None:0,
    }
    scoreper = {}

    for i in range(gamenum):
        res = GameMain(player1,player2).run()

        util.p.print(str(i+1) + " games over")
        util.p.print("First  Player1: "+str(player1)[1:-25])
        util.p.print("Second Player2: "+str(player2)[1:-25])
        if (res == 0):
            util.p.print('勝利AI：'+str(player1)[1:-25])
        elif (res == 1):
            util.p.print('勝利AI：'+str(player2)[1:-25])
        util.p.print('')

        score[player1] += 1 if res == 0 else 0
        score[player2] += 1 if res == 1 else 0
        score[None]    += 1 if res is None else 0

        temp_player = player1
        player1 = player2
        player2 = temp_player

    scoreper[player1] = score[player1] / gamenum * 100
    scoreper[player2] = score[player2] / gamenum * 100
    scoreper[None] = score[None] / gamenum * 100

    player1 = p1
    player2 = p2

    util.p.print('対戦数：'+str(gamenum))
    util.p.print('AI1:'+str(player1)[1:-25])
    util.p.print('AI2:'+str(player2)[1:-25])
    util.p.print('AI1の勝率：'+str(scoreper[player1]))
    util.p.print('AI2の勝率：'+str(scoreper[player2]))
    util.p.print('引き分け率：'+str(scoreper[None   ]))

    playtime = time.time() - start
    util.p.print("処理時間：{0}".format(playtime)+"[sec]")
    result = {
        '対戦回数：':gamenum,
        'AI1：':str(player1)[1:-25],
        'AI2：':str(player2)[1:-25],
        'AI1勝利数：':score[player1],
        'AI2勝利数：':score[player2],
        '引き分け数：':score[None   ],
        'AI1の勝率：':scoreper[player1],
        'AI2の勝率：':scoreper[player2],
        '引き分け率：':scoreper[None   ],
        '処理時間：':playtime,
    }
    return result
