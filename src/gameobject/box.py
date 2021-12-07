from . import piece
import copy 
import numpy as np

class Box:
    def __init__(self, boxlist=None, board=None):
        self.piecelist = None
        if (boxlist is not None):
            tlist = []
            for piecedict in boxlist:
                p = piece.Piece.getInstance(piecedict)
                tlist.append(p)
            self.piecelist = tlist

        if (board is not None):
            self.piecelist = piece.Piece.getAllPiece()
            for bp in board.onboard.flatten():
                if (bp is not None):
                    self.remove(bp)

    def clone(self):
        cobj = Box()

        cobj.piecelist = copy.copy(self.piecelist)
        return cobj

    def remove(self, piece):
        self.piecelist.remove(piece)

    def toJsonObject(self):
        obj = []
        for p in self.piecelist:
            obj.append(p.toDict())
        return obj
