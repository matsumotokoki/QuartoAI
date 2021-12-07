from . import piece
import copy
import numpy as np

class Board:
    def __init__(self, boardlist=None):
        self.onboard=None
        if (boardlist is not None):
            self.onboard = np.full((4,4), None)
            for cell in boardlist:
                if cell["piece"] is not None:
                    self.setBoard(\
                            cell["column"],
                            cell["row"],
                            piece.Piece.getInstance(cell["piece"])\
                        )

    def setBoard(self, column, row, piece):
        self.onboard[column, row] = piece

    def getBoard(self, column, row):
        return self.onboard[column, row]

    def toList(self):
        return self.onboard

    def toJsonObject(self):
        obj = []
        for column in range(4):
            for row in range(4):
                p = self.onboard[column,row]
                if p is not None: p = p.toDict()
                dic = {\
                    "column":column,\
                    "row":row,\
                    "piece":p,\
                }
                obj.append(dic)
        return obj

class HiTechBoard(Board):
    def __init__(self, boardlist=None):
        self.line_info = None
        if(boardlist is not None):
            self.line_info = np.zeros((10,4))
            super(HiTechBoard,self).__init__(boardlist)

    def setBoard(self, column, row, piece):
        super(HiTechBoard,self).setBoard(column, row, piece)

        if piece is not None:
            col_index = column     #列のインデックス
            row_index = row+4  #行のインデックス

            self.line_info[col_index] += piece.param
            self.line_info[row_index] += piece.param

            #斜1の判定
            if column == row:
                self.line_info[8] += piece.param

            #斜2の判定
            if column + row == 3:
                self.line_info[9] += piece.param

    def isQuarto(self):
        if len(np.where(np.absolute(self.line_info)==4)[0]) != 0 : return True
        return False

    def clone(self):
        cobj = HiTechBoard()

        cobj.onboard = self.onboard.copy()
        cobj.line_info = self.line_info.copy()

        return cobj
