import json
import os
from datetime import date

CONDITIONS = [
    "liquidity_sweep",
    "bos",
    "structural_liquidity",
    "poi"
]

def calculate_pnl(risk, result_r):
    return risk * result_r


def main():
    print("Welcome to the Trade PnL Journal!")
    journal()

def new_group():
    return {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "breakevens": 0,
        "total_r": 0,
        "winning_r": 0,
        "losing_r": 0
    }
def update_stats(stats, key, result_r):
    group = stats.setdefault(key, new_group())
    group["trades"] += 1
    if result_r > 0:
        group["wins"] += 1
        group["winning_r"] += result_r
    elif result_r < 0:
        group["losses"] += 1
        group["losing_r"] += result_r
    else:
        group["breakevens"] += 1

    group["total_r"] += result_r

def finalize_stats(stats):
    for group in stats.values():
        trades = group["trades"]

        group["win_rate"] = (
            group["wins"] / trades * 100
            if trades
            else 0
        )

        group["avg_r"] = (
            group["total_r"] / trades
            if trades
            else 0
        )

        group["avg_win_r"] = (
            group["winning_r"] / group["wins"]
            if group["wins"]
            else 0
        )

        group["avg_loss_r"] = (
            group["losing_r"] / group["losses"]
            if group["losses"]
            else 0
        )

def load_trades():
    #load trades
    if os.path.exists("trades.json"):
        with open("trades.json", "r") as file:
            return json.load(file)
        
    return []

def save_trades(trades):
    with open("trades.json", "w") as file:
        json.dump(trades, file, indent=4)
    
def get_next_trade_id(trades):
    if trades:
        return trades[-1]["id"] + 1 
    return 1


def get_trade(trade_id, today):

    pair = input("Enter the currency pair: ")
    direction = input("BUY/SELL: ").lower()
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
    exit_type = input("How did you exit? (tp/sl/be/manual): ")
    planned_tp = float(input("Planned TP (R): "))

    return {
        "id": trade_id,
        "date": str(today),
        "pair": pair,
        "direction": direction,
        "risk": risk,
        "result_r": result_r,
        "setup": setup,
        "liquidity_sweep": liquidity_sweep.lower() == "y",
        "bos": bos.lower() == "y",
        "structural_liquidity": structural_liquidity.lower() == "y",
        "poi": poi.lower() == "y",
        "trade_reason": trade_reason,
        "mistake": mistake.lower() == "y",
        "mistake_type": mistake_type,
        "exit_type": exit_type.lower(),
        "planned_tp": planned_tp
    }


def update_condition_stats(condition_stats, trade, result_r):
    for condition in CONDITIONS:
        if trade.get(condition, False):
            update_stats(condition_stats, condition, result_r)

def all_conditions_met(trade):
    return all(
        trade.get(condition, False)
        for condition in CONDITIONS
    )


def calculate_tp_capture(planned_tp, result_r):
    if planned_tp <= 0 or result_r <= 0:
        return 0

    return min((result_r / planned_tp) * 100, 100)

def is_early_exit(trade):
    exit_type = trade.get("exit_type", "")
    result_r = trade.get("result_r", 0)
    planned_tp = trade.get("planned_tp", 0)

    return (
        exit_type == "manual"
        and result_r > 0
        and planned_tp > 0
        and result_r < planned_tp
    )

def calculate_r_left(planned_tp, result_r):
    if planned_tp <= 0 or result_r <= 0:
        return 0
    
    return max(planned_tp - result_r, 0)

def calculate_expectancy(overall):
    win_rate = overall["wins"] / overall["trades"]
    loss_rate = overall["losses"] / overall["trades"]

    avg_win_r = overall["avg_win_r"]
    avg_loss_r = overall["avg_loss_r"]

    return (
        win_rate * avg_win_r
        + loss_rate * avg_loss_r
    )


