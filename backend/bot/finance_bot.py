# bot/finance_bot.py

def analyze_stock(financials):
    """
    financials: dict with keys
    revenue_growth, profit_consistency, debt_level,
    promoter_holding_trend, valuation, key_risks, business_model
    """

    score = 0
    reasoning = []

    # Business model clarity
    if financials['business_model'] == "clear":
        score += 1
        reasoning.append("Business model is clear.")
    else:
        reasoning.append("Business model unclear.")

    # Revenue growth
    if financials['revenue_growth'] > 0.1:
        score += 1
        reasoning.append("Revenue growth trend is positive.")
    else:
        reasoning.append("Revenue growth is weak.")

    # Profit consistency
    if financials['profit_consistency'] > 0.8:
        score += 1
        reasoning.append("Profit has been consistent.")
    else:
        reasoning.append("Profit is volatile.")

    # Debt level
    if financials['debt_level'] < 0.5:
        score += 1
        reasoning.append("Debt level is manageable.")
    else:
        reasoning.append("Debt level is high.")

    # Promoter holding trend
    if financials['promoter_holding_trend'] > 0:
        score += 1
        reasoning.append("Promoter holding trend is positive.")
    else:
        reasoning.append("Promoter holding is decreasing.")

    # Valuation
    if financials['valuation'] == "undervalued":
        score += 1
        reasoning.append("Valuation looks attractive.")
    else:
        reasoning.append("Valuation seems high.")

    # Key risks
    if financials['key_risks'] == "low":
        score += 1
        reasoning.append("Key risks are low.")
    else:
        reasoning.append("Key risks present.")

    # Final verdict
    if score >= 5:
        verdict = "Buy ✅"
    elif score >= 3:
        verdict = "Watch ⏳"
    else:
        verdict = "Avoid ❌"

    return verdict, "\n".join(reasoning)
