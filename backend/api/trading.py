from fastapi import APIRouter, HTTPException, status

router = APIRouter()

# Example strategies for toggling
STRATEGIES = ["grid", "scalping", "swing", "dca", "momentum", "arbitrage"]

# In-memory state for toggles (for demonstration)
strategy_states = {strategy: False for strategy in STRATEGIES}
perpetual_mode = {"enabled": False}

@router.post("/strategies/{strategy}/toggle")
def toggle_strategy(strategy: str):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=404, detail="Strategy not found")
    strategy_states[strategy] = not strategy_states[strategy]
    return {"strategy": strategy, "enabled": strategy_states[strategy]}

@router.post("/perpetual-mode/toggle")
def toggle_perpetual_mode():
    perpetual_mode["enabled"] = not perpetual_mode["enabled"]
    return {"perpetual_mode": perpetual_mode["enabled"]}
@router.get("/strategies")
def get_strategies():
    # Return the current state of all strategies
    return {"strategies": strategy_states}

@router.get("/market-condition")
def get_market_condition():
    # Dummy data for demonstration
    return {
        "market": "BTC/USDT",
        "condition": "bullish",
        "price": 65000,
        "volume": 123456,
        "timestamp": "2025-04-12T19:20:00Z"
    }