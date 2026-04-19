import pandas as pd
import numpy as np

def get_portfolio_correlation(new_symbol_df, open_positions_dfs):
    """
    CHAPTER 10: THE CORRELATION MATRIX.
    Ensures the new asset isn't just a 'copy' of what we already own.
    """
    print("🧬 AWM CORRELATION ENGINE: Auditing Risk De-coupling...")

    if not open_positions_dfs:
        return 0.0 # No correlation if portfolio is empty

    correlations = []
    # Calculate daily percent change (returns)
    new_returns = new_symbol_df['close'].pct_change().dropna()

    for symbol, df in open_positions_dfs.items():
        pos_returns = df['close'].pct_change().dropna()

        # Align dataframes to the same date range
        combined = pd.concat([new_returns, pos_returns], axis=1).dropna()
        if combined.empty: continue

        # Calculate Pearson Correlation
        corr = combined.corr().iloc[0, 1]
        correlations.append(corr)
        print(f" - Correlation with {symbol}: {corr:.2f}")

    # Return the highest correlation found (we care about the worst-case overlap)
    max_corr = max(correlations) if correlations else 0
    return max_corr
