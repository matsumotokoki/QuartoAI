#!/usr/bin/env python3

import os, sys
pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pardir)

from src.gamesys import gamemain
import rospy

def main():
    num = 1
    rospy.init_node('play_game_node', anonymous=True)
    gamemain.winningPercentageRun(num)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException: pass

