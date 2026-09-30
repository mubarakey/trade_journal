from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date 
from database import create_tables,get_connection
from calculations import (
    calculate_pnl,
    all_conditions_met,
    is_valid_entry_type,
    calculate_tp_capture,
    is_early_exit,
    calculate_r_left,
    calculate_trade_quality,
    is_valid_direction,
    is_valid_exit_type,
    is_valid_risk,
    is_valid_planned_tp,
    is_valid_pair,
    is_valid_result_r,
    is_valid_mistake_type
)
app = FastAPI(
    title="Trading Journal API",
    description="Backend API for the Trading Journal application.",
    version="1.0.0"
)
app.add_middleware( CORSMiddleware,
    allow_origins=["*"],       
    allow_methods=["*"],
    allow_headers=["*"],
)
create_tables()

@app.get(
    "/",
    tags=["System"]
)
def home():
    return {
        "message": "Trading Journal API is running!"
    }


@app.post(
    "/trades",
    tags=["Trades"],
    summary="Create a new trade"
)
def create_trade(
    pair: str,
    direction: str,
    risk: float,
    result_r: float,
    entry_type: str,
    liquidity_sweep: bool,
    bos: bool,
    structural_liquidity: bool,
    poi: bool,
    exit_type: str,
    planned_tp: float,
    mistake: bool,
    mistake_type: str
):

    if not is_valid_pair(pair):
        raise HTTPException(
            status_code=400,
            detail="Pair is required."
        )

    if not is_valid_direction(direction):
        raise HTTPException(
            status_code=400,
            detail="Invalid direction. Use buy or sell."
        )

    if not is_valid_risk(risk):
        raise HTTPException(
            status_code=400,
            detail="Risk must be greater than 0."
        )

    if not is_valid_risk(risk):
        raise HTTPException(
            status_code=400,
            detail="Risk must be greater than 0."
        )

    if not is_valid_result_r(result_r):
        raise HTTPException(
            status_code=400,
            detail="Result R must be a number."
        )
    if not is_valid_entry_type(entry_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid entry type."
        )
    if not is_valid_exit_type(exit_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid exit type."
        )
    if not is_valid_exit_type(exit_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid exit type."
        )
    if not is_valid_planned_tp(planned_tp):
        raise HTTPException(
            status_code=400,
            detail="Planned TP must be greater than 0."
        )

    trade = {
        "trade_date": str(date.today()),
        "pair": pair,
        "direction": direction,
        "risk": risk,
        "result_r": result_r,
        "entry_type": entry_type,
        "liquidity_sweep": liquidity_sweep,
        "bos": bos,
        "structural_liquidity": structural_liquidity,
        "poi": poi,
        "exit_type": exit_type,
        "planned_tp": planned_tp,
        "mistake": mistake,
        "mistake_type": mistake_type
    }

    pnl = calculate_pnl(risk, result_r)

    valid_smc = all_conditions_met(trade)

    tp_capture = calculate_tp_capture(
        planned_tp,
        result_r
    )

    early_exit = is_early_exit(trade)

    r_left = calculate_r_left(
        planned_tp,
        result_r
    ) if early_exit else 0

    trade_quality = calculate_trade_quality(trade)

    # Save trade to database
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO trades (
            trade_date,
            pair,
            direction,
            risk,
            result_r,
            entry_type,
            liquidity_sweep,
            bos,
            structural_liquidity,
            poi,
            exit_type,
            planned_tp,
            mistake,
            mistake_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade["trade_date"],
        pair,
        direction,
        risk,
        result_r,
        entry_type,
        liquidity_sweep,
        bos,
        structural_liquidity,
        poi,
        exit_type,
        planned_tp,
        mistake,
        mistake_type
    ))

    connection.commit()
    connection.close()

    # Return response
    return {
        **trade,
        "pnl": pnl,
        "valid_smc": valid_smc,
        "tp_capture": tp_capture,
        "early_exit": early_exit,
        "r_left": r_left,
        "trade_quality": trade_quality
    }

@app.get(
    "/trades",
    tags=["Trades"],
    summary="Get all trades"
)
def get_trades():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM trades")

    rows = cursor.fetchall()

    connection.close()

    trades = []

    for row in rows:

        trade = {
            "id": row[0],
            "pair": row[1],
            "direction": row[2],
            "risk": row[3],
            "result_r": row[4],
            "entry_type": row[5],
            "liquidity_sweep": bool(row[6]),
            "bos": bool(row[7]),
            "structural_liquidity": bool(row[8]),
            "poi": bool(row[9]),
            "exit_type": row[10],
            "planned_tp": row[11],
            "mistake": bool(row[12]),
            "mistake_type": row[13]
        }

        trades.append(trade)

    return trades

