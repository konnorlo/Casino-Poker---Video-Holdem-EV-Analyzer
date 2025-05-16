from treys import Card, Deck, Evaluator
import random

#   to use this bot:
#   instructions are included
#   first type in 2 of your cards
#   then type in flop
#   boom ev  
# 
#   run with
#
#   /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 1_hand.py

def print_card(card):
    """Debug function to print a card in readable format"""
    return Card.int_to_str(card)

def parse_card(card_str):
    """Parse a string like 'As' into a card integer"""
    if len(card_str) != 2:
        raise ValueError(f"Invalid card format: {card_str}")
    
    rank = card_str[0].upper()
    suit = card_str[1].lower()
    
    # Validate rank and suit
    if rank not in "23456789TJQKA":
        raise ValueError(f"Invalid rank in card: {card_str}")
    if suit not in "shdc":
        raise ValueError(f"Invalid suit in card: {card_str}")
    
    # Create card integer
    card_int = Card.new(card_str)
    return card_int

def create_deck_without_cards(excluded_cards):
    """Create a deck excluding specific cards"""
    full_deck = []
    # Generate all 52 cards
    for rank in "23456789TJQKA":
        for suit in "shdc":
            card_str = f"{rank}{suit}"
            card = Card.new(card_str)
            if card not in excluded_cards:
                full_deck.append(card)
    return full_deck

def simulate_hand(hero_cards, flop_cards, evaluator, deck):
    """Simulate a single hand and return the result"""
    # Deal villain's cards
    villain_cards = random.sample(deck, 2)
    remaining_deck = [c for c in deck if c not in villain_cards]
    
    # Deal turn and river
    turn_river = random.sample(remaining_deck, 2)
    board = flop_cards + turn_river
    
    # Evaluate hands (lower score is better in treys)
    try:
        hero_score = evaluator.evaluate(board, hero_cards)
        villain_score = evaluator.evaluate(board, villain_cards)
        
        if hero_score < villain_score:
            return "win"
        elif hero_score == villain_score:
            return "tie"
        else:
            return "loss"
    except Exception as e:
        print(f"Error evaluating hand: {e}")
        print(f"Hero cards: {[print_card(c) for c in hero_cards]}")
        print(f"Villain cards: {[print_card(c) for c in villain_cards]}")
        print(f"Board: {[print_card(c) for c in board]}")
        raise e

def casino_holdem_simulation(hero_str, flop_str, simulations=10000):
    """Run a Casino Hold'em simulation and return the results"""
    try:
        # Parse the input strings into card objects
        hero_cards = [parse_card(c) for c in hero_str.split()]
        flop_cards = [parse_card(c) for c in flop_str.split()]
        
        # Check correct number of cards
        if len(hero_cards) != 2:
            raise ValueError(f"Expected 2 hero cards, got {len(hero_cards)}")
        if len(flop_cards) != 3:
            raise ValueError(f"Expected 3 flop cards, got {len(flop_cards)}")
        
        # Check for duplicate cards
        all_cards = hero_cards + flop_cards
        card_strs = [Card.int_to_str(c) for c in all_cards]
        if len(set(card_strs)) != len(card_strs):
            raise ValueError("Duplicate cards detected")
        
        # Initialize the evaluator
        evaluator = Evaluator()
        
        # Create a deck without the known cards
        deck = create_deck_without_cards(all_cards)
        
        # Run simulations
        wins = ties = losses = 0
        
        for i in range(simulations):
            result = simulate_hand(hero_cards, flop_cards, evaluator, deck)
            if result == "win":
                wins += 1
            elif result == "tie":
                ties += 1
            elif result == "loss":
                losses += 1
        
        # Calculate probabilities
        total = wins + ties + losses
        win_prob = wins / total
        tie_prob = ties / total
        loss_prob = losses / total
        
        # Calculate expected values for Casino Hold'em
        # EV if you call: win = +3, tie = 0, lose = -3
        call_ev = win_prob * 3 + tie_prob * 0 + loss_prob * (-3)
        # EV of folding = lose ante (-1)
        fold_ev = -1
        
        return {
            'win_probability': win_prob,
            'tie_probability': tie_prob,
            'loss_probability': loss_prob,
            'call_ev': call_ev,
            'fold_ev': fold_ev,
            'recommendation': 'CALL' if call_ev > fold_ev else 'FOLD'
        }
    
    except Exception as e:
        print(f"Simulation error: {e}")
        raise e

def main():
    try:
        # Get user input
        hero_str = input("Enter your two hole cards (e.g., 'As Kd'):\n")
        flop_str = input("Enter the three flop cards (e.g., '2c Jh 9s'):\n")
        
        print("Running simulations... (this may take a few seconds)")
        results = casino_holdem_simulation(hero_str, flop_str)
        
        # Print results
        print("\n--- Results ---")
        print(f"Win probability: {results['win_probability']:.4f}")
        print(f"Tie probability: {results['tie_probability']:.4f}")
        print(f"Loss probability: {results['loss_probability']:.4f}")
        print(f"EV of calling (3x raise): {results['call_ev']:.4f}")
        print(f"EV of folding: {results['fold_ev']:.4f}")
        print(f"\nRecommendation: {results['recommendation']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()


###
#     run with /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 1_hand.py
#     yeah thats it
# 
# 
# 
# 
#  
