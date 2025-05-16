from treys import Card, Evaluator
import random

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

def get_ante_payout(rank_class):
    # Payouts for the ANTE bet (from the image)
    return {
        1: 100,  # Royal Flush
        2: 20,   # Straight Flush
        3: 10,   # Four of a Kind
        4: 3,    # Full House
        5: 2,    # Flush
        6: 1     # Straight or less
    }.get(rank_class, 1)

def get_bonus_payout(rank_class, hero_cards, board):
    # Bonus bet payout table (from the image)
    if rank_class == 1:    # Royal Flush
        return 100
    elif rank_class == 2:  # Straight Flush
        return 50
    elif rank_class == 3:  # Four of a Kind
        return 40
    elif rank_class == 4:  # Full House
        return 30
    elif rank_class == 5:  # Flush
        return 20
    elif rank_class == 6:  # Straight
        return 7
    elif rank_class == 7:  # Three of a Kind
        return 7
    elif rank_class == 8:  # Pair (must be Aces)
        hand = hero_cards + board
        ranks = [Card.get_rank_int(c) for c in hand]
        if ranks.count(14) >= 2:
            return 7  # Pair of Aces to Straight
        else:
            return 0
    elif rank_class == 9:
        return 0
    return 0

def dealer_qualifies(board, dealer_hand, evaluator):
    score = evaluator.evaluate(board, dealer_hand)
    hand_class = evaluator.get_rank_class(score)
    # Pair or better
    if hand_class <= 8:
        hand = dealer_hand + board
        ranks = [Card.get_rank_int(c) for c in hand]
        for rank, count in {r: ranks.count(r) for r in set(ranks)}.items():
            # Only pairs of 4s (rank 2) or higher qualify (ranks: 0=2, 1=3, 2=4...)
            if count >= 2 and rank >= 2:
                return True
    return False

def hand_name(rank_class, hero_cards, board):
    names = {
        1: "Royal Flush",
        2: "Straight Flush",
        3: "Four of a Kind",
        4: "Full House",
        5: "Flush",
        6: "Straight",
        7: "Three of a Kind",
        8: "Pair",
        9: "High Card"
    }
    if rank_class == 8:
        ranks = [Card.get_rank_int(c) for c in hero_cards + board]
        if ranks.count(14) >= 2:
            return "Pair of Aces"
    return names[rank_class]

def simulate_hand(hero_cards, flop_cards, evaluator, deck):
    villain_cards = random.sample(deck, 2)
    remaining_deck = [c for c in deck if c not in villain_cards]
    turn_river = random.sample(remaining_deck, 2)
    board = flop_cards + turn_river

    hero_score = evaluator.evaluate(board, hero_cards)
    villain_score = evaluator.evaluate(board, villain_cards)
    hero_class = evaluator.get_rank_class(hero_score)
    villain_class = evaluator.get_rank_class(villain_score)

    villain_qualifies = dealer_qualifies(board, villain_cards, evaluator)
    ante_payout = get_ante_payout(hero_class)
    bonus_payout = get_bonus_payout(hero_class, hero_cards, board)
    # -1 unit ante, -2 units play, -1 unit bonus are always risked if bet

    # --- ANTE & PLAY handling (per standard rules) ---
    ante_result = -1   # Risked every hand
    play_result = -2   # Risked every hand if we CALL (always call in this sim)
    # We will return winnings by adding to these negative bases

    # Winning/tie/lose logic (note: treys lower score is better!)
    if hero_score < villain_score:  # Hero wins
        if villain_qualifies:
            ante_result += ante_payout + 1  # plus the original bet
            play_result += 2 + 2            # 1:1 on play plus original bet
        else:  # Dealer doesn't qualify: ante pays, play pushes
            ante_result += ante_payout + 1
            play_result += 2                # Just get play bet back (push)
    elif hero_score == villain_score:  # Tie (pushes all)
        ante_result += 1    # Just get ante back
        play_result += 2    # Just get play back
    else:  # Dealer wins
        if not villain_qualifies:
            ante_result += ante_payout + 1
            play_result += 2  # Push
        # else: lost both bets, already accounted for by -1 and -2

    # --- BONUS handling ---
    bonus_result = -1
    if bonus_payout > 0:
        bonus_result += bonus_payout + 1  # plus original bet
    else:
        bonus_result += 0  # just lose the bonus bet

    return ante_result, play_result, bonus_result, hero_class, hand_name(hero_class, hero_cards, board)

