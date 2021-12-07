from . import base_ai, ucb1
from ..gameobject import board, box, piece
import numpy as np
from ..gameutil import util
import time

class Parameter:
    def __init__(self):
        self.playoutTimelimit = 6   #プレイアウトの時間制限
        self.ucb1_c = 1.0           #ucb1のc定数
        self.ucb1_fpu = 100         #fpu値
        self.playoutDepthBorder = 4 #プレイアウトをさらに深くする閾値   -1はチェックしない
        self.putCgt = 10
        self.choiceCgt = 11

class Montecarlo(base_ai.BaseAi):
    def __init__(self):
        self.param = Parameter()

    def choice(self, in_board, in_box):
        in_board = board.HiTechBoard(in_board)
        in_box = box.Box(in_box)

        if len(in_box.piecelist) == 16:
            randnum = np.random.randint(len(in_box.piecelist))
            res_piece = in_box.piecelist[randnum]

        else:
            branchinfo = MontebranchInfo(in_board, in_box, None, True, self.param)
            res_piece = branchinfo.runChoice()

        res_piece = res_piece.toDict()
        res_call = "Quarto" if in_board.isQuarto() else "Non"

        return {'piece':res_piece,\
                'call':res_call,\
                }
    
    def put(self, in_board, in_piece):
        in_board = board.HiTechBoard(in_board)
        in_piece = piece.Piece.getInstance(in_piece)

        in_box = box.Box(board=in_board)
        in_box.remove(in_piece)

        branchinfo = MontebranchInfo(in_board, in_box, in_piece, True, self.param)
        res_column, res_row = branchinfo.runPut()
        in_board.setBoard(res_column, res_row, in_piece)
        res_call = "Quarto" if in_board.isQuarto() else "Non"

        return {'call':res_call,\
                'column':res_column,\
                'row':res_row}

class MonteBranchRand:
    def __init__(self, board, box, piece, myturn):
        self.board = board
        self.box = box
        self.piece = piece
        self.myturn = myturn
        self.winner = None

    def run(self):
        while(self.winner is None):
            if (self.piece is None):
                if (len(self.box.piecelist) == 0):
                    break
                self.choiceRand()
                self.myturn = not self.myturn
            else:
                self.putRand()
                if (len(self.box.piecelist)==0):
                    break
        return self.winner

    def putRand(self):
        if (util.endPiece(self.board, self.piece)):
            self.winner = self.myturn
            return

        checkpattern = util.losePiecePos(self.board, self.box, self.piece)

        if (not np.any(checkpattern)):
            self.winner = not self.myturn
            return
        
        patternlist = np.where(checkpattern)
        randnum = np.random.randint(patternlist[0].size)
        self.board.setBoard(patternlist[0][randnum], patternlist[1][randnum], self.piece)
        self.piece = None

    def choiceRand(self):
        oddspieces = util.oddsPieces(self.board, self.box.piecelist)
        patternsize = len(oddspieces)
        if (patternsize == 0):
            self.winner = not self.myturn
            return
        randnum = np.random.randint(patternsize)

        self.piece = oddspieces[randnum]
        self.box.remove(self.piece)

class DammyBranch:
    def __init__(self):
        self.myturn = True
        self.winner = False
        self.isLeaf = False
        self.branchlostcounter = 0
        self.leafcounter = 0
        self.branchnum = 1
    
    def onLeaf(self):
        pass

