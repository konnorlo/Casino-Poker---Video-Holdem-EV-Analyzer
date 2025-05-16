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
    return Card.int_to_str(card)

def parse_card(card_str):
    if len(card_str) != 2:
        raise ValueError(f"Invalid card format: {card_str}")
    rank = card_str[0].upper()
    suit = card_str[1].lower()
    if rank not in "23456789TJQKA" or suit not in "shdc":
        raise ValueError(f"Invalid card: {card_str}")
    return Card.new(card_str)

def create_deck_without_cards(excluded_cards):
    full_deck = []
    for rank in "23456789TJQKA":
        for suit in "shdc":
            card_str = f"{rank}{suit}"
            card = Card.new(card_str)
            if card not in excluded_cards:
                full_deck.append(card)
    return full_deck

def get_ante_bonus_payout(rank_class):
    # Updated payouts according to the rules in the image
    ante_payouts = {
        1: 100,  # Royal Flush (100:1)
        2: 20,   # Straight Flush (20:1)
        3: 10,   # Four of a Kind (10:1)
        4: 3,    # Full House (3:1)
        5: 2,    # Flush (2:1)
        6: 1     # Straight or less (1:1)
    }
    bonus_payouts = {
        1: 100,  # Royal Flush (100:1)
        2: 50,   # Straight Flush (50:1)
        3: 40,   # Four of a Kind (40:1)
        4: 30,   # Full House (30:1)
        5: 20,   # Flush (20:1)
        6: 7,    # Straight (7:1)
        7: 7,    # Three of a Kind (7:1)
        8: 7     # Two Pair (7:1)
        # Pair of Aces is not on the bonus payout table, so it would be 0
    }
    return ante_payouts.get(rank_class, 1), bonus_payouts.get(rank_class, 0)

def dealer_qualifies(board, dealer_hand, evaluator):
    # Dealer qualifies with pair of 4s or better
    full_score = evaluator.evaluate(board, dealer_hand)
    hand_class = evaluator.get_rank_class(full_score)
    
    if hand_class <= 8:  # Pair or better
        hand = dealer_hand + board
        ranks = [Card.get_rank_int(c) for c in hand]
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        
        # Check if the pair is 4 or higher
        for rank, count in rank_counts.items():
            if count >= 2 and rank >= 2:  # 2 = card rank 4 in treys lib (2-14 scale with 2=4, 14=Ace)
                return True
    
    return False

def simulate_hand(hero_cards, flop_cards, evaluator, deck):
    villain_cards = random.sample(deck, 2)
    remaining_deck = [c for c in deck if c not in villain_cards]
    turn_river = random.sample(remaining_deck, 2)
    board = flop_cards + turn_river

    hero_score = evaluator.evaluate(board, hero_cards)
    villain_score = evaluator.evaluate(board, villain_cards)
    hero_class = evaluator.get_rank_class(hero_score)
    villain_qualifies = dealer_qualifies(board, villain_cards, evaluator)

    ante_payout, bonus_payout = get_ante_bonus_payout(hero_class)

    # Bonus only paid for Straight or better (i.e. class <= 6) 
    # or for specifically paired aces
    bonus = 0
    if hero_class <= 6:
        bonus = bonus_payout
    elif hero_class == 8:  # Pair
        hand = hero_cards + board
        ranks = [Card.get_rank_int(c) for c in hand]
        if ranks.count(14) >= 2:  # Check for pair of Aces (rank 14)
            bonus = 7  # Pair of Aces pays 7:1 on bonus

    # Default: no payout
    ante = -1  # Always lose ante if fold
    play = -2  # Play is 2x the ante

    if hero_score < villain_score:  # Lower score is better in treys
        # Hero wins
        ante = ante_payout
        play = 2
    elif hero_score == villain_score:
        # Tie
        ante = 1  # Push on ante (1:1)
        play = 0  # Push on play
    else:
        # Hero loses
        if not villain_qualifies:
            ante = 1  # Push on ante (1:1)
            play = 0  # Push on play

    return ante, play, bonus


def casino_holdem_simulation(hero_str, flop_str, simulations=10000):
    try:
        hero_cards = [parse_card(c) for c in hero_str.split()]
        flop_cards = [parse_card(c) for c in flop_str.split()]
        if len(hero_cards) != 2 or len(flop_cards) != 3:
            raise ValueError("Enter 2 hole cards and 3 flop cards.")

        all_cards = hero_cards + flop_cards
        card_strs = [Card.int_to_str(c) for c in all_cards]
        if len(set(card_strs)) != len(card_strs):
            raise ValueError("Duplicate cards detected.")

        evaluator = Evaluator()
        deck = create_deck_without_cards(all_cards)

        total_ante = 0
        total_play = 0
        total_bonus = 0

        for _ in range(simulations):
            ante, play, bonus = simulate_hand(hero_cards, flop_cards, evaluator, deck)
            total_ante += ante
            total_play += play
            total_bonus += bonus

        avg_ante = total_ante / simulations
        avg_play = total_play / simulations
        avg_bonus = total_bonus / simulations

        call_ev = avg_ante + avg_play + avg_bonus
        fold_ev = -1  # always lose ante

        return {
            'ante_ev': avg_ante,
            'play_ev': avg_play,
            'bonus_ev': avg_bonus,
            'call_ev': call_ev,
            'fold_ev': fold_ev,
            'recommendation': 'CALL' if call_ev > fold_ev else 'FOLD'
        }

    except Exception as e:
        print(f"Simulation error: {e}")
        raise e

def main():
    try:
        hero_str = input("Enter your two hole cards (e.g., 'As Kd'):\n")
        flop_str = input("Enter the three flop cards (e.g., '2c Jh 9s'):\n")

        print("Running simulations... (this may take a few seconds)")
        results = casino_holdem_simulation(hero_str, flop_str)

        print("\n--- Simulation Results ---")
        print(f"EV from Ante payout:  {results['ante_ev']:.4f}")
        print(f"EV from Play decision: {results['play_ev']:.4f}")
        print(f"EV from Bonus payout: {results['bonus_ev']:.4f}")
        print(f"Total EV if Call:      {results['call_ev']:.4f}")
        print(f"Total EV if Fold:      {results['fold_ev']:.4f}")
        print(f"\nRecommendation: {results['recommendation']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

