def calculate_kelly(win_probability, win_odds, loss_probability=None):
    if loss_probability is None:
        loss_probability = 1 - win_probability

    b = win_odds
    p = win_probability
    q = loss_probability

    kelly_fraction = (b * p - q) / b
    return max(kelly_fraction, 0)

def ev_to_win_probability(ev):
    return (ev + 1) / 2

def simulate_hand_ev():
    # Placeholder EV calculation
    return 0.03  # Example EV for demonstration purposes

def main():
    print("Blackjack EV and Kelly Calculator (TUI)")

    while True:
        try:
            bankroll = float(input("Enter your bankroll ($): "))
            if bankroll <= 0:
                print("Please enter a positive bankroll.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    ev = simulate_hand_ev()
    win_probability = ev_to_win_probability(ev)
    kelly_fraction = calculate_kelly(win_probability, 1)  # 1:1 odds

    recommended_bet = kelly_fraction * bankroll

    print(f"\nEV: {ev:.4f}")
    print(f"Kelly Fraction: {kelly_fraction:.4f}")
    print(f"Recommended Bet: ${recommended_bet:.2f} ({kelly_fraction * 100:.2f}% of bankroll)")

if __name__ == "__main__":
    main()
