import json
import os
from datetime import date

CONDITIONS = [
    "liquidity_sweep",
    "bos",
    "structural_liquidity",
    "poi"
]

ENTRY_TYPES = [
    "failed_orderblock",
    "fibonacci_zone",
    "supply_zone",
    "demand_zone"
]


def calculate_pnl(risk, result_r):
    if not isinstance(risk, (int, float)):
        return 0

    if not isinstance(result_r, (int, float)):
        return 0

    return risk * result_r

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

        group["expectancy"] = (
            (group["wins"] / trades) * group["avg_win_r"]
            + (group["losses"] / trades) * group["avg_loss_r"]
            if trades
            else 0
        )

        group["profit_factor"] = (
            group["winning_r"] / abs(group["losing_r"])
            if group["losing_r"] != 0
            else 0
        )

def load_trades():
    if not os.path.exists("trades.json"):
        return []

    try:
        with open("trades.json", "r") as file:
            trades = json.load(file)

        if not isinstance(trades, list):
            print("Warning: trades.json must contain a list of trades.")
            return []

        return trades

    except json.JSONDecodeError:
        print("Warning: trades.json contains invalid data.")
        return []
    
def save_trades(trades):
    try:
        with open("trades.json", "w") as file:
            json.dump(trades, file, indent=4)

    except OSError:
        print("Error: Could not save trades.json.")

def get_next_trade_id(trades):
    if not trades:
        return 1

    return max(
        trade["id"]
        for trade in trades
    ) + 1

def get_entry_type():
    print("\nEntry Types:")

    for number, entry_type in enumerate(ENTRY_TYPES, start=1):
        display_name = entry_type.replace("_", " ").title()
        print(f"{number}. {display_name}")

    while True:
        choice = input("choose entry type: ")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(ENTRY_TYPES):
                return ENTRY_TYPES[choice - 1]
            
        print("Invalid choice. Please select a valid entry type.")

def get_direction():
    while True:
        direction = input("BUY/SELL: ").lower()

        if direction in ["buy", "sell"]:
            return direction

        print("Invalid direction. Please enter BUY or SELL.")

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def get_yes_no(prompt):
    while True:
        answer = input(prompt).lower()

        if answer in ["y", "n"]:
            return answer == "y"

        print("Please enter y or n.")

def get_exit_type():
    valid_exit_types = ["tp", "sl", "be", "manual"]

    while True:
        exit_type = input(
            "How did you exit? (tp/sl/be/manual): "
        ).lower()

        if exit_type in valid_exit_types:
            return exit_type

        print("Invalid exit type. Please choose tp, sl, be, or manual.")

def get_positive_float(prompt):
    while True:
        value = get_float_input(prompt)

        if value > 0:
            return value

        print("Please enter a number greater than 0.")

