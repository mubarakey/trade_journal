import json
import os
from datetime import date


def calculate_pnl(risk, result_r):
    return risk * result_r


def main():
    print("Welcome to the Trade PnL Journal!")
    journal()


def journal():
    today = date.today()
   #load trades
    if os.path.exists("trades.json"):
        with open("trades.json", "r") as file:
            trades = json.load(file)
    else:
        trades = []

    #a loop for asking user input
    while True:
        pair = input("Enter the currency pair: ")
        direction = input("BUY/SELL: ")
        risk = float(input("Enter the risk amount: "))
        result_r = float(input("Enter the result(r): "))
        
        trade = {
            "date": str(today),
            "pair": pair,
            "direction": direction,
            "risk": risk,
            "result_r": result_r
        }
        trades.append(trade)

        again = input("Add another trade? (y/n): ")
        if again.lower() != 'y':
            break

    
    #save all trades
    with open("trades.json", "w") as file:
        json.dump(trades, file, indent=4)

    print("Trades saved successfully!")

    total_profit= 0
    total_r = 0
    total_loss = 0
    breakevens = 0
    net_pnl = 0
    wins = 0
    losses = 0

    for i in trades:
        result = calculate_pnl(i["risk"], i["result_r"])
        total_r += i["result_r"]
        net_pnl += result

        if i["result_r"] > 0:
            total_profit += result
            wins += 1

        elif i["result_r"] == 0:
            breakevens +=1

        else:
            total_loss += result
            losses += 1

    total_trades = len(trades)

    print("\n----- TRADING SUMMARY -----")
    print(f"Total Trades: {total_trades}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Breakevens: {breakevens}")
    print(f"Profit: ${total_profit:.2f}")
    print(f"Loss: ${total_loss:.2f}")
    print(f"Total R: {total_r:.2f}R")
    print(f"Net PnL: ${net_pnl:.2f}")



if __name__ == "__main__":
    main()