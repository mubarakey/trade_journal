def calculate_pnl(risk, result_r):
    if not isinstance(risk, (int, float)):
        return 0

    if not isinstance(result_r, (int, float)):
        return 0

    return risk * result_r

CONDITIONS = [
    "liquidity_sweep",
    "bos",
    "structural_liquidity",
    "poi"
]


def all_conditions_met(trade):
    return all(
        trade.get(condition, False)
        for condition in CONDITIONS
    )

ENTRY_TYPES = [
    "failed_orderblock",
    "fibonacci_zone",
    "supply_zone",
    "demand_zone"
]


def is_valid_entry_type(entry_type):
    return entry_type in ENTRY_TYPES


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

def calculate_trade_quality(trade):
    score = 0

    if all_conditions_met(trade):
        score += 1

    if is_valid_entry_type(trade.get("entry_type")):
        score += 1

    if trade.get("planned_tp", 0) > 0:
        score += 1

    if not trade.get("mistake", False):
        score += 1

    if trade.get("exit_type") in ["tp", "sl", "be", "manual"]:
        score += 1

    return score

DIRECTIONS = [
    "buy",
    "sell"
]


def is_valid_direction(direction):
    return direction.lower() in DIRECTIONS

EXIT_TYPES = [
    "tp",
    "sl",
    "be",
    "manual"
]


def is_valid_exit_type(exit_type):
    return exit_type.lower() in EXIT_TYPES

def is_valid_risk(risk):
    return isinstance(risk, (int, float)) and risk > 0

def is_valid_planned_tp(planned_tp):
    return isinstance(planned_tp, (int, float)) and planned_tp > 0

def is_valid_pair(pair):
    return isinstance(pair, str) and len(pair.strip()) > 0

def is_valid_result_r(result_r):
    return isinstance(result_r, (int, float))

def is_valid_mistake_type(mistake, mistake_type):
    if mistake:
        return (
            isinstance(mistake_type, str)
            and len(mistake_type.strip()) > 0
        )

    return True