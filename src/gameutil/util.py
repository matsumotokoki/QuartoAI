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

# def losePiecePos(board, box, piece, plist_column, plist_row):
#     psize = plist_column.size
#     checkpattern = np.full((psize), False)
#     if (len(box.piecelist)==0): return checkpattern
#     for i in range(psize):
#         tboard = board.clone()
#         tboard.setBoard(plist_column[i], plist_row[i], piece)
#         reach = np.where(np.absolute(tboard.line_info) == 3)
#
#         if reach[0].size == 0:
#             checkpattern[i] = True
#             continue
#         
#         for bp in box.piecelist:
#             if (not endPiece(tboard, bp)):
#                 checkpattern[i] = True
#     return checkpattern

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
        self.dark  = (165,30,30)
        self.light = (240,230,140)
        self.brown = (255,153,51)
        self.gray  = (125,125,125)

        pygame.init()
        self.screen = pygame.display.set_mode(Rect(0,0,750,500).size)
        pygame.display.set_caption("Quarto")

    def UpdateDisplay(self, board, choicepiece, box):
        self.draw_gamewindow()
        self.draw_box(box)
        self.draw_board(board)
        self.draw_choice(choicepiece)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def draw_box(self, box):
        for i, p in enumerate(box.piecelist):
            color = self.light if p.toDict()['color'] == 'light' else self.dark
            size  = 45 if p.toDict()['height'] == 'tall' else 35
            if p.toDict()['shape'] == 'circular':
                if p.toDict()['top'] == 'hollow':
                    pygame.draw.circle(self.screen, (color), (500+230/4*(i%4)+230/8,30+230/4*(i//4)+230/8), size/2,5)
                else:
                    pygame.draw.circle(self.screen, (color), (500+230/4*(i%4)+230/8,30+230/4*(i//4)+230/8), size/2)
            elif p.toDict()['shape'] == 'square':
                if p.toDict()['top'] == 'hollow':
                    pygame.draw.rect(self.screen, (color), Rect(500+230/4*(i%4)+(230/4-size)/2,30+230/4*(i//4)+(230/4-size)/2,size,size),3)
                else:
                    pygame.draw.rect(self.screen, (color), Rect(500+230/4*(i%4)+(230/4-size)/2,30+230/4*(i//4)+(230/4-size)/2,size,size),0)

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
        pygame.draw.rect(self.screen, (self.gray), Rect(0,0,750,500),0)
        pygame.draw.rect(self.screen, (self.brown), Rect(30,30,440,440),0)
        pygame.draw.rect(self.screen, (self.black), Rect(30,30,440,440),5)
        for i in range(5):
            pygame.draw.line(self.screen, (self.black), (30,30+440/4*i), (470,30+440/4*i),3)
            pygame.draw.line(self.screen, (self.black), (30+440/4*i,30), (30+440/4*i,470),3)

        pygame.draw.rect(self.screen, (self.white), Rect(500,30,230,230),0)
        pygame.draw.rect(self.screen, (self.black), Rect(500,30,230,230),5)
        for i in range(5):
            pygame.draw.line(self.screen, (self.black), (500,30+230/4*i),(730,30+230/4*i),3)
            pygame.draw.line(self.screen, (self.black), (500+230/4*i,30),(500+230/4*i,260),3)

        pygame.draw.rect(self.screen, (self.white), Rect(500,290,230,180),0)
        pygame.draw.rect(self.screen, (self.black), Rect(500,290,230,180),5)

    #TODO
    def draw_turn(self, turn):
        pass
    
    #TODO
    def draw_winner(self, winner):
        pass

