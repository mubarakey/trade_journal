def calculate_profit(risk, result_r):
    return risk * result_r
def calculate_loss(risk, result_r):
    return risk * result_r

trade = []
#a loop for asking user input
while True:
    pair = input("Enter the currency pair (or type 'exit' to finish): ")
    if pair.lower() == 'exit':
        break
    direction = input("BUY/SELL: ")
    risk = float(input("Enter the risk amount: "))
    result_r = float(input("Enter the result(r): "))
trades = [
    {
        "pair": pair,
        "direction": direction,
        "risk": risk,
        "result_r": result_r
    }

]



trade.append(trades)

for i in trades:
    if i["result_r"] > 0:
        profit = calculate_profit(i["result_r"], i["risk"])
    else:
        loss = calculate_loss(i["result_r"], i["risk"])
print(f"Total Profit: {profit}")
print(f"Total Loss: {loss}")