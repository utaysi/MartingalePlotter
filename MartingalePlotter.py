#Plots a graph of a single run of rolls using the Martingale Strategy. 

import random
import matplotlib.pyplot as plt
import argparse

# --- Game Probabilities and Payouts ---
PROB_T = 7/15
PROB_CT = 7/15 # Calculated as (14/15) - (7/15)
PROB_ACE = 1/15 # Calculated as 1 - (14/15)

PAYOUT_T = 2
PAYOUT_CT = 2
PAYOUT_ACE = 14
# -------------------------------------

def play_roulette(choice):
    """Simulates a single round based on predefined probabilities."""
    # Generate a random float between 0 and 1
    result = random.random()

    # Determine the outcome based on probabilities
    if result < PROB_T:
        result_choice = 'T'
    elif result < PROB_T + PROB_CT:
        result_choice = 'CT'
    else:
        result_choice = 'Ace'

    # Return the payout multiplier if the choice matches the result
    if choice == result_choice:
        if choice == 'T':
            return PAYOUT_T
        elif choice == 'CT':
            return PAYOUT_CT
        else: # Ace
            return PAYOUT_ACE
    else:
        # Loss
        return 0

def martingale_bot(initial_balance, initial_bet, choice, max_rolls=10000, verbose=False):
    """
    Runs a single Martingale simulation run.
    Returns a dictionary with simulation results.
    """
    lose_count = 0
    balance = float(initial_balance)
    bet = float(initial_bet)
    roll_count = 0
    balance_history = [balance] # Start with initial balance
    bankrupted = False

    if verbose:
        print(f"Starting run: Balance=${balance:.2f}, Bet=${bet:.2f}, Choice={choice}")

    if balance < bet:
        if verbose:
            print("Initial balance less than initial bet.")
        return {
            "final_balance": balance, "roll_count": 0, "max_balance": balance,
            "bankrupted": True, "balance_history": balance_history, "lose_streak": 0
        }

    while balance >= bet and roll_count < max_rolls:
        multiplier = play_roulette(choice)
        roll_count += 1

        if multiplier > 0: # Win condition
            win_amount = bet * (multiplier - 1) # Net win
            balance += bet * multiplier # Add gross winnings
            if verbose:
                print(f"  Roll {roll_count}: Won {win_amount:.2f}! Bet={bet:.2f}. Bal={balance:.2f}")
            bet = initial_bet # Reset bet
            lose_count = 0
        else: # Loss condition
            if verbose:
                print(f"  Roll {roll_count}: Lost! Bet={bet:.2f}. Bal before={balance:.2f}")
            balance -= bet
            lose_count += 1
            bet *= 2 # Double bet
            if verbose:
                print(f"  New balance: {balance:.2f}. Next bet: {bet:.2f}")

        balance_history.append(balance)

        if balance < bet:
            bankrupted = True
            if verbose:
                print(f"  Bankrupt: Balance ({balance:.2f}) < Next Bet ({bet:.2f})")
            break

    if roll_count >= max_rolls:
         if verbose:
            print(f"  Reached max rolls ({max_rolls}).")


    max_balance = max(balance_history) if balance_history else initial_balance
    return {
        "final_balance": balance,
        "roll_count": roll_count,
        "max_balance": max_balance,
        "bankrupted": bankrupted,
        "balance_history": balance_history, # Keep history for potential plotting
        "lose_streak": lose_count # Streak at the end
    }