class MontebranchInfo:
    def __init__(self, board, box, piece, myturn, param, parent=DammyBranch()):
        self.board = board
        self.box = box
        self.piece = piece
        self.myturn = myturn
        self.param = param

        self.branchList = None        
        self.left = None              
        self.top = None               
        
        self.branchnum = 0            
        self.branchPlayoutCount = None
        self.branchPlayoutWin = None  
        self.branchPlayoutDraw = None 
        self.branchPlayoutTotal = 0   

        self.branchPlayoutTarget = 0  
        self.branchlostcounter = 0    
        self.leafcounter = 0          

        self.isLeaf = False           
        self.winner = None            
        self.parent = parent          

    def runChoice(self):
        cgtflag = len(np.where(self.board.onboard != None)[0]) >= self.param.choiceCgt
        self.createChoiceBranch(cgtflag)

        if (self.branchList is None): return self.box.piecelist[0]

        topScoreIndex = self.searchRoute()
        return self.branchList[topScoreIndex].piece
    
    def runPut(self):
        if (util.endPiece(self.board, self.piece)):
            return util.endPiecePos(self.board, self.piece)

        cgtflag = len(np.where(self.board.onboard != None)[0]) >= self.param.putCgt
        self.createPutBranch(cgtflag)

        if (self.branchList is None):
            index = np.where(self.board.onboard == None)
            return index[0][0], index[1][0]

        topScoreIndex = self.searchRoute()
        return self.branchList[topScoreIndex].column, self.branchList[topScoreIndex].row

    def createChoiceBranch(self, cgtflag):
        if(len(self.box.piecelist)==0):
            self.isLeaf = True
            self.onLeaf()
            return

        oddspieces = util.oddsPieces(self.board, self.box.piecelist)
        self.branchnum = len(oddspieces)

        if(self.branchnum == 0):
            self.winner = not self.myturn
            self.isLeaf = True
            self.onLeaf()
            return
        
        self.branchList = []
        for p in oddspieces:
            tbox = self.box.clone()
            tbox.remove(p)
            bi = MontebranchInfo(
                self.board.clone(), 
                tbox,              
                p,                 
                not self.myturn,   
                self.param,      
                self
            )
            self.branchList.append(bi)
        
        if(cgtflag):self.createChoiceCgt()
        else:self.playoutinit()

    def createChoiceCgt(self):
        for bi in self.branchList:
            bi.createPutBranch(True)
            bi.branchList = None
            if (self.isLeaf): break


    def createPutBranch(self, cgtflag):
        if (util.endPiece(self.board, self.piece)):
            self.winner = self.myturn
            self.isLeaf = True
            self.onLeaf()
            return

        if (len(self.box.piecelist)==0):
            self.isLeaf = True
            self.onLeaf()
            return

        checkpattern = util.losePiecePos(self.board, self.box, self.piece)
        patternlist = np.where(checkpattern)
        self.branchnum = patternlist[0].size

        if (self.branchnum == 0):
            self.winner = not self.myturn
            self.isLeaf = True
            self.onLeaf()
            return
        
        self.branchList = []
        for column, row in zip(patternlist[0], patternlist[1]):
            tboard = self.board.clone()
            tboard.setBoard(column, row, self.piece)
            bi = MontebranchInfo(\
                        tboard,\
                        self.box.clone(),\
                        None,\
                        self.myturn,\
                        self.param,\
                        self\
                    )
            bi.column = column
            bi.row = row
            self.branchList.append(bi)

        if (cgtflag): self.createPutCgt()
        else: self.playoutinit()

    def createPutCgt(self):
        for bi in self.branchList:
            bi.createChoiceBranch(True)
            bi.branchList = None
            if (self.isLeaf): break

    def playoutinit(self):
        self.branchPlayoutCount  = np.zeros((self.branchnum))
        self.branchPlayoutWin    = np.zeros((self.branchnum))
        self.branchPlayoutDraw   = np.zeros((self.branchnum))
        self.branchPlayoutTotal  = 0
        self.branchPlayoutTarget = 0
        self.branchlostcounter   = 0

    def onLeaf(self):
        self.parent.leafcounter += 1
        if (self.parent.myturn == self.winner):
            self.parent.winner = self.winner
            self.parent.isLeaf = True
            self.parent.onLeaf()
            return
        
        if ((not self.parent.myturn) == self.winner):
            self.parent.branchlostcounter += 1
            if(self.parent.branchlostcounter == self.parent.branchnum):
                self.parent.winner = self.winner
                self.parent.isLeaf = True
                self.parent.onLeaf()
                return
        if (self.parent.leafcounter == self.parent.branchnum):
            self.parent.isLeaf = True
            self.parent.onLeaf()
            return
        
        if (self.parent.leafcounter == self.parent.branchnum):
            self.parent.isLeaf = True
            self.parent.onLeaf()
            return

    def playout(self):
        result = False
        if (self.isLeaf):
            result = self.winner

        elif (self.branchList is None):
            result = MonteBranchRand(self.board.clone(), \
                                     self.box.clone(),\
                                     self.piece,\
                                     self.myturn).run()
        else:
            self.branchPlayoutCount[self.branchPlayoutTarget] += 1
            self.branchPlayoutTotal += 1
            targetbi = self.branchList[self.branchPlayoutTarget]

            if (self.branchPlayoutCount[self.branchPlayoutTarget] == self.param.playoutDepthBorder and targetbi.branchList is None):
                if (targetbi.piece is None):
                    cgtflag = len(np.where(targetbi.board.onboard != None)[0]) >= self.param.choiceCgt
                    targetbi.createChoiceBranch(cgtflag)
                else:
                    cgtflag = len(np.where(targetbi.board.onboard != None)[0]) >= self.param.putCgt
                    targetbi.createPutBranch(cgtflag)

            result = targetbi.playout()

            if result == self.myturn: self.branchPlayoutWin[self.branchPlayoutTarget] += 1
            elif result == None: self.branchPlayoutDraw[self.branchPlayoutTarget] += 1
        
            if (np.sum(self.branchPlayoutWin) != 0):
                u = ucb1.UCB1.ucb1(self.branchPlayoutCount, self.branchPlayoutWin, self.branchPlayoutTotal, self.param.ucb1_c, self.param.ucb1_fpu)
            else:
                u = ucb1.UCB1.ucb1(self.branchPlayoutCount, self.branchPlayoutDraw, self.branchPlayoutTotal, self.param.ucb1_c, self.param.ucb1_fpu)

            self.branchPlayoutTarget = u.argmax()
        
        return result

    def searchRoute(self):
        if (not self.isLeaf):
            endtime = time.time() + self.param.playoutTimelimit
            while(time.time() < endtime):
                self.playout()
                if (self.isLeaf):break

        returnIndex = -1
        countmax = -1

        for i in range(self.branchnum):
            if self.branchList[i].winner == True:
                returnIndex = i
                break
            
            elif self.branchList[i].winner is None:
                if self.isLeaf:
                    returnIndex = i
                elif countmax < self.branchPlayoutCount[i]:
                    countmax = self.branchPlayoutCount[i]
                    returnIndex = i

        if (returnIndex == -1):
            if self.isLeaf:
                returnIndex = 0
            else:
                returnIndex = self.branchPLayoutCount.argmax()

        self.simpleLog()
        
        return returnIndex
    
    def myprint(self, depth):
        if self.branchList is None: return
        if depth > 1 : return

        count = None
        if (self.branchPlayoutCount is not None):
            count = self.branchPlayoutCount
            win   = self.branchPlayoutWin
            draw  = self.branchPlayoutDraw
            wper  = self.branchPlayoutWin/self.branchPLayoutCount
            dper  = self.branchPlayoutDraw/self.branchPlayoutCount
            wucb  = ubc1.UCB1.ucb1(self.branchPlayoutCount, self.branchPlayoutWin,  self.branchPlayoutTotal)
            ducb  = ubc1.UCB1.ucb1(self.branchPlayoutCount, self.branchPlayoutDraw, self.branchPlayoutTotal)

        for i in range(self.branchnum):
            bi = self.brachList[i]
            c  = None if count is None else count[i]
            w  = None if count is None else win[i]
            d  = None if count is None else draw[i]
            wp = None if count is None else wper[i]
            dp = None if count is None else dper[i]
            wu = None if count is None else wucb[i]
            du = None if count is None else ducb[i]

            val = str(depth)+'\t'+str(self.myturn)
            if(bi.piece is not None):
                val += '\tchoice\t'+str(bi.piece.toNumList())
            else:
                val += '\tput\t'+str(bi.left)+','+str(bi.top)
            val += '\t'+str(bi.isLeaf)
            val += '\t'+str(bi.winner)
            val += '\t'+str(self.branchPlayoutTotal)
            val += '\t'+str(c)
            val += '\t'+str(w)
            val += '\t'+str(d)
            val += '\t'+str(wp)
            val += '\t'+str(dp)
            val += '\t'+str(wu)
            val += '\t'+str(du)            
            util.p.print(val)
            bi.myprint(depth+1)
        
    def simpleLog(self):
        util.p.print(str(self.isLeaf)+' '+str(self.winner)+' '+str(self.branchPlayoutTotal))























