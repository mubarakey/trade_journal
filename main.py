def calculate_profit(risk, result_r):
    return risk * result_r
def calculate_loss(risk, result_r):
    return risk * result_r

trades = [
    {
        "pair": "EURUSD",
        "direction": "BUY",
        "risk": 15,
        "result_r": 3
    },
    {
        "pair": "GBPUSD",
        "direction": "SELL",
        "risk": 15,
        "result_r": -1
    }
]

for trade in trades:
    if trade["result_r"] > 0:
        profit = calculate_profit(trade["result_r"], trade["risk"])
    else:
        loss = calculate_loss(trade["result_r"], trade["risk"])
print(f"Total Profit: {profit}")
print(f"Total Loss: {loss}")