from . import base_ai
from ..gameobject import board, box, piece
import numpy as np
from ..gameutil import util

class RandomAi(base_ai.BaseAi):
    def choice(self, in_board, in_box):
        in_board = board.HiTechBoard(in_board) 
        in_box = box.Box(in_box)   

        randnum = np.random.randint( len(in_box.piecelist) )
        res_piece = in_box.piecelist[randnum]
        oddspieces = util.oddsPieces(in_board, in_box.piecelist)

        patternsize = len(oddspieces)
        if (patternsize != 0):
            randnum = np.random.randint( patternsize )
            res_piece = oddspieces[randnum]

        res_call = "Quarto" if in_board.isQuarto() else "Non"

        return {\
            'piece':res_piece.toDict(),\
            'call':res_call,\
        }
    
    def put(self, in_board, in_piece):
        in_board = board.HiTechBoard(in_board)
        in_piece = piece.Piece.getInstance(in_piece)
        
        in_box = box.Box(board=in_board)
        in_box.remove(in_piece)

        checkpattern = util.losePiecePos(in_board, in_box, in_piece)

        if ( not np.any(checkpattern) ):
            patternlist = np.where(in_board.onboard==None)
            
            randnum = np.random.randint(patternlist[0].size)
            res_column = patternlist[0][randnum]
            res_row = patternlist[1][randnum]
        else:
            patternlist = np.where(checkpattern)
            
            randnum = np.random.randint(patternlist[0].size)
            res_column = patternlist[0][randnum]
            res_row = patternlist[1][randnum]

        if(util.endPiece(in_board, in_piece)):
            res_column, res_row = util.endPiecePos(in_board, in_piece)

        in_board.setBoard(res_column,res_row,in_piece)
        res_call = "Quarto" if in_board.isQuarto() else "Non"

        return {\
            'call':res_call,\
            'column':res_column,\
            'row':res_row,\
        }
