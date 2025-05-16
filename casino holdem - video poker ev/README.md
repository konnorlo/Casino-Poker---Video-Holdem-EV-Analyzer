This is an EV analyzer for Stake.com's Casino Holdem - Video Poker 1 handed game.

Included are:
    1_hand.py - Text-based implementation of the game's EV calculator
    1_hand_gui.py - Graphics-based implementation of the game's EV calculator
    kelly_criterion.py - Calculates bet based on bankroll size per Kelly criterion

Dependencies:
	libraries: 
		treys
		pygame

To install these dependencies:
	pip install pygame
	pip install treys


To run these commands in terminal:
	for the text based implementation (TUI):
	/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 1_hand.py
	
	for the graphics based implementation (GUI):
	/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 1_hand_gui.py

    for Kelly Criterion:
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 kelly_criterion.py

Gamble responsibly.
Overall EV of this game is -0.035 * bet size per hand.
