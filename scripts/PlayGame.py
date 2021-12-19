#!/usr/bin/env python3

import os, sys
pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pardir)

from src.gamesys import gamemain

if __name__ == "__main__":
    num = 1
    gamemain.winningPercentageRun(num)