@app.put("/trades/{trade_id}")
def update_trade(
    trade_id: int,
    pair: str,
    direction: str,
    risk: float,
    result_r: float,
    entry_type: str,
    liquidity_sweep: bool,
    bos: bool,
    structural_liquidity: bool,
    poi: bool,
    exit_type: str,
    planned_tp: float,
    mistake: bool,
    mistake_type: str
):

    if not is_valid_entry_type(entry_type):
        return {
            "error": "Invalid entry type"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE trades
        SET
            pair = ?,
            direction = ?,
            risk = ?,
            result_r = ?,
            entry_type = ?,
            liquidity_sweep = ?,
            bos = ?,
            structural_liquidity = ?,
            poi = ?,
            exit_type = ?,
            planned_tp = ?,
            mistake = ?,
            mistake_type = ?
        WHERE id = ?
    """, (
        pair,
        direction,
        risk,
        result_r,
        entry_type,
        liquidity_sweep,
        bos,
        structural_liquidity,
        poi,
        exit_type,
        planned_tp,
        mistake,
        mistake_type,
        trade_id
    ))

    if cursor.rowcount == 0:
        connection.close()

        return {
            "error": "Trade not found"
        }

    connection.commit()
    connection.close()

    return {
        "message": "Trade updated successfully",
        "trade_id": trade_id
    }

@app.get(
    "/trades/{trade_id}",
    tags=["Trades"],
    summary="Get a single trade"
)
def get_trade(trade_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM trades WHERE id = ?",
        (trade_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found."
        )

    return {
        "id": row[0],
        "trade_date": row[14],
        "pair": row[1],
        "direction": row[2],
        "risk": row[3],
        "result_r": row[4],
        "entry_type": row[5],
        "liquidity_sweep": bool(row[6]),
        "bos": bool(row[7]),
        "structural_liquidity": bool(row[8]),
        "poi": bool(row[9]),
        "exit_type": row[10],
        "planned_tp": row[11],
        "mistake": bool(row[12]),
        "mistake_type": row[13]
    }

@app.get(
    "/stats",
    tags=["Statistics"],
    summary="Get overall trading statistics"
)
def get_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT result_r FROM trades")

    rows = cursor.fetchall()

    connection.close()

    total_trades = len(rows)

    wins = 0
    losses = 0
    breakevens = 0

    total_r = 0
    winning_r = 0
    losing_r = 0

    for row in rows:
        result_r = row[0]

        total_r += result_r

        if result_r > 0:
            wins += 1
            winning_r += result_r

        elif result_r < 0:
            losses += 1
            losing_r += result_r

        else:
            breakevens += 1

    win_rate = 0

    if total_trades > 0:
        win_rate = (wins / total_trades) * 100

    avg_r = 0

    if total_trades > 0:
        avg_r = total_r / total_trades

    avg_win_r = 0

    if wins > 0:
        avg_win_r = winning_r / wins

    avg_loss_r = 0

    if losses > 0:
        avg_loss_r = losing_r / losses

    expectancy = avg_r

    profit_factor = 0

    if losing_r != 0:
        profit_factor = winning_r / abs(losing_r)

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "breakevens": breakevens,
        "total_r": total_r,
        "win_rate": win_rate,
        "avg_r": avg_r,
        "avg_win_r": avg_win_r,
        "avg_loss_r": avg_loss_r,
        "expectancy": expectancy,
        "profit_factor": profit_factor
    }
@app.get(
    "/stats/entry-types",
    tags=["Statistics"],
    summary="Get entry type performance"
)
def get_entry_type_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT entry_type, result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        entry_type = row[0]
        result_r = row[1]

        if entry_type not in stats:
            stats[entry_type] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "total_r": 0
            }

        stats[entry_type]["trades"] += 1
        stats[entry_type]["total_r"] += result_r

        if result_r > 0:
            stats[entry_type]["wins"] += 1

        elif result_r < 0:
            stats[entry_type]["losses"] += 1

    for entry_type in stats:
        trades = stats[entry_type]["trades"]

        stats[entry_type]["average_r"] = (
            stats[entry_type]["total_r"] / trades
        )

    return stats

@app.get(
    "/stats/exit-discipline",
    tags=["Statistics"],
    summary="Get exit discipline statistics"
)
def get_exit_discipline_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            result_r,
            planned_tp,
            exit_type
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    early_exit_count = 0
    total_tp_capture = 0
    total_r_left = 0

    for row in rows:
        result_r = row[0]
        planned_tp = row[1]
        exit_type = row[2]

        if (
            exit_type == "manual"
            and result_r > 0
            and planned_tp > 0
            and result_r < planned_tp
        ):
            early_exit_count += 1

            tp_capture = (result_r / planned_tp) * 100

            r_left = planned_tp - result_r

            total_tp_capture += tp_capture
            total_r_left += r_left

    average_tp_capture = 0

    if early_exit_count > 0:
        average_tp_capture = (
            total_tp_capture / early_exit_count
        )

    return {
        "early_exit_count": early_exit_count,
        "average_tp_capture": average_tp_capture,
        "r_left_on_early_exits": total_r_left
    }

@app.get(
    "/stats/conditions",
    tags=["Statistics"],
    summary="Get SMC condition performance"
)
def get_condition_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            liquidity_sweep,
            bos,
            structural_liquidity,
            poi,
            result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    conditions = {
        "liquidity_sweep": {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_r": 0
        },
        "bos": {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_r": 0
        },
        "structural_liquidity": {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_r": 0
        },
        "poi": {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_r": 0
        }
    }

    for row in rows:
        liquidity_sweep = bool(row[0])
        bos = bool(row[1])
        structural_liquidity = bool(row[2])
        poi = bool(row[3])
        result_r = row[4]

        trade_conditions = {
            "liquidity_sweep": liquidity_sweep,
            "bos": bos,
            "structural_liquidity": structural_liquidity,
            "poi": poi
        }

        for condition, present in trade_conditions.items():

            if not present:
                continue

            conditions[condition]["trades"] += 1
            conditions[condition]["total_r"] += result_r

            if result_r > 0:
                conditions[condition]["wins"] += 1

            elif result_r < 0:
                conditions[condition]["losses"] += 1

    for condition in conditions:
        trades = conditions[condition]["trades"]

        if trades > 0:
            conditions[condition]["average_r"] = (
                conditions[condition]["total_r"] / trades
            )
        else:
            conditions[condition]["average_r"] = 0

    return conditions

@app.get(
    "/stats/mistakes",
    tags=["Statistics"],
    summary="Get mistake statistics"
)
def get_mistake_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT mistake, mistake_type
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    total_trades = len(rows)
    total_mistakes = 0
    mistake_types = {}

    for row in rows:
        mistake = bool(row[0])
        mistake_type = row[1]

        if mistake:
            total_mistakes += 1

            if mistake_type not in mistake_types:
                mistake_types[mistake_type] = 0

            mistake_types[mistake_type] += 1

    mistake_rate = 0

    if total_trades > 0:
        mistake_rate = (
            total_mistakes / total_trades
        ) * 100

    return {
        "total_trades": total_trades,
        "total_mistakes": total_mistakes,
        "mistake_rate": mistake_rate,
        "mistake_types": mistake_types
    }

@app.get(
    "/stats/directions",
    tags=["Statistics"],
    summary="Get buy and sell performance"
)
def get_direction_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT direction, result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        direction = row[0]
        result_r = row[1]

        if direction not in stats:
            stats[direction] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[direction]["trades"] += 1
        stats[direction]["total_r"] += result_r

        if result_r > 0:
            stats[direction]["wins"] += 1

        elif result_r < 0:
            stats[direction]["losses"] += 1

        else:
            stats[direction]["breakevens"] += 1

    for direction in stats:
        trades = stats[direction]["trades"]

        stats[direction]["average_r"] = (
            stats[direction]["total_r"] / trades
        )

    return stats

@app.get(
    "/stats/setup-combinations",
    tags=["Statistics"],
    summary="Get setup combination performance"
)
def get_setup_combination_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT direction, entry_type, result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        direction = row[0]
        entry_type = row[1]
        result_r = row[2]

        key = f"{direction}_{entry_type}"

        if key not in stats:
            stats[key] = {
                "direction": direction,
                "entry_type": entry_type,
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[key]["trades"] += 1
        stats[key]["total_r"] += result_r

        if result_r > 0:
            stats[key]["wins"] += 1

        elif result_r < 0:
            stats[key]["losses"] += 1

        else:
            stats[key]["breakevens"] += 1

    for key in stats:
        trades = stats[key]["trades"]

        stats[key]["average_r"] = (
            stats[key]["total_r"] / trades
        )

    return stats

@app.get(
    "/stats/smc-validity",
    tags=["Statistics"],
    summary="Compare valid and invalid SMC trades"
)
def get_smc_validity_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            liquidity_sweep,
            bos,
            structural_liquidity,
            poi,
            result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {
        "valid_smc": {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "breakevens": 0,
            "total_r": 0
        },
        "invalid_smc": {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "breakevens": 0,
            "total_r": 0
        }
    }

    for row in rows:
        trade = {
            "liquidity_sweep": bool(row[0]),
            "bos": bool(row[1]),
            "structural_liquidity": bool(row[2]),
            "poi": bool(row[3])
        }

        result_r = row[4]

        if all_conditions_met(trade):
            key = "valid_smc"
        else:
            key = "invalid_smc"

        stats[key]["trades"] += 1
        stats[key]["total_r"] += result_r

        if result_r > 0:
            stats[key]["wins"] += 1

        elif result_r < 0:
            stats[key]["losses"] += 1

        else:
            stats[key]["breakevens"] += 1

    for key in stats:
        trades = stats[key]["trades"]

        if trades > 0:
            stats[key]["average_r"] = (
                stats[key]["total_r"] / trades
            )
        else:
            stats[key]["average_r"] = 0

    return stats

@app.get(
    "/stats/pairs",
    tags=["Statistics"],
    summary="Get pair performance"
)
def get_pair_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT pair, result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        pair = row[0]
        result_r = row[1]

        if pair not in stats:
            stats[pair] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[pair]["trades"] += 1
        stats[pair]["total_r"] += result_r

        if result_r > 0:
            stats[pair]["wins"] += 1

        elif result_r < 0:
            stats[pair]["losses"] += 1

        else:
            stats[pair]["breakevens"] += 1

    for pair in stats:
        trades = stats[pair]["trades"]

        stats[pair]["average_r"] = (
            stats[pair]["total_r"] / trades
        )

    return stats

@app.get(
    "/stats/daily",
    tags=["Statistics"],
    summary="Get daily performance"
)
def get_daily_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT trade_date, result_r
        FROM trades
        WHERE trade_date != ''
        ORDER BY trade_date
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        trade_date = row[0]
        result_r = row[1]

        if trade_date not in stats:
            stats[trade_date] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[trade_date]["trades"] += 1
        stats[trade_date]["total_r"] += result_r

        if result_r > 0:
            stats[trade_date]["wins"] += 1

        elif result_r < 0:
            stats[trade_date]["losses"] += 1

        else:
            stats[trade_date]["breakevens"] += 1

    for trade_date in stats:
        trades = stats[trade_date]["trades"]

        stats[trade_date]["average_r"] = (
            stats[trade_date]["total_r"] / trades
        )

    return stats

@app.get(
    "/stats/weekly",
    tags=["Statistics"],
    summary="Get weekly performance"
)
def get_weekly_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT trade_date, result_r
        FROM trades
        WHERE trade_date != ''
        ORDER BY trade_date
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        trade_date = row[0]
        result_r = row[1]

        year, week, _ = date.fromisoformat(trade_date).isocalendar()

        week_key = f"{year}-W{week:02d}"

        if week_key not in stats:
            stats[week_key] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[week_key]["trades"] += 1
        stats[week_key]["total_r"] += result_r

        if result_r > 0:
            stats[week_key]["wins"] += 1

        elif result_r < 0:
            stats[week_key]["losses"] += 1

        else:
            stats[week_key]["breakevens"] += 1

    for week in stats:
        trades = stats[week]["trades"]

        stats[week]["average_r"] = (
            stats[week]["total_r"] / trades
        )

    return stats


@app.get(
    "/stats/monthly",
    tags=["Statistics"],
    summary="Get monthly performance"
)
def get_monthly_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT trade_date, result_r
        FROM trades
        WHERE trade_date != ''
        ORDER BY trade_date
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        trade_date = row[0]
        result_r = row[1]

        month_key = trade_date[:7]

        if month_key not in stats:
            stats[month_key] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[month_key]["trades"] += 1
        stats[month_key]["total_r"] += result_r

        if result_r > 0:
            stats[month_key]["wins"] += 1

        elif result_r < 0:
            stats[month_key]["losses"] += 1

        else:
            stats[month_key]["breakevens"] += 1

    for month in stats:
        trades = stats[month]["trades"]

        stats[month]["average_r"] = (
            stats[month]["total_r"] / trades
        )

    return stats

@app.get(
    "/stats/performance-over-time",
    tags=["Statistics"],
    summary="Get performance over time"
)
def get_performance_over_time():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, trade_date, pair, result_r
        FROM trades
        WHERE trade_date != ''
        ORDER BY trade_date, id
    """)

    rows = cursor.fetchall()

    connection.close()

    performance = []

    cumulative_r = 0

    for row in rows:
        trade_id = row[0]
        trade_date = row[1]
        pair = row[2]
        result_r = row[3]

        cumulative_r += result_r

        performance.append({
            "trade_id": trade_id,
            "trade_date": trade_date,
            "pair": pair,
            "result_r": result_r,
            "cumulative_r": cumulative_r
        })

    return performance

