from ..brain import base_ai
from ..gameobject import board, box, piece

class GamePlayer:
    def __init__(self, ai=None):
        self.ai = ai
        if ai is None: self.ai = ManualAI()
    
    def choice(self, board, box):
        return self.ai.choice(board, box)

    def put(self, board, piece):
        return self.ai.put(board,piece)

class ManualAI(base_ai.BaseAi):
    def choice(self, in_board, in_box):
        in_board = board.HiTechBoard(in_board)
        in_box = box.Box(in_box)

        boxpiecenum = len(in_box.piecelist)
        box_index = None

        while(box_index is None):
            in_str = [int(i) for i in input("choice >>").split()]
            if not(0 <= in_str[0] and in_str[0] < boxpiecenum ):continue
            box_index = in_str[0]

        res_call = "Quarto" if in_board.isQuarto() else "Non"

        return {\
                'piece':in_box.piecelist[box_index].toDict(),\
                'call':res_call,\
                }

    def put(self, in_board, in_piece):
        in_board = board.HiTechBoard(in_board)
        in_piece = piece.Piece.getInstance(in_piece)

        res_column = None
        res_row = None

        while(res_column is None):
            in_str = [int(i) for i in input('put(column, row) >>').split()]
            if not (0 <= in_str[0] and in_str[0] <= 3 and \
                    0 <= in_str[1] and in_str[1] <= 3): continue

            if(in_board.getBoard(in_str[0],in_str[1]) is not None): continue

            res_column = in_str[0]
            res_row    = in_str[1]

        in_board.setBoard(res_column, res_row, in_piece)
        res_call = "Quarto" if in_board.isQuarto() else "Non"

        return{'call':res_call,\
               'column':res_column,\
               'row':res_row,\
                }
