import numpy as np
import copy
import codecs

import pygame
from pygame.locals import *


def endPiece(board, piece):
    putPieceResult = np.absolute(board.line_info + piece.param)
    return len(np.where(putPieceResult == 4)[0]) != 0

def endPiecePos(board, piece):
    patternlist = np.where(board.onboard==None)
    for column, row in zip(patternlist[0], patternlist[1]):
        tboard = board.clone()
        tboard.setBoard(column, row, piece)
        if (tboard.isQuarto()):
            return column, row

    return patternlist[0][0], patternlist[1][0]

def oddsPieces(board, piece):
    tempbox = copy.copy(piece)
    for p in piece:
        if endPiece(board, p):tempbox.remove(p)
    return tempbox

def losePiecePos(board, box, piece):
    checkpos = board.onboard == None
    if(len(box.piecelist)==0):return checkpos   #boxが空なら負けはしないので即リターン
    cw = np.where(checkpos)
    
    for column, row in zip(cw[0],cw[1]):
        tli = board.line_info.copy()
        tli[row] += piece.param
        tli[column+4] += piece.param
        tli[8] += piece.param if column == row else 0
        tli[9] += piece.param if column + row == 3 else 0
        if np.any(np.logical_or(tli == 3 ,tli == -3)):
            for p in box.piecelist:
                if not np.any(np.absolute(tli + p.param) == 4): break
            else:
                checkpos[column,row] = False

    return checkpos

class p:
    _file = None

    @classmethod
    def open(cls, filename):
        print("open file" + filename)
        cls._file = open(filename, "w", encoding="utf-8")

    @classmethod
    def close(cls):
        if(cls._file is not None):
            cls._file.close()
            cls._file = None
            print('close file ')

    @classmethod
    def print(cls,str):
        if(cls._file is not None):
            print(str, file=cls._file)
        print(str)
        #pass