@app.get(
    "/stats/drawdown",
    tags=["Statistics"],
    summary="Get drawdown statistics"
)
def get_drawdown_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT trade_date, result_r
        FROM trades
        WHERE trade_date != ''
        ORDER BY trade_date, id
    """)

    rows = cursor.fetchall()

    connection.close()

    cumulative_r = 0
    peak_r = 0
    max_drawdown = 0

    for row in rows:
        result_r = row[1]

        cumulative_r += result_r

        if cumulative_r > peak_r:
            peak_r = cumulative_r

        drawdown = peak_r - cumulative_r

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    current_drawdown = peak_r - cumulative_r

    return {
        "current_r": cumulative_r,
        "peak_r": peak_r,
        "current_drawdown": current_drawdown,
        "max_drawdown": max_drawdown
    }

@app.get(
    "/stats/streaks",
    tags=["Statistics"],
    summary="Get winning and losing streaks"
)
def get_streak_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT trade_date, result_r
        FROM trades
        WHERE trade_date != ''
        ORDER BY trade_date, id
    """)

    rows = cursor.fetchall()

    connection.close()

    current_streak = 0
    current_streak_type = "none"

    longest_win_streak = 0
    longest_loss_streak = 0

    win_streak = 0
    loss_streak = 0

    for row in rows:
        result_r = row[1]

        if result_r > 0:
            win_streak += 1
            loss_streak = 0

            if win_streak > longest_win_streak:
                longest_win_streak = win_streak

        elif result_r < 0:
            loss_streak += 1
            win_streak = 0

            if loss_streak > longest_loss_streak:
                longest_loss_streak = loss_streak

        else:
            win_streak = 0
            loss_streak = 0

    if win_streak > 0:
        current_streak = win_streak
        current_streak_type = "win"

    elif loss_streak > 0:
        current_streak = loss_streak
        current_streak_type = "loss"

    return {
        "current_streak": current_streak,
        "current_streak_type": current_streak_type,
        "longest_win_streak": longest_win_streak,
        "longest_loss_streak": longest_loss_streak
    }

