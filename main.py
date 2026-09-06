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

    #auto add of trade id
   
    if trades:
        trade_id = trades[-1]["id"] + 1
    else:
        trade_id = 1


    #a loop for asking user input
    while True:
        pair = input("Enter the currency pair: ")
        direction = input("BUY/SELL: ")
        risk = float(input("Enter the risk amount: "))
        result_r = float(input("Enter the result(r): "))
        setup = input("Enter setup: ")
        liquidity_sweep = input("Liquidity sweep? (y/n): ")
        bos = input("Break of Structure? (y/n): ")
        structural_liquidity = input("Structural liquidity? (y/n): ")
        poi = input("Valid POI? (y/n): ")
        
       
        trade = {
            "id": trade_id,
            "date": str(today),
            "pair": pair,
            "direction": direction,
            "risk": risk,
            "result_r": result_r,
            "setup": setup,
            "liquidity_sweep": liquidity_sweep.lower() == 'y',
            "bos": bos.lower() == 'y',
            "structural_liquidity": structural_liquidity.lower() == 'y',
            "poi": poi.lower() == 'y'
        }
        trades.append(trade)
        trade_id += 1

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
    total_win_r = 0
    total_loss_r = 0
    liquidity_sweep_trades = 0
    liquidity_sweep_wins = 0
    bos_trades = 0
    bos_wins = 0    
    structural_liquidity_trades = 0
    structural_liquidity_wins = 0
    poi_trades = 0
    poi_wins = 0
    all_conditions_trades = 0
    all_conditions_wins = 0
    all_conditions_r = 0

    for i in trades:
        result = calculate_pnl(i["risk"], i["result_r"])
        total_r += i["result_r"]
        net_pnl += result

        if i["result_r"] > 0:
            total_profit += result
            wins += 1
            total_win_r += i["result_r"]

        elif i["result_r"] == 0:
            breakevens +=1

        else:
            total_loss += result
            losses += 1
            total_loss_r += i["result_r"]

        if i.get("liquidity_sweep", False):
            liquidity_sweep_trades += 1
            if i["result_r"] > 0:
                liquidity_sweep_wins += 1

        if i.get("bos", False):
            bos_trades += 1
            if i["result_r"] > 0:
                bos_wins += 1
        if i.get("structural_liquidity", False):
            structural_liquidity_trades += 1
            if i["result_r"] > 0:
                structural_liquidity_wins += 1
        if i.get("poi", False):
            poi_trades += 1
            if i["result_r"] > 0:
                poi_wins += 1

        if i.get("liquidity_sweep", False) and i.get("bos", False) and i.get("structural_liquidity", False) and i.get("poi", False):
            all_conditions_trades += 1
            all_conditions_r += i["result_r"]

            if i["result_r"] > 0:
                all_conditions_wins +=1

    
    total_trades = len(trades)
    if wins > 0:
        avg_win_r = total_win_r / wins
    else:
        avg_win_r = 0
    if losses > 0:
        avg_loss_r = total_loss_r / losses
    else:
        avg_loss_r = 0
    if total_trades > 0:
        win_rate = (wins / total_trades) * 100 
    else:
        win_rate = 0
    if liquidity_sweep_trades > 0:
        liquidity_sweep_win_rate = (liquidity_sweep_wins / liquidity_sweep_trades) * 100
    else:
        liquidity_sweep_win_rate = 0
    if bos_trades > 0:
        bos_win_rate = (bos_wins / bos_trades) * 100
    else:
        bos_win_rate = 0
    if structural_liquidity_trades > 0:
        structural_liquidity_win_rate = (structural_liquidity_wins / structural_liquidity_trades) * 100
    else:
        structural_liquidity_win_rate = 0
    if poi_trades > 0:
        poi_win_rate = (poi_wins / poi_trades) * 100
    else:
        poi_win_rate = 0
    if all_conditions_trades > 0:
        all_conditions_win_rate = (all_conditions_wins / all_conditions_trades) * 100
        all_conditions_avg_r = all_conditions_r / all_conditions_trades
    else:
        all_conditions_win_rate = 0
        all_conditions_avg_r = 0

    print("\n----- TRADING SUMMARY -----")
    print(f"Total Trades: {total_trades}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Breakevens: {breakevens}")
    print(f"Profit: ${total_profit:.2f}")
    print(f"Loss: ${total_loss:.2f}")
    print(f"Total R: {total_r:.2f}R")
    print(f"Net PnL: ${net_pnl:.2f}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Liquidity Sweep Trades: {liquidity_sweep_trades}")
    print(f"Liquidity Sweep Win Rate: {liquidity_sweep_win_rate:.2f}%")
    print(f"BOS Trades: {bos_trades}")
    print(f"BOS Win Rate: {bos_win_rate:.2f}%")
    print(f"Structural Liquidity Trades: {structural_liquidity_trades}")
    print(f"Structural Liquidity Win Rate: {structural_liquidity_win_rate:.2f}%")
    print(f"POI Trades: {poi_trades}")
    print(f"POI Win Rate: {poi_win_rate:.2f}%")
    print(f"All Conditions Trades: {all_conditions_trades}")
    print(f"All Conditions Win Rate: {all_conditions_win_rate:.2f}%")
    print(f"All Conditions Average R: {all_conditions_avg_r:.2f}R")
    print(f"Average Win R: {avg_win_r:.2f}R")
    print(f"Average Loss R: {avg_loss_r:.2f}R")

if __name__ == "__main__":
    main()