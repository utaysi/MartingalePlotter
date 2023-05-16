#Simulate many runs of "Rolls before bankruptcy" until a specific bet count. 
#This will show the odds of survival for the current betting strategy within the given amount of rolls. 

import random
from decimal import Decimal, getcontext

getcontext().prec = 4

def randomize():
    return random.randint(1, 2)

results = []
wincount = 0
resultBalances = []
# i = Chance Percentage
for i in range(0,100,1):
    balance = Decimal('10.0')
    initialbet = Decimal('0.10')
    bet = initialbet
    # i = Bet Count
    for i in range(0,500,1): 
        balance -= bet
        if randomize() == 1:
            #Win Multiplier
            balance += bet * Decimal('2')
            print('(' + str(i) + ') Bet ' + str(bet) + ': W, balance: ' + str(balance))
            bet = initialbet
        else:
            print('(' + str(i) + ') Bet ' + str(bet) + ': L, balance: ' + str(balance))
            bet = bet*2
        if (balance <= 0):
            print('BANKRUPT.')
            break
    if balance >= 0:
        wincount += 1
        resultBalances.append(balance)
    else:
        wincount -= 1
        resultBalances.append(balance)
    print(wincount)
print('Max Balance: ' + str(max(resultBalances)))