@app.get(
    "/stats/entry-types/detailed",
    tags=["Statistics"],
    summary="Get detailed entry type performance"
)
def get_detailed_entry_type_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT entry_type, result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        entry_type = row[0]
        result_r = row[1]

        if entry_type not in stats:
            stats[entry_type] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[entry_type]["trades"] += 1
        stats[entry_type]["total_r"] += result_r

        if result_r > 0:
            stats[entry_type]["wins"] += 1

        elif result_r < 0:
            stats[entry_type]["losses"] += 1

        else:
            stats[entry_type]["breakevens"] += 1

    for entry_type in stats:
        trades = stats[entry_type]["trades"]
        wins = stats[entry_type]["wins"]

        stats[entry_type]["average_r"] = (
            stats[entry_type]["total_r"] / trades
        )

        stats[entry_type]["win_rate"] = (
            (wins / trades) * 100
        )

    return stats

@app.get(
    "/stats/directions/detailed",
    tags=["Statistics"],
    summary="Get detailed direction performance"
)
def get_detailed_direction_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT direction, result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        direction = row[0]
        result_r = row[1]

        if direction not in stats:
            stats[direction] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[direction]["trades"] += 1
        stats[direction]["total_r"] += result_r

        if result_r > 0:
            stats[direction]["wins"] += 1

        elif result_r < 0:
            stats[direction]["losses"] += 1

        else:
            stats[direction]["breakevens"] += 1

    for direction in stats:
        trades = stats[direction]["trades"]
        wins = stats[direction]["wins"]

        stats[direction]["average_r"] = (
            stats[direction]["total_r"] / trades
        )

        stats[direction]["win_rate"] = (
            (wins / trades) * 100
        )

    return stats

