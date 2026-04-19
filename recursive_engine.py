from vault import SessionLocal, PerformanceAudit
from sqlalchemy import func

def get_recursive_weights():
    """
    CHAPTER 6: RECURSIVE INTELLIGENCE.
    Analyzes past performance to adjust current sensor weights.
    """
    print("🧠 AWM RECURSIVE ENGINE: Auditing Past Performance...")
    db = SessionLocal()
    try:
        # Analyze last 20 trades
        last_trades = db.query(PerformanceAudit).order_by(PerformanceAudit.timestamp.desc()).limit(20).all()

        if len(last_trades) < 5:
            return {"whale_weight": 1.0, "tech_weight": 1.0, "fund_weight": 1.0}

        # Calculate which sensor correlates with WINNING
        wins = [t for t in last_trades if t.result == 'WIN']

        # Simple Logic: If average whale_score of wins is high, keep it.
        # If losses have high whale_scores, the whales are 'Trapping' us.
        whale_reliability = 1.0
        losses = [t for t in last_trades if t.result == 'LOSS']

        avg_loss_whale = sum(t.whale_score for t in losses) / len(losses) if losses else 0
        if avg_loss_whale > 2.0:
            print("⚠️ RECURSIVE ALERT: High Whale Score detected in Losses. Reducing Whale Weight.")
            whale_reliability = 0.5 # Put whales on probation

        return {"whale_weight": whale_reliability, "tech_weight": 1.0, "fund_weight": 1.0}
    finally:
        db.close()