class Display:
    def __init__(self):
        self.black = (0,0,0)
        self.white = (255,255,255)
        self.dark  = (195,60,60)
        self.light = (240,230,140)
        self.brown = (255,153,51)
        self.gray  = (115,115,115)
        self.red  = (240,30,30)

        pygame.init()
        self.font = pygame.font.Font(None,60)
        self.sfont = pygame.font.Font(None,30)
        self.ssfont = pygame.font.Font(None,20)
        self.screen = pygame.display.set_mode(Rect(0,0,750,550).size)
        pygame.display.set_caption("Quarto")

    def UpdateDisplay(self, board, choicepiece, box, turn, phase):
        self.turn = turn
        self.phase = phase
        self.draw_gamewindow()
        self.draw_box(box)
        self.draw_board(board)
        self.draw_choice(choicepiece)
        self.draw_turn(self.turn)
        self.draw_phase(self.phase)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def draw_box(self, box):
        for i, p in enumerate(box.piecelist):
            color = self.light if p.toDict()['color'] == 'light' else self.dark
            size  = 40 if p.toDict()['height'] == 'tall' else 30
            if p.toDict()['shape'] == 'circular':
                if p.toDict()['top'] == 'hollow':
                    pygame.draw.circle(self.screen, (color), (503+230/4*(i%4)+230/8,33+230/4*(i//4)+230/8), size/2,5)
                else:
                    pygame.draw.circle(self.screen, (color), (503+230/4*(i%4)+230/8,33+230/4*(i//4)+230/8), size/2)
            elif p.toDict()['shape'] == 'square':
                if p.toDict()['top'] == 'hollow':
                    pygame.draw.rect(self.screen, (color), Rect(503+230/4*(i%4)+(230/4-size)/2,33+230/4*(i//4)+(230/4-size)/2,size,size),3)
                else:
                    pygame.draw.rect(self.screen, (color), Rect(503+230/4*(i%4)+(230/4-size)/2,33+230/4*(i//4)+(230/4-size)/2,size,size),0)

        for i in range(16):
            text = self.ssfont.render(str(i), True, (self.gray))
            self.screen.blit(text, [504+230/4*(i%4),34+230/4*(i//4)])

    def draw_board(self, board):
        for i in range(4):
            for j in range(4):
                p = board.getBoard(i,j)
                if p == None:continue
                color = self.light if p.toDict()['color'] == 'light' else self.dark
                size  = 90 if p.toDict()['height'] == 'tall' else 70
                if p.toDict()['shape'] == 'circular':
                    if p.toDict()['top'] == 'hollow':
                        pygame.draw.circle(self.screen, (color), (30+440/4*(j)+440/8,30+440/4*(i)+440/8), size/2,5)
                    else:
                        pygame.draw.circle(self.screen, (color), (30+440/4*(j)+440/8,30+440/4*(i)+440/8), size/2)
                elif p.toDict()['shape'] == 'square':
                    if p.toDict()['top'] == 'hollow':
                        pygame.draw.rect(self.screen, (color), Rect(30+440/4*(j)+(440/4-size)/2,30+440/4*(i)+(440/4-size)/2,size,size),5)
                    else:
                        pygame.draw.rect(self.screen, (color), Rect(30+440/4*(j)+(440/4-size)/2,30+440/4*(i)+(440/4-size)/2,size,size),0)

    def draw_choice(self, choicepiece):
        p = choicepiece
        if p == None:return
        color = self.light if p.toDict()['color'] == 'light' else self.dark
        size  = 150 if p.toDict()['height'] == 'tall' else 120
        if p.toDict()['shape'] == 'circular':
            if p.toDict()['top'] == 'hollow':
                pygame.draw.circle(self.screen, (color), (615,380), size/2,5)
            else:
                pygame.draw.circle(self.screen, (color), (615,380), size/2)
        elif p.toDict()['shape'] == 'square':
            if p.toDict()['top'] == 'hollow':
                pygame.draw.rect(self.screen, (color), Rect(500+(230-size)/2,290+(180-size)/2,size,size),8)
            else:
                pygame.draw.rect(self.screen, (color), Rect(500+(230-size)/2,290+(180-size)/2,size,size),0)

    def draw_gamewindow(self):
        pygame.draw.rect(self.screen, (self.gray), Rect(0,0,750,550),0)

        pygame.draw.rect(self.screen, (self.brown), Rect(30,30,440,440),0)
        pygame.draw.rect(self.screen, (self.black), Rect(30,30,440,440),5)
        if self.phase=="put":pygame.draw.rect(self.screen, (self.red), Rect(25,25,450,450),5)
        for i in range(5):
            pygame.draw.line(self.screen, (self.black), (30,30+440/4*i), (470,30+440/4*i),3)
            pygame.draw.line(self.screen, (self.black), (30+440/4*i,30), (30+440/4*i,470),3)

        for i in range(4):
            text = self.sfont.render(str(i), True, (self.black))
            self.screen.blit(text, [8,80+110*i])
            self.screen.blit(text, [80+110*i,5])

        pygame.draw.rect(self.screen, (self.white), Rect(500,30,230,230),0)
        pygame.draw.rect(self.screen, (self.black), Rect(500,30,230,230),5)
        if self.phase=="choice":pygame.draw.rect(self.screen, (self.red), Rect(495,25,240,240),5)

        for i in range(5):
            pygame.draw.line(self.screen, (self.black), (500,30+230/4*i),(730,30+230/4*i),3)
            pygame.draw.line(self.screen, (self.black), (500+230/4*i,30),(500+230/4*i,260),3)


        pygame.draw.rect(self.screen, (self.white), Rect(500,290,230,180),0)
        pygame.draw.rect(self.screen, (self.black), Rect(500,290,230,180),5)

        pygame.draw.rect(self.screen, (self.white), Rect(30,490,440,50),0)
        pygame.draw.rect(self.screen, (self.black), Rect(30,490,440,50),5)

        pygame.draw.rect(self.screen, (self.white), Rect(500,490,230,50),0)
        pygame.draw.rect(self.screen, (self.black), Rect(500,490,230,50),5)

    def draw_turn(self, turn):
        text = self.font.render("player " + str(turn+1), True, (self.black))
        self.screen.blit(text, [170,493])
    
    #TODO
    def draw_phase(self, phase):
        text = self.font.render(phase, True, (self.black))
        self.screen.blit(text, [550,493] if phase == "choice" else [575, 493])
        pass