@app.get(
    "/stats/mistakes/detailed",
    tags=["Statistics"],
    summary="Get detailed mistake performance"
)
def get_detailed_mistake_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT mistake_type, result_r
        FROM trades
        WHERE mistake = 1
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        mistake_type = row[0]
        result_r = row[1]

        if mistake_type not in stats:
            stats[mistake_type] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[mistake_type]["trades"] += 1
        stats[mistake_type]["total_r"] += result_r

        if result_r > 0:
            stats[mistake_type]["wins"] += 1

        elif result_r < 0:
            stats[mistake_type]["losses"] += 1

        else:
            stats[mistake_type]["breakevens"] += 1

    for mistake_type in stats:
        trades = stats[mistake_type]["trades"]
        wins = stats[mistake_type]["wins"]

        stats[mistake_type]["average_r"] = (
            stats[mistake_type]["total_r"] / trades
        )

        stats[mistake_type]["win_rate"] = (
            (wins / trades) * 100
        )

    return stats
@app.get(
    "/stats/exit-types",
    tags=["Statistics"],
    summary="Get exit type performance"
)
def get_exit_type_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT exit_type, result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        exit_type = row[0]
        result_r = row[1]

        if exit_type not in stats:
            stats[exit_type] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats[exit_type]["trades"] += 1
        stats[exit_type]["total_r"] += result_r

        if result_r > 0:
            stats[exit_type]["wins"] += 1

        elif result_r < 0:
            stats[exit_type]["losses"] += 1

        else:
            stats[exit_type]["breakevens"] += 1

    for exit_type in stats:
        trades = stats[exit_type]["trades"]
        wins = stats[exit_type]["wins"]

        stats[exit_type]["average_r"] = (
            stats[exit_type]["total_r"] / trades
        )

        stats[exit_type]["win_rate"] = (
            (wins / trades) * 100
        )

    return stats