def casino_holdem_simulation(hero_str, flop_str, simulations=10000):
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

    total_ante_net = 0
    total_play_net = 0
    total_bonus_net = 0

    hand_frequencies = {
        "Royal Flush": 0,
        "Straight Flush": 0,
        "Four of a Kind": 0,
        "Full House": 0,
        "Flush": 0,
        "Straight": 0,
        "Three of a Kind": 0,
        "Two Pair": 0,
        "Pair": 0,
        "Pair of Aces": 0,
        "High Card": 0
    }

    call_wins = 0
    call_pushes = 0
    call_losses = 0
    bonus_win_count = 0
    bonus_win_amount = 0

    for _ in range(simulations):
        ante_result, play_result, bonus_result, hero_class, hand_name_str = simulate_hand(hero_cards, flop_cards, evaluator, deck)
        total_ante_net += ante_result
        total_play_net += play_result
        total_bonus_net += bonus_result

        # Classify hand frequencies
        if hand_name_str in hand_frequencies:
            hand_frequencies[hand_name_str] += 1
        elif hand_name_str == "Pair of Aces":
            hand_frequencies["Pair of Aces"] += 1

        # Call outcome stats
        if ante_result + play_result > 0:
            call_wins += 1
        elif ante_result + play_result == 0:
            call_pushes += 1
        else:
            call_losses += 1

        # Bonus stats
        if bonus_result > 0:
            bonus_win_count += 1
            bonus_win_amount += bonus_result

    avg_ante_net = total_ante_net / simulations
    avg_play_net = total_play_net / simulations
    avg_bonus_net = total_bonus_net / simulations

    call_ev_with_bonus = avg_ante_net + avg_play_net + avg_bonus_net
    call_ev_without_bonus = avg_ante_net + avg_play_net
    fold_ev_without_bonus = -1  # Always lose ante
    fold_ev_with_bonus = -1 + avg_bonus_net  # Lose ante, resolve bonus

    bonus_hit_rate = (bonus_win_count / simulations) * 100
    bonus_average_win = bonus_win_amount / bonus_win_count if bonus_win_count > 0 else 0

    hand_percentages = {hand: (count / simulations) * 100 for hand, count in hand_frequencies.items()}

    win_percentage = call_wins / simulations * 100
    push_percentage = call_pushes / simulations * 100
    loss_percentage = call_losses / simulations * 100

    return {
        'ante_ev': avg_ante_net,
        'play_ev': avg_play_net,
        'bonus_ev': avg_bonus_net,
        'call_ev_with_bonus': call_ev_with_bonus,
        'call_ev_without_bonus': call_ev_without_bonus,
        'fold_ev_with_bonus': fold_ev_with_bonus,
        'fold_ev_without_bonus': fold_ev_without_bonus,
        'bonus_hit_rate': bonus_hit_rate,
        'bonus_average_win': bonus_average_win,
        'hand_percentages': hand_percentages,
        'win_pct': win_percentage,
        'push_pct': push_percentage,
        'loss_pct': loss_percentage,
        'recommendation': 'CALL' if call_ev_with_bonus > fold_ev_with_bonus else 'FOLD',
        'bonus_recommendation': 'PLACE BONUS BET' if avg_bonus_net > -1 else 'SKIP BONUS BET'
    }

def main():
    try:
        hero_str = input("Enter your two hole cards (e.g., 'As Kd'):\n")
        flop_str = input("Enter the three flop cards (e.g., '2c Jh 9s'):\n")

        print("Running simulations... (this may take a few seconds)")
        results = casino_holdem_simulation(hero_str, flop_str)

        print("\n--- Casino Hold'em Simulation Results ---")
        print("\nExpected Values (per unit wagered):")
        print(f"EV from Ante bet:          {results['ante_ev']:.4f} units")
        print(f"EV from Play bet:          {results['play_ev']:.4f} units")
        print(f"EV from Bonus bet:         {results['bonus_ev']:.4f} units")

        print("\nStrategy Options:")
        print(f"EV if Call with Bonus:     {results['call_ev_with_bonus']:.4f} units")
        print(f"EV if Call without Bonus:  {results['call_ev_without_bonus']:.4f} units")
        print(f"EV if Fold with Bonus:     {results['fold_ev_with_bonus']:.4f} units")
        print(f"EV if Fold without Bonus:  {results['fold_ev_without_bonus']:.4f} units")

        print("\nBonus Bet Analysis:")
        print(f"Bonus Hit Rate:            {results['bonus_hit_rate']:.2f}%")
        print(f"Average Bonus Win:         {results['bonus_average_win']:.2f} units")

        print("\nOutcome Frequencies:")
        print(f"Win percentage:            {results['win_pct']:.2f}%")
        print(f"Push percentage:           {results['push_pct']:.2f}%")
        print(f"Loss percentage:           {results['loss_pct']:.2f}%")

        print("\nHand Frequencies:")
        for hand, percentage in sorted(results['hand_percentages'].items(), 
                                       key=lambda x: (
                                           0 if x[0] == "Royal Flush" else
                                           1 if x[0] == "Straight Flush" else
                                           2 if x[0] == "Four of a Kind" else
                                           3 if x[0] == "Full House" else
                                           4 if x[0] == "Flush" else
                                           5 if x[0] == "Straight" else
                                           6 if x[0] == "Three of a Kind" else
                                           7 if x[0] == "Two Pair" else
                                           8 if x[0] == "Pair of Aces" else
                                           9 if x[0] == "Pair" else
                                           10)):
            if percentage > 0:
                print(f"  {hand + ':':20} {percentage:.2f}%")

        print("\nRecommendations:")
        print(f"Main Game: {results['recommendation']}")
        print(f"Bonus Bet: {results['bonus_recommendation']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
