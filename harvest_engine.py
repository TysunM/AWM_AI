def calculate_harvest_signals(symbol, current_price, entry_price, initial_atr):
    """
    CHAPTER 11: THE HARMONIC HARVEST.
    Determines if we should scale out of a position.
    """
    # Distance of the initial risk (The Shield distance from Ch. 8)
    risk_distance = initial_atr * 3

    # Target 1: 1:1 Risk/Reward Ratio
    target_1 = entry_price + risk_distance

    # Check if we've crossed the milestone
    if current_price >= target_1:
        return {
            "action": "HARVEST_PARTIAL",
            "amount": 0.50, # Sell 50%
            "new_stop": entry_price, # Move remaining to Breakeven
            "label": "PT1_REACHED"
        }

    return {"action": "HOLD", "label": "GROWING"}