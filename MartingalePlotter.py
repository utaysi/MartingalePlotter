#Plots a graph of a single run of rolls using the Martingale Strategy. 

import random
import matplotlib.pyplot as plt

def play_roulette(bet, choice):
    # Generate a random float between 0 and 1
    result = random.random()
    
    # Check which result we got based on probabilities
    if result < 7/15:
        result_choice = 'T'
    elif result < 14/15:
        result_choice = 'CT'
    else:
        result_choice = 'Ace'
        
    # If the bet choice matches the result, return the multiplier for that result
    if choice == result_choice:
        return 2 if choice in ['T', 'CT'] else 14
    else:
        return 0

def martingale_bot():
    lose_count = 0
    choice = 'T' # You can change this to 'CT' or 'Ace'
    initial_balance = 20
    balance = initial_balance
    initial_bet = 0.1
    bet = initial_bet
    roll_count = 0
    balance_results =[]

    while balance > bet:
        multiplier = play_roulette(bet, choice)
        roll_count +=1
        if multiplier:
            win_amount = bet * (multiplier - 1)
            balance += win_amount
            bet = initial_bet
            lose_count = 0
            balance_results.append(balance)
            print(f"Won {win_amount}! New balance: {balance:.2f}")

        else:
            balance -= bet
            bet *= 2
            lose_count += 1
            balance_results.append(balance)
            print(f"Lost! New balance: {balance:.2f}")
    print('---\nLose streak: ' + str(lose_count))
    print('Roll count: ' + str(roll_count))
    print('Max reached: ' + str(max(balance_results)))
    # Plotting the balance results
    plt.plot(balance_results)
    plt.title('------ Base bet: {} & Initial Balance: {} ------\nTotal Rolls: {}\nLose Streak Before Bankruptcy: {}\nMax reached: {:.2f}'.format(initial_bet, initial_balance, roll_count, lose_count,  max(balance_results)))
    plt.xlabel('Roll Count')
    plt.ylabel('Balance')
    plt.tight_layout()
    plt.show()

martingale_bot()

