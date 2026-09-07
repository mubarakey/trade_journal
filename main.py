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
        trade_reason = input("Why did you take this trade? ")
        mistake = input("Did you make a mistake on this trade? (y/n): ")

        if mistake.lower() == "y":
            mistake_type = input("What was the mistake? ")
        else:
            mistake_type = "none"
                
       
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
            "poi": poi.lower() == 'y',
            "trade_reason": trade_reason,
            "mistake": mistake.lower() == "y",
            "mistake_type": mistake_type,
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

    not_all_conditions_trades = 0
    not_all_conditions_wins = 0
    not_all_conditions_r = 0

    setup_stats = {}
    pair_stats = {}
    direction_stats = {}
    condition_direction_stats = {}
    discipline_stats = {}
    risk_stats = {
        "total_risk": 0,
        "highest_risk": 0,
        "lowest_risk": None
    }

    for i in trades:
        setup = i.get("setup", "unknown").lower()
        pair = i.get("pair", "unknown").lower()
        direction = i.get("direction", "unknown").lower()
        all_conditions = (
            i.get("liquidity_sweep", False)
            and i.get("bos", False)
            and i.get("structural_liquidity", False)
            and i.get("poi", False)
         )
        
        if pair not in pair_stats:
            pair_stats[pair] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }
        pair_stats[pair]["trades"] += 1
        if i["result_r"] > 0:
            pair_stats[pair]["wins"] += 1
        elif i["result_r"] < 0:
            pair_stats[pair]["losses"] +=1
        elif i["result_r"] == 0:
            pair_stats[pair]["breakevens"] += 1
        pair_stats[pair]["total_r"] += i["result_r"]
        if setup not in setup_stats:
            setup_stats[setup] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }
        setup_stats[setup]["trades"] += 1


        if i["result_r"] > 0:
            setup_stats[setup]["wins"] += 1
        elif i["result_r"] < 0:
            setup_stats[setup]["losses"] +=1
        elif i["result_r"] == 0:
            setup_stats[setup]["breakevens"] += 1
        setup_stats[setup]["total_r"] += i["result_r"]


        if direction not in direction_stats:
            direction_stats[direction] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "breakevens": 0,
            "total_r": 0
        }

        direction_stats[direction]["trades"] += 1

        if i["result_r"] > 0:
            direction_stats[direction]["wins"] += 1
        elif i["result_r"] < 0:
            direction_stats[direction]["losses"] += 1
        elif i["result_r"] == 0:
            direction_stats[direction]["breakevens"] += 1

        direction_stats[direction]["total_r"] += i["result_r"]

        # all condition direction stats
        if all_conditions:
            condition_type = "all_conditions"
            discipline = "valid_trade"
        else:
            condition_type = "not_all_conditions"
            discipline = "invalid_trade"

        key = f"{direction}_{condition_type}"

        if key not in condition_direction_stats:
            condition_direction_stats[key] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }
        if discipline not in discipline_stats:
            discipline_stats[discipline] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }
        condition_direction_stats[key]["trades"] += 1

        if i["result_r"] > 0:
            condition_direction_stats[key]["wins"] += 1
        elif i["result_r"] < 0:
            condition_direction_stats[key]["losses"] += 1
        else:
            condition_direction_stats[key]["breakevens"] += 1

        condition_direction_stats[key]["total_r"] += i["result_r"]

        discipline_stats[discipline]["trades"] += 1

        #calculation of risks logic
        risk = i["risk"]

        risk_stats["total_risk"] += risk
        
        if risk > risk_stats["highest_risk"]:
            risk_stats["highest_risk"] = risk

        if risk_stats["lowest_risk"] is None or risk < risk_stats["lowest_risk"]:
            risk_stats["lowest_risk"] = risk

        if i["result_r"] > 0:
            discipline_stats[discipline]["wins"] += 1
        elif i["result_r"] < 0:
            discipline_stats[discipline]["losses"] += 1
        else:
            discipline_stats[discipline]["breakevens"] += 1

        discipline_stats[discipline]["total_r"] += i["result_r"]

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
        else:
            not_all_conditions_trades += 1
            not_all_conditions_r += i["result_r"]

            if i["result_r"] > 0:
                not_all_conditions_wins += 1

    
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
    if  not_all_conditions_trades > 0:
        not_all_conditions_win_rate = (not_all_conditions_wins / not_all_conditions_trades) * 100
        not_all_conditions_avg_r = not_all_conditions_r / not_all_conditions_trades
    else:
        not_all_conditions_win_rate = 0
        not_all_conditions_avg_r = 0
    if total_trades > 0:
        expectancy = total_r / total_trades
    else:
        expectancy = 0

    if total_trades > 0:
        risk_stats["average_risk"] = risk_stats["total_risk"] / total_trades
    else:
        risk_stats["average_risk"] = 0

    for setup, stats in setup_stats.items():
        if stats["trades"] > 0:
            stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
            stats["avg_r"] = stats["total_r"] / stats["trades"]
        else:
            stats["win_rate"] = 0
            stats["avg_r"] = 0
    
    for pair, stats in pair_stats.items():
        if stats["trades"] > 0:
            stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
            stats["avg_r"] = stats["total_r"] / stats["trades"]
        else:
            stats["win_rate"] = 0
            stats["avg_r"] = 0
    
    for direction, stats in direction_stats.items():
        if stats["trades"] > 0:
            stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
            stats["avg_r"] = stats["total_r"] / stats["trades"]
        else:
            stats["win_rate"] = 0
            stats["avg_r"] = 0
    for key, stats in condition_direction_stats.items():
        if stats["trades"] > 0:
            stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
            stats["avg_r"] = stats["total_r"] / stats["trades"]
        else:
            stats["win_rate"] = 0
            stats["avg_r"] = 0
    for discipline, stats in discipline_stats.items():
        if stats["trades"] > 0:
            stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
            stats["avg_r"] = stats["total_r"] / stats["trades"]
        else:
            stats["win_rate"] = 0
            stats["avg_r"] = 0


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
    print(f"Expectancy: {expectancy:.2f}R")
    print(f"Not All Conditions Trades: {not_all_conditions_trades}")
    print(f"Not All Conditions Win Rate: {not_all_conditions_win_rate:.2f}%")
    print(f"Not All Conditions Average R: {not_all_conditions_avg_r:.2f}R")

    print("\n----- SETUP ANALYSIS -----")

    for setup, stats in setup_stats.items():
        print(f"\nSetup: {setup}")
        print(f"Trades: {stats['trades']}")
        print(f"Wins: {stats['wins']}")
        print(f"Losses: {stats['losses']}")
        print(f"Breakevens: {stats['breakevens']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print(f"Total R: {stats['total_r']:.2f}R")
        print(f"Average R: {stats['avg_r']:.2f}R")

    print("\n----- PAIR ANALYSIS -----")

    for pair, stats in pair_stats.items():
        print(f"\nPair: {pair}")
        print(f"Trades: {stats['trades']}")
        print(f"Wins: {stats['wins']}")
        print(f"Losses: {stats['losses']}")
        print(f"Breakevens: {stats['breakevens']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print(f"Total R: {stats['total_r']:.2f}R")
        print(f"Average R: {stats['avg_r']:.2f}R")

    print("\n----- DIRECTION ANALYSIS -----")

    for direction, stats in direction_stats.items():
        print(f"\nDirection: {direction.upper()}")
        print(f"Trades: {stats['trades']}")
        print(f"Wins: {stats['wins']}")
        print(f"Losses: {stats['losses']}")
        print(f"Breakevens: {stats['breakevens']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print(f"Total R: {stats['total_r']:.2f}R")
        print(f"Average R: {stats['avg_r']:.2f}R")
    print("\n----- DIRECTION + CONDITIONS ANALYSIS -----")

    for key, stats in condition_direction_stats.items():
        print(f"\nGroup: {key}")
        print(f"Trades: {stats['trades']}")
        print(f"Wins: {stats['wins']}")
        print(f"Losses: {stats['losses']}")
        print(f"Breakevens: {stats['breakevens']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print(f"Total R: {stats['total_r']:.2f}R")
        print(f"Average R: {stats['avg_r']:.2f}R")

    print("\n----- DISCIPLINE ANALYSIS -----")

    for discipline, stats in discipline_stats.items():
        print(f"\nDiscipline: {discipline}")
        print(f"Trades: {stats['trades']}")
        print(f"Wins: {stats['wins']}")
        print(f"Losses: {stats['losses']}")
        print(f"Breakevens: {stats['breakevens']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print(f"Total R: {stats['total_r']:.2f}R")
        print(f"Average R: {stats['avg_r']:.2f}R")

    print("\n----- RISK ANALYSIS -----")

    print(f"Total Risk Taken: ${risk_stats['total_risk']:.2f}")
    print(f"Average Risk per Trade: ${risk_stats['average_risk']:.2f}")
    print(f"Highest Risk: ${risk_stats['highest_risk']:.2f}")
    print(f"Lowest Risk: ${risk_stats['lowest_risk']:.2f}")

if __name__ == "__main__":
    main()