def run_multiple_simulations(num_runs, initial_balance, initial_bet, choice, max_rolls=10000, plot_last_run=False):
    """Runs multiple simulations and prints statistics."""
    results = []
    print(f"Running {num_runs} simulations...")
    print(f"Parameters: Initial Balance=${initial_balance:.2f}, Initial Bet=${initial_bet:.2f}, Choice={choice}, Max Rolls={max_rolls}")

    for i in range(num_runs):
        # Only print details for the first run if verbose is needed, or none
        run_result = martingale_bot(initial_balance, initial_bet, choice, max_rolls, verbose=(i==0 and plot_last_run)) # Verbose only for first run if plotting
        results.append(run_result)
        # Simple progress indicator
        if (i + 1) % (num_runs // 10 if num_runs >= 10 else 1) == 0:
            print(f"  Completed {i + 1}/{num_runs} runs...")

    # --- Calculate Statistics ---
    total_rolls = sum(r['roll_count'] for r in results)
    bankrupt_count = sum(1 for r in results if r['bankrupted'])
    final_balances = [r['final_balance'] for r in results]
    max_balances = [r['max_balance'] for r in results]

    avg_rolls = total_rolls / num_runs if num_runs > 0 else 0
    bankruptcy_rate = (bankrupt_count / num_runs) * 100 if num_runs > 0 else 0
    avg_final_balance = sum(final_balances) / num_runs if num_runs > 0 else 0
    avg_max_balance = sum(max_balances) / num_runs if num_runs > 0 else 0

    print("\n--- Overall Simulation Statistics ---")
    print(f"Number of Runs: {num_runs}")
    print(f"Average Roll Count: {avg_rolls:.2f}")
    print(f"Bankruptcy Rate: {bankruptcy_rate:.2f}% ({bankrupt_count}/{num_runs})")
    print(f"Average Final Balance: ${avg_final_balance:.2f}")
    print(f"Average Max Balance Reached: ${avg_max_balance:.2f}")

    # --- Optional Plotting of Last Run ---
    if plot_last_run and num_runs > 0:
        last_run = results[-1]
        print("\n--- Plotting Last Simulation Run ---")
        balance_history = last_run['balance_history']
        roll_count = last_run['roll_count']
        final_balance = last_run['final_balance']
        max_balance = last_run['max_balance']
        lose_streak = last_run['lose_streak']

        if roll_count > 0:
            plt.figure(figsize=(12, 7)) # Slightly larger plot
            plt.plot(range(roll_count + 1), balance_history)
            plt.title(f'Martingale Simulation (Last Run): Bal=${initial_balance:.2f}, Bet=${initial_bet:.2f}, Choice={choice}')
            plt.xlabel('Roll Count')
            plt.ylabel('Balance ($)')
            plt.grid(True, linestyle='--', alpha=0.7)

            stats_text = (
                f"Run Parameters:\n"
                f"  Initial Bal: ${initial_balance:.2f}\n"
                f"  Initial Bet: ${initial_bet:.2f}\n"
                f"  Choice: {choice}\n"
                f"Run Results:\n"
                f"  Total Rolls: {roll_count}\n"
                f"  Final Balance: ${final_balance:.2f}\n"
                f"  Max Balance: ${max_balance:.2f}\n"
                f"  Ending Streak: {lose_streak}\n"
                f"  Bankrupted: {'Yes' if last_run['bankrupted'] else 'No'}"
            )
            plt.text(0.98, 0.98, stats_text, transform=plt.gca().transAxes, fontsize=9,
                     verticalalignment='top', horizontalalignment='right',
                     bbox=dict(boxstyle='round,pad=0.5', fc='lightblue', alpha=0.8))

            plt.tight_layout(rect=[0, 0, 0.95, 0.96]) # Adjust layout
            plt.show()
        else:
            print("Last run had no rolls, skipping plot.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Martingale strategy simulations.')
    parser.add_argument('--balance', type=float, default=20, help='Initial balance.')
    parser.add_argument('--bet', type=float, default=0.1, help='Initial bet amount.')
    parser.add_argument('--choice', type=str, default='T', choices=['T', 'CT', 'Ace'], help='Betting choice.')
    parser.add_argument('--num_runs', type=int, default=1, help='Number of simulations to run.')
    parser.add_argument('--max_rolls', type=int, default=10000, help='Maximum rolls per simulation.')
    parser.add_argument('--plot_last', action='store_true', help='Plot the balance history of the last simulation run.')

    args = parser.parse_args()

    if args.num_runs == 1 and not args.plot_last:
        # If only one run is requested, behave like the old script and plot it by default
        args.plot_last = True

    run_multiple_simulations(
        num_runs=args.num_runs,
        initial_balance=args.balance,
        initial_bet=args.bet,
        choice=args.choice,
        max_rolls=args.max_rolls,
        plot_last_run=args.plot_last
    )
