from fastapi import APIRouter, HTTPException, Query
from wallet_manager import wallet_manager, SUPPORTED_CHAINS

router = APIRouter()

@router.post("/wallet/create")
def create_wallet(chain: str = Query(..., description="Chain name (e.g., ethereum, bsc, polygon)")):
    try:
        address = wallet_manager.create_wallet(chain)
        return {"chain": chain, "address": address}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/wallet/address")
def get_wallet_address(chain: str):
    wallet = wallet_manager.get_wallet(chain)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"chain": chain, "address": wallet["address"]}

@router.get("/wallet/balance")
def get_wallet_balance(chain: str):
    balance = wallet_manager.get_balance(chain)
    if balance is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"chain": chain, "balance": str(balance)}

@router.get("/wallet/profit")
def get_profit(chain: str):
    profit = wallet_manager.profit_ledger.get(chain, 0.0)
    return {"chain": chain, "profit": profit}

@router.post("/wallet/profit/add")
def add_profit(chain: str, amount: float):
    wallet_manager.add_profit(chain, amount)
    return {"chain": chain, "profit": wallet_manager.profit_ledger[chain]}

@router.post("/wallet/profit/withdraw")
def withdraw_profit(chain: str, to_address: str, amount: float):
    try:
        wallet_manager.withdraw_profit(chain, to_address, amount)
        return {"chain": chain, "profit": wallet_manager.profit_ledger[chain]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))