@app.get(
    "/stats/conditions/directions",
    tags=["Statistics"],
    summary="Get SMC condition and direction performance"
)
def get_condition_direction_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            direction,
            liquidity_sweep,
            bos,
            structural_liquidity,
            poi,
            result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    stats = {}

    for row in rows:
        direction = row[0]
        result_r = row[5]

        conditions = {
            "liquidity_sweep": bool(row[1]),
            "bos": bool(row[2]),
            "structural_liquidity": bool(row[3]),
            "poi": bool(row[4])
        }

        for condition, present in conditions.items():

            if not present:
                continue

            key = f"{direction}_{condition}"

            if key not in stats:
                stats[key] = {
                    "direction": direction,
                    "condition": condition,
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "breakevens": 0,
                    "total_r": 0
                }

            stats[key]["trades"] += 1
            stats[key]["total_r"] += result_r

            if result_r > 0:
                stats[key]["wins"] += 1

            elif result_r < 0:
                stats[key]["losses"] += 1

            else:
                stats[key]["breakevens"] += 1

    for key in stats:
        trades = stats[key]["trades"]
        wins = stats[key]["wins"]

        stats[key]["average_r"] = (
            stats[key]["total_r"] / trades
        )

        stats[key]["win_rate"] = (
            (wins / trades) * 100
        )

    return stats

@app.get(
    "/stats/smc-compliance",
    tags=["Statistics"],
    summary="Get SMC compliance statistics"
)
def get_smc_compliance_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            liquidity_sweep,
            bos,
            structural_liquidity,
            poi,
            result_r
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    total_trades = len(rows)

    valid_trades = 0
    invalid_trades = 0

    valid_total_r = 0
    invalid_total_r = 0

    for row in rows:
        trade = {
            "liquidity_sweep": bool(row[0]),
            "bos": bool(row[1]),
            "structural_liquidity": bool(row[2]),
            "poi": bool(row[3])
        }

        result_r = row[4]

        if all_conditions_met(trade):
            valid_trades += 1
            valid_total_r += result_r

        else:
            invalid_trades += 1
            invalid_total_r += result_r

    compliance_rate = 0

    if total_trades > 0:
        compliance_rate = (
            valid_trades / total_trades
        ) * 100

    return {
        "total_trades": total_trades,
        "valid_smc_trades": valid_trades,
        "invalid_smc_trades": invalid_trades,
        "compliance_rate": compliance_rate,
        "valid_smc_total_r": valid_total_r,
        "invalid_smc_total_r": invalid_total_r
    }

@app.get(
    "/stats/exit-discipline/summary",
    tags=["Statistics"],
    summary="Get exit discipline summary"
)
def get_exit_discipline_summary():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            result_r,
            planned_tp,
            exit_type
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    total_trades = len(rows)

    tp_exits = 0
    sl_exits = 0
    be_exits = 0
    manual_exits = 0

    early_exits = 0
    total_tp_capture = 0
    total_r_left = 0

    for row in rows:
        result_r = row[0]
        planned_tp = row[1]
        exit_type = row[2]

        if exit_type == "tp":
            tp_exits += 1

        elif exit_type == "sl":
            sl_exits += 1

        elif exit_type == "be":
            be_exits += 1

        elif exit_type == "manual":
            manual_exits += 1

        if (
            exit_type == "manual"
            and result_r > 0
            and planned_tp > 0
            and result_r < planned_tp
        ):
            early_exits += 1

            tp_capture = (
                result_r / planned_tp
            ) * 100

            r_left = planned_tp - result_r

            total_tp_capture += tp_capture
            total_r_left += r_left

    average_tp_capture = 0

    if early_exits > 0:
        average_tp_capture = (
            total_tp_capture / early_exits
        )

    return {
        "total_trades": total_trades,
        "tp_exits": tp_exits,
        "sl_exits": sl_exits,
        "be_exits": be_exits,
        "manual_exits": manual_exits,
        "early_exits": early_exits,
        "average_tp_capture": average_tp_capture,
        "total_r_left": total_r_left
    }

@app.get(
    "/stats/trade-quality",
    tags=["Statistics"],
    summary="Get trade quality statistics"
)
def get_trade_quality_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            risk,
            result_r,
            entry_type,
            liquidity_sweep,
            bos,
            structural_liquidity,
            poi,
            planned_tp,
            mistake,
            exit_type
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    total_trades = len(rows)

    quality_counts = {
        "5": 0,
        "4": 0,
        "3": 0,
        "2": 0,
        "1": 0,
        "0": 0
    }

    total_quality = 0

    for row in rows:
        trade = {
            "risk": row[0],
            "result_r": row[1],
            "entry_type": row[2],
            "liquidity_sweep": bool(row[3]),
            "bos": bool(row[4]),
            "structural_liquidity": bool(row[5]),
            "poi": bool(row[6]),
            "planned_tp": row[7],
            "mistake": bool(row[8]),
            "exit_type": row[9]
        }

        quality = calculate_trade_quality(trade)

        quality_counts[str(quality)] += 1
        total_quality += quality

    average_quality = 0

    if total_trades > 0:
        average_quality = total_quality / total_trades

    return {
        "total_trades": total_trades,
        "average_quality": average_quality,
        "quality_5": quality_counts["5"],
        "quality_4": quality_counts["4"],
        "quality_3": quality_counts["3"],
        "quality_2": quality_counts["2"],
        "quality_1": quality_counts["1"],
        "quality_0": quality_counts["0"]
    }
@app.get(
    "/stats/trade-quality/performance",
    tags=["Statistics"],
    summary="Compare trade quality with performance"
)
def get_trade_quality_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            result_r,
            entry_type,
            liquidity_sweep,
            bos,
            structural_liquidity,
            poi,
            planned_tp,
            mistake,
            exit_type
        FROM trades
    """)

    rows = cursor.fetchall()

    connection.close()

    quality_stats = {}

    for row in rows:
        result_r = row[0]

        trade = {
            "entry_type": row[1],
            "liquidity_sweep": bool(row[2]),
            "bos": bool(row[3]),
            "structural_liquidity": bool(row[4]),
            "poi": bool(row[5]),
            "planned_tp": row[6],
            "mistake": bool(row[7]),
            "exit_type": row[8]
        }

        quality = calculate_trade_quality(trade)

        if quality not in quality_stats:
            quality_stats[quality] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "breakevens": 0,
                "total_r": 0
            }

        stats = quality_stats[quality]

        stats["trades"] += 1
        stats["total_r"] += result_r

        if result_r > 0:
            stats["wins"] += 1
        elif result_r < 0:
            stats["losses"] += 1
        else:
            stats["breakevens"] += 1

    performance = []

    for quality in sorted(quality_stats.keys(), reverse=True):
        stats = quality_stats[quality]

        win_rate = 0
        avg_r = 0

        if stats["trades"] > 0:
            win_rate = (
                stats["wins"] / stats["trades"]
            ) * 100

            avg_r = (
                stats["total_r"] / stats["trades"]
            )

        performance.append({
            "quality": quality,
            "trades": stats["trades"],
            "wins": stats["wins"],
            "losses": stats["losses"],
            "breakevens": stats["breakevens"],
            "win_rate": win_rate,
            "total_r": stats["total_r"],
            "avg_r": avg_r
        })

@app.get(
    "/trades/{trade_id}/review",
    tags=["Trades"],
    summary="Review a trade"
)
def get_trade_review(trade_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM trades WHERE id = ?",
        (trade_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found."
        )
    trade = {
        "id": row[0],
        "trade_date": row[14],
        "pair": row[1],
        "direction": row[2],
        "risk": row[3],
        "result_r": row[4],
        "entry_type": row[5],
        "liquidity_sweep": bool(row[6]),
        "bos": bool(row[7]),
        "structural_liquidity": bool(row[8]),
        "poi": bool(row[9]),
        "exit_type": row[10],
        "planned_tp": row[11],
        "mistake": bool(row[12]),
        "mistake_type": row[13]
    }

    pnl = calculate_pnl(
        trade["risk"],
        trade["result_r"]
    )

    valid_smc = all_conditions_met(trade)

    tp_capture = calculate_tp_capture(
        trade["planned_tp"],
        trade["result_r"]
    )

    early_exit = is_early_exit(trade)

    r_left = calculate_r_left(
        trade["planned_tp"],
        trade["result_r"]
    )

    trade_quality = calculate_trade_quality(trade)

    return {
        **trade,
        "pnl": pnl,
        "valid_smc": valid_smc,
        "tp_capture": tp_capture,
        "early_exit": early_exit,
        "r_left": r_left,
        "trade_quality": trade_quality
    }
@app.put(
    "/trades/{trade_id}",
    tags=["Trades"],
    summary="Update a trade"
)
def update_trade(
    trade_id: int,
    pair: str,
    direction: str,
    risk: float,
    result_r: float,
    entry_type: str,
    liquidity_sweep: bool,
    bos: bool,
    structural_liquidity: bool,
    poi: bool,
    exit_type: str,
    planned_tp: float,
    mistake: bool,
    mistake_type: str
):

    if not is_valid_pair(pair):
        raise HTTPException(
            status_code=400,
            detail="Pair is required."
        )

    if not is_valid_direction(direction):
        raise HTTPException(
            status_code=400,
            detail="Invalid direction. Use buy or sell."
        )

    if not is_valid_risk(risk):
        raise HTTPException(
            status_code=400,
            detail="Risk must be greater than 0."
        )

    if not is_valid_risk(risk):
        raise HTTPException(
            status_code=400,
            detail="Risk must be greater than 0."
        )

    if not is_valid_result_r(result_r):
        raise HTTPException(
            status_code=400,
            detail="Result R must be a number."
        )
    if not is_valid_entry_type(entry_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid entry type."
        )
    if not is_valid_exit_type(exit_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid exit type."
        )
    if not is_valid_exit_type(exit_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid exit type."
        )
    if not is_valid_planned_tp(planned_tp):
        raise HTTPException(
            status_code=400,
            detail="Planned TP must be greater than 0."
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM trades WHERE id = ?",
        (trade_id,)
    )

    existing_trade = cursor.fetchone()

    if existing_trade is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Trade not found."
        )

    trade = {
        "id": trade_id,
        "trade_date": existing_trade[14],
        "pair": pair,
        "direction": direction,
        "risk": risk,
        "result_r": result_r,
        "entry_type": entry_type,
        "liquidity_sweep": liquidity_sweep,
        "bos": bos,
        "structural_liquidity": structural_liquidity,
        "poi": poi,
        "exit_type": exit_type,
        "planned_tp": planned_tp,
        "mistake": mistake,
        "mistake_type": mistake_type
    }

    cursor.execute("""
        UPDATE trades
        SET
            pair = ?,
            direction = ?,
            risk = ?,
            result_r = ?,
            entry_type = ?,
            liquidity_sweep = ?,
            bos = ?,
            structural_liquidity = ?,
            poi = ?,
            exit_type = ?,
            planned_tp = ?,
            mistake = ?,
            mistake_type = ?
        WHERE id = ?
    """, (
        pair,
        direction,
        risk,
        result_r,
        entry_type,
        liquidity_sweep,
        bos,
        structural_liquidity,
        poi,
        exit_type,
        planned_tp,
        mistake,
        mistake_type,
        trade_id
    ))

    connection.commit()
    connection.close()

    pnl = calculate_pnl(risk, result_r)
    valid_smc = all_conditions_met(trade)
    tp_capture = calculate_tp_capture(
        planned_tp,
        result_r
    )
    early_exit = is_early_exit(trade)
    r_left = calculate_r_left(
        planned_tp,
        result_r
    )
    trade_quality = calculate_trade_quality(trade)

    return {
        **trade,
        "pnl": pnl,
        "valid_smc": valid_smc,
        "tp_capture": tp_capture,
        "early_exit": early_exit,
        "r_left": r_left,
        "trade_quality": trade_quality
    }