# Plots graphs and statistics for Martingale Strategy simulations.

import random
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import argparse
import statistics # For calculating average

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

def run_multiple_simulations(num_runs, initial_balance, initial_bet, choice, max_rolls, plot_last_run):
    """Runs multiple simulations, prints statistics, and optionally plots the last run using Matplotlib."""
    results = []
    print(f"\n--- Running {num_runs} Simulation(s) ---")
    print(f"Parameters: Initial Balance=${initial_balance:.2f}, Initial Bet=${initial_bet:.2f}, Choice={choice}, Max Rolls Per Run={max_rolls}")

    for i in range(num_runs):
        # Only print details for the first run if verbose is needed (i.e., when plotting)
        run_result = martingale_bot(initial_balance, initial_bet, choice, max_rolls, verbose=(i == num_runs - 1 and plot_last_run))
        results.append(run_result)
        # Simple progress indicator for multiple runs
        if num_runs > 1 and (i + 1) % (num_runs // 10 if num_runs >= 10 else 1) == 0:
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

    # --- Optional Plotting of Last Run (using Matplotlib) ---
    if plot_last_run and num_runs > 0:
        last_run = results[-1] # Plot the actual last run
        print("\n--- Plotting Last Simulation Run (using Matplotlib) ---")
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
            print("Last run had no rolls, skipping Matplotlib plot.")


def run_parameter_scan(balance_start, balance_end, balance_step,
                       bet_start, bet_end, bet_step,
                       runs_per_combo, choice, max_rolls):
    """
    Runs simulations across ranges of initial balance and initial bet.
    Generates an interactive 3D plot of the average final balance using Plotly.
    """
    balances = np.arange(balance_start, balance_end + balance_step, balance_step)
    bets = np.arange(bet_start, bet_end + bet_step, bet_step)

    # Ensure ranges are not empty
    if len(balances) == 0 or len(bets) == 0:
        print("Error: Balance or Bet range resulted in zero values. Check start/end/step.")
        return

    print(f"\n--- Running Parameter Scan ---")
    print(f"Balance Range: ${balance_start:.2f} to ${balance_end:.2f} (step ${balance_step:.2f})")
    print(f"Bet Range: ${bet_start:.2f} to ${bet_end:.2f} (step ${bet_step:.2f})")
    print(f"Runs per Combination: {runs_per_combo}")
    print(f"Betting Choice: {choice}")
    print(f"Max Rolls per Run: {max_rolls}")

    # Store results for plotting
    scan_balances = []
    scan_bets = []
    avg_final_balances = []

    total_combos = len(balances) * len(bets)
    completed_combos = 0

    for bal in balances:
        for bet_val in bets:
            # Skip combinations where initial balance is less than initial bet
            if bal < bet_val:
                continue

            combo_final_balances = []
            for _ in range(runs_per_combo):
                # Run simulation for this specific (bal, bet_val) combo
                # Suppress verbose output from individual runs during scan
                result = martingale_bot(bal, bet_val, choice, max_rolls, verbose=False)
                combo_final_balances.append(result['final_balance'])

            # Calculate average final balance for this combo
            avg_bal = statistics.mean(combo_final_balances) if combo_final_balances else 0

            # Store results
            scan_balances.append(bal)
            scan_bets.append(bet_val)
            avg_final_balances.append(avg_bal)

            completed_combos += 1
            if completed_combos % 10 == 0 or completed_combos == total_combos: # Progress update
                 print(f"  Completed {completed_combos}/{total_combos} parameter combinations...")


    if not scan_balances:
        print("\nNo valid parameter combinations found to plot (e.g., balance < bet for all).")
        return

    # --- Create 3D Plot with Plotly ---
    print("\nGenerating 3D plot...")
    fig = go.Figure(data=[go.Scatter3d(
        x=scan_balances,
        y=scan_bets,
        z=avg_final_balances,
        mode='markers',
        marker=dict(
            size=5,
            color=avg_final_balances, # Color points by the Z value (average final balance)
            colorscale='Viridis',     # Choose a colorscale
            opacity=0.8,
            colorbar=dict(title='Avg Final Balance ($)')
        )
    )])

    fig.update_layout(
        title=f'Martingale Scan: Avg Final Balance vs. Initial Params<br>(Choice={choice}, Runs/Combo={runs_per_combo}, Max Rolls={max_rolls})',
        scene=dict(
            xaxis_title='Initial Balance ($)',
            yaxis_title='Initial Bet ($)',
            zaxis_title='Average Final Balance ($)'
        ),
        margin=dict(l=0, r=0, b=0, t=40) # Adjust margins
    )

    # Save plot as HTML
    plot_filename = "martingale_scan_3d.html"
    fig.write_html(plot_filename)
    print(f"\nInteractive 3D plot saved as: {plot_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Martingale strategy simulations or parameter scans.')

    # General arguments
    parser.add_argument('--choice', type=str, default='T', choices=['T', 'CT', 'Ace'], help='Betting choice.')
    parser.add_argument('--max_rolls', type=int, default=10000, help='Maximum rolls per simulation run.')

    # Mode selection
    parser.add_argument('--mode', type=str, default='run', choices=['run', 'scan'], help='Operation mode: "run" single/multiple simulations, "scan" parameter space.')

    # Arguments for 'run' mode
    parser.add_argument('--balance', type=float, default=20, help='Initial balance (for run mode).')
    parser.add_argument('--bet', type=float, default=0.1, help='Initial bet amount (for run mode).')
    parser.add_argument('--num_runs', type=int, default=1, help='Number of simulations to run (for run mode).')
    parser.add_argument('--plot_last', action='store_true', help='Plot balance history of the last run using Matplotlib (for run mode).')

    # Arguments for 'scan' mode
    parser.add_argument('--balance_start', type=float, default=2.0, help='Starting initial balance for scan.')
    parser.add_argument('--balance_end', type=float, default=20.0, help='Ending initial balance for scan.')
    parser.add_argument('--balance_step', type=float, default=1.0, help='Step size for balance scan.')
    parser.add_argument('--bet_start', type=float, default=0.05, help='Starting initial bet for scan.')
    parser.add_argument('--bet_end', type=float, default=1.0, help='Ending initial bet for scan.')
    parser.add_argument('--bet_step', type=float, default=0.05, help='Step size for bet scan.')
    parser.add_argument('--runs_per_combo', type=int, default=50, help='Number of runs for each parameter combination in scan mode.')

    args = parser.parse_args()

    if args.mode == 'run':
        # Default plotting behavior for single run
        if args.num_runs == 1 and not args.plot_last:
            args.plot_last = True

        run_multiple_simulations(
            num_runs=args.num_runs,
            initial_balance=args.balance,
            initial_bet=args.bet,
            choice=args.choice,
            max_rolls=args.max_rolls,
            plot_last_run=args.plot_last
        )
    elif args.mode == 'scan':
        run_parameter_scan(
            balance_start=args.balance_start,
            balance_end=args.balance_end,
            balance_step=args.balance_step,
            bet_start=args.bet_start,
            bet_end=args.bet_end,
            bet_step=args.bet_step,
            runs_per_combo=args.runs_per_combo,
            choice=args.choice,
            max_rolls=args.max_rolls
        )