def analyze_trades(trades):

    overall = {}
    setup_stats = {}
    pair_stats = {}
    direction_stats = {}
    condition_stats = {}
    condition_direction_stats = {}
    discipline_stats = {}
    mistake_stats = {}
    exit_stats = {}
    early_exit_stats = {}

    total_planned_tp = 0
    total_tp_capture = 0
    total_r_left = 0
    total_pnl = 0

    for trade in trades:
        result_r = trade["result_r"]
        planned_tp = trade.get("planned_tp",0)

        tp_capture = calculate_tp_capture(
            planned_tp,
            result_r
        )

        r_left = calculate_r_left(
            planned_tp,
            result_r
        )

        total_r_left += r_left
        total_planned_tp += planned_tp
        total_tp_capture += tp_capture
    
        update_stats(
            overall,
            "all",
            result_r
        )

        total_pnl += calculate_pnl(
            trade["risk"],
            result_r
        )

        update_stats(
            pair_stats,
            trade.get("pair", "unknown"),
            result_r
        )

        update_stats(
            setup_stats,
            trade.get("setup", "unknown"),
            result_r
        )

        update_stats(
            direction_stats,
            trade.get("direction", "unknown"),
            result_r
        )

        mistake_type = trade.get("mistake_type", "none")

        if mistake_type != "none":
            update_stats(
                mistake_stats,
                mistake_type,
                result_r
            )

        update_stats(
            exit_stats,
            trade.get("exit_type", "unknown"),
            result_r
        )
        update_condition_stats(
            condition_stats,
            trade,
            result_r
        )
        if all_conditions_met(trade):
            update_stats(
                discipline_stats,
                "Valid_trade",
                result_r
            )
        else:
            update_stats(
                discipline_stats,
                "Invalid_trade",
                result_r
            )
        condition_type = (
            "all_conditions"
            if all_conditions_met(trade)
            else "not_all_conditions"
            )
        
        key = (
            trade.get("direction", "unknown"),
            condition_type
        )

        update_stats(
            condition_direction_stats,
            key,
            result_r
        )

        if is_early_exit(trade):
            update_stats(
                early_exit_stats,
                "early_exit",
                result_r
            )

    for stats in (
        overall,
        setup_stats,
        pair_stats,
        direction_stats,
        mistake_stats,
        exit_stats,
        condition_stats,
        discipline_stats,
        condition_direction_stats,
        early_exit_stats
    ):
        finalize_stats(stats)

    overall_stats = get_overall_stats(overall)
    expectancy = calculate_expectancy(overall_stats)

    average_planned_tp = (
        total_planned_tp / len(trades)
        if trades
        else 0
    )

    average_tp_capture = (
        total_tp_capture / len(trades)
        if trades
        else 0
    )

    return {
        "overall": overall_stats,
        "total_pnl": total_pnl,
        "setup": setup_stats,
        "pair": pair_stats,
        "direction": direction_stats,
        "mistake": mistake_stats,
        "exit": exit_stats,
        "early_exit": early_exit_stats,
        "condition": condition_stats,
        "discipline": discipline_stats,
        "condition_direction": condition_direction_stats,
        "average_planned_tp": average_planned_tp,
        "average_tp_capture": average_tp_capture,
        "total_r_left": total_r_left,
        "expectancy": expectancy,
    }

def get_overall_stats(overall):
    return overall["all"]

#function for formatting keys for output result
def format_stats_key(key):
    if isinstance(key, tuple):
        direction, condition_type = key
        
        direction = direction.upper()

        if condition_type == "all_conditions":
            condition_type = "All Conditions"
        else: 
            condition_type = "Not All Conditions"
        return f"{direction} - {condition_type}"

    if key == "Valid_trade":
        return "Valid Trade"

    if key == "Invalid_trade":  
        return "Invalid Trade"
    
    return str(key)

def print_stats(title, stats):
    print(f"\n----- {title} -----")

    for key, group in stats.items():
        print(f"\n{format_stats_key(key)}")
        print(f"Trades: {group['trades']}")
        print(f"Wins: {group['wins']}")
        print(f"Losses: {group['losses']}")
        print(f"Breakevens: {group['breakevens']}")
        print(f"Total R: {group['total_r']:.2f}R")
        print(f"Average R: {group['avg_r']:.2f}R")
        print(f"Win Rate: {group['win_rate']:.2f}%")

def print_summary(stats):
    overall = stats["overall"]
    total_pnl = stats["total_pnl"]

    print("\n----- TRADING SUMMARY -----")
    print(f"Total Trades: {overall['trades']}")
    print(f"Wins: {overall['wins']}")
    print(f"Losses: {overall['losses']}")
    print(f"Breakevens: {overall['breakevens']}")
    print(f"Total R: {overall['total_r']:.2f}R")
    print(f"Average R: {overall['avg_r']:.2f}R")
    print(f"Average Win: {overall['avg_win_r']:.2f}R")
    print(f"Average Loss: {overall['avg_loss_r']:.2f}R")
    print(f"Expectancy: {stats['expectancy']:.2f}R")
    print(f"Win Rate: {overall['win_rate']:.2f}%")
    print(f"Net PnL: ${total_pnl:.2f}")
    print(f"Average Planned TP: {stats['average_planned_tp']:.2f}R")
    print(f"Average TP Capture: {stats['average_tp_capture']:.2f}%")
    print(f"R Left on Early Exits: {stats['total_r_left']:.2f}R")

    print_stats("CONDITION ANALYSIS", stats["condition"])
    print_stats("DISCIPLINE ANALYSIS", stats["discipline"])
    valid_r = stats["discipline"].get("Valid_trade", {}).get("total_r", 0)
    invalid_r = stats["discipline"].get("Invalid_trade", {}).get("total_r", 0)

    print(f"Valid Trade R: {valid_r:.2f}R")
    print(f"Invalid Trade R: {invalid_r:.2f}R")
    print_stats("EXIT ANALYSIS", stats["exit"])

    print_stats(
        "EARLY EXIT ANALYSIS",
        stats["early_exit"]
    )  

    print_stats(
        "CONDITION + DIRECTION",
        stats["condition_direction"]
    )
  

    
    

def journal():
    today = date.today()
    
    trades = load_trades()

    trade_id = get_next_trade_id(trades)

    while True:
        trade = get_trade(trade_id, today)
        trades.append(trade)

        trade_id += 1

        again = input("Add another trade? (y/n): ")

        if again.lower() != "y":
            break

    save_trades(trades)

    print("Trades saved successfully!")

    stats = analyze_trades(trades)

    print_summary(stats)
 
main()
    