def get_text_input(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be empty.")

def get_trade(trade_id, today):

    pair = get_text_input("Enter the currency pair: ")
    direction = get_direction()
    risk = get_positive_float("Enter the risk amount: ")
    result_r = get_float_input(
        "Enter the result (R, e.g. 2, -1, 0): "
    )
    entry_type = get_entry_type()
    liquidity_sweep = get_yes_no("Liquidity sweep? (y/n): ")
    bos = get_yes_no("Break of Structure? (y/n): ")
    structural_liquidity = get_yes_no("Structural liquidity? (y/n): ")
    poi = get_yes_no("Valid POI? (y/n): ")
    trade_reason = get_text_input(
        "Why did you take this trade? "
    )
    mistake = get_yes_no(
        "Did you make a mistake on this trade? (y/n): "
    )

    if mistake:
        mistake_type = get_text_input(
            "What was the mistake? "
    )
    else:
        mistake_type = "none"


    exit_type = get_exit_type()
    planned_tp = get_positive_float("Planned TP (R): ")

    return {
        "id": trade_id,
        "date": str(today),
        "pair": pair,
        "direction": direction,
        "risk": risk,
        "result_r": result_r,
        "entry_type": entry_type,
        "liquidity_sweep": liquidity_sweep,
        "bos": bos,
        "structural_liquidity": structural_liquidity,
        "poi": poi,
        "trade_reason": trade_reason,
        "mistake": mistake,
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
    trades = overall["trades"]

    if trades == 0:
        return 0

    win_rate = overall["wins"] / trades
    loss_rate = overall["losses"] / trades
    avg_win_r = overall["avg_win_r"]
    avg_loss_r = overall["avg_loss_r"]

    return (
        win_rate * avg_win_r
        + loss_rate * avg_loss_r
    )

def calculate_profit_factor(overall):
    gross_profit = overall["winning_r"]
    gross_loss = abs(overall["losing_r"])

    if gross_loss == 0:
        return 0

    return gross_profit / gross_loss

def analyze_trades(trades):
    if not trades:
        return {
            "overall": {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0,
                "avg_r": 0,
                "avg_win_r": 0,
                "avg_loss_r": 0,
                "win_rate": 0,
                "expectancy": 0,
                "profit_factor": 0
            },
            "total_pnl": 0,
            "entry_type": {},
            "pair": {},
            "direction": {},
            "mistake": {},
            "exit": {},
            "early_exit": {},
            "exit_discipline": {},
            "condition": {},
            "discipline": {},
            "condition_direction": {},
            "average_planned_tp": 0,
            "average_tp_capture": 0,
            "average_early_exit_tp_capture": 0,
            "total_r_left": 0,
            "expectancy": 0,
            "profit_factor": 0
        }
    

    overall = {}
    entry_type_stats = {}
    pair_stats = {}
    direction_stats = {}
    condition_stats = {}
    condition_direction_stats = {}
    discipline_stats = {}
    mistake_stats = {}
    exit_stats = {}
    early_exit_stats = {}
    exit_discipline_stats = {}

    early_exit_count = 0
    total_planned_tp = 0
    total_tp_capture = 0
    early_exit_tp_capture = 0
    total_r_left = 0
    total_pnl = 0
    r_left = 0

    for trade in trades:
        result_r = trade.get("result_r", 0)
        planned_tp = trade.get("planned_tp",0)

        tp_capture = calculate_tp_capture(
            planned_tp,
            result_r
        )
        

        if is_early_exit(trade):
            early_exit_count += 1
            early_exit_tp_capture += tp_capture
            
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
            trade.get("risk", 0),
            result_r
        )

        update_stats(
            pair_stats,
            trade.get("pair", "unknown"),
            result_r
        )

        update_stats(
            entry_type_stats,
            trade.get("entry_type", "unknown"),
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
            update_stats(
                exit_discipline_stats,
                "early_exit",
                result_r
            )

        elif trade.get("exit_type") == "manual":
            update_stats(
                exit_discipline_stats,
                "manual_completed",
                result_r
            )

    for stats in (
        overall,
        entry_type_stats,
        pair_stats,
        direction_stats,
        mistake_stats,
        exit_stats,
        condition_stats,
        discipline_stats,
        condition_direction_stats,
        early_exit_stats,
        exit_discipline_stats
    ):
        finalize_stats(stats)

    overall_stats = get_overall_stats(overall)
    expectancy = calculate_expectancy(overall_stats)
    profit_factor = calculate_profit_factor(overall_stats)

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

    average_early_exit_tp_capture = (
        early_exit_tp_capture / early_exit_count
        if early_exit_count
        else 0
    )

    return {
        "overall": overall_stats,
        "total_pnl": total_pnl,
        "entry_type": entry_type_stats,
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
        "average_early_exit_tp_capture": average_early_exit_tp_capture,
        "total_r_left": total_r_left,
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "exit_discipline": exit_discipline_stats,
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

    # Make entry types easier to read
    if key in ENTRY_TYPES:
        return key.replace("_", " ").title()

    return str(key)

def print_dashboard(stats):
    overall = stats["overall"]

    print("\n" + "=" * 50)
    print("           TRADING JOURNAL DASHBOARD")
    print("=" * 50)

    print("\n----- OVERALL PERFORMANCE -----")
    print(f"Total Trades: {overall['trades']}")
    print(f"Win Rate: {overall['win_rate']:.2f}%")
    print(f"Total R: {overall['total_r']:.2f}R")
    print(f"Average R: {overall['avg_r']:.2f}R")
    print(f"Expectancy: {stats['expectancy']:.2f}R")
    print(f"Profit Factor: {stats['profit_factor']:.2f}")
    print(f"Net PnL: ${stats['total_pnl']:.2f}")

    print("\n----- SMC PERFORMANCE -----")

    valid_trade = stats["discipline"].get("Valid_trade", {})
    invalid_trade = stats["discipline"].get("Invalid_trade", {})

    print(f"Valid Trades: {valid_trade.get('trades', 0)}")
    print(f"Valid Trade Win Rate: {valid_trade.get('win_rate', 0):.2f}%")
    print(f"Valid Trade R: {valid_trade.get('total_r', 0):.2f}R")

    print(f"Invalid Trades: {invalid_trade.get('trades', 0)}")
    print(f"Invalid Trade Win Rate: {invalid_trade.get('win_rate', 0):.2f}%")
    print(f"Invalid Trade R: {invalid_trade.get('total_r', 0):.2f}R")

    print("\n" + "=" * 50)

    print("\n----- EXIT DISCIPLINE -----")

    print(
        f"Average Planned TP: "
        f"{stats['average_planned_tp']:.2f}R"
    )

    print(
        f"Average TP Capture: "
        f"{stats['average_tp_capture']:.2f}%"
    )

    print(
        f"Early Exit TP Capture: "
        f"{stats['average_early_exit_tp_capture']:.2f}%"
    )

    print(
        f"R Left on Early Exits: "
        f"{stats['total_r_left']:.2f}R"
    )

    print("\n----- BEST PERFORMERS -----")

    if stats["entry_type"]:
        best_entry_type = max(
            stats["entry_type"],
            key=lambda key: stats["entry_type"][key]["total_r"]
        )

        best_entry = stats["entry_type"][best_entry_type]

        print(
            f"Best Entry Type: "
            f"{format_stats_key(best_entry_type)}"
        )
        print(
            f"Best Entry Type R: "
            f"{best_entry['total_r']:.2f}R"
        )
        print(
            f"Best Entry Type Win Rate: "
            f"{best_entry['win_rate']:.2f}%"
        )

    if stats["direction"]:
        best_direction = max(
            stats["direction"],
            key=lambda key: stats["direction"][key]["total_r"]
        )

        best_direction_stats = stats["direction"][best_direction]

        print(
            f"Best Direction: "
            f"{format_stats_key(best_direction)}"
        )
        print(
            f"Best Direction R: "
            f"{best_direction_stats['total_r']:.2f}R"
        )
        print(
            f"Best Direction Win Rate: "
            f"{best_direction_stats['win_rate']:.2f}%"
        )

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
        print(f"Average Win: {group['avg_win_r']:.2f}R")
        print(f"Average Loss: {group['avg_loss_r']:.2f}R")
        print(f"Expectancy: {group['expectancy']:.2f}R")
        print(f"Profit Factor: {group['profit_factor']:.2f}")

def print_summary(stats):
    overall = stats["overall"]
    total_pnl = stats["total_pnl"]
    print_stats(
        "ENTRY TYPE ANALYSIS",
        stats["entry_type"]
    )
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
    print(f"Profit Factor: {stats['profit_factor']:.2f}")
    print(f"Win Rate: {overall['win_rate']:.2f}%")
    print(f"Net PnL: ${total_pnl:.2f}")
    print(f"Average Planned TP: {stats['average_planned_tp']:.2f}R")
    print(
        f"Average Early Exit TP Capture: "
        f"{stats['average_early_exit_tp_capture']:.2f}%"
    )
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
    print_dashboard(stats)
    print_summary(stats)

def main():
    print("Welcome to the Trade PnL Journal!")
    journal()

main()
    
