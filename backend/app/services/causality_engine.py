import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
from typing import Dict, Any, List, Tuple
from datetime import datetime

class CausalityEngine:
    """
    Advanced econometric engine for validating relationships between narrative pulses
    and market movements. 
    
    Implements:
    1. Granger Causality: Statistical test for lead/lag predictive power.
    2. Elasticity Calculation: Quantifying % change delta.
    """

    def check_granger_causality(
        self, signal_series: List[float], target_series: List[float], maxlag: int = 3
    ) -> Dict[str, Any]:
        """
        Calculates if the signal (e.g. news volume) 'Granger-causes' the target (e.g. price).
        Returns p-values for different lags.
        """
        if len(signal_series) < 10 or len(target_series) < 10:
            return {"error": "Insufficient data points for Granger test (min 10 required)"}

        # Prepare DataFrame
        df = pd.DataFrame({
            'target': target_series,
            'signal': signal_series
        })
        
        # We must ensure the series is stationary for Granger.
        # For simplicity in this version, we take the first difference (percentage change)
        df_diff = df.pct_change().dropna()
        
        # Replace infs and NaNs resulting from pct_change
        df_diff.replace([np.inf, -np.inf], 0, inplace=True)
        df_diff.fillna(0, inplace=True)

        if len(df_diff) < 5:
            return {"error": "Insufficient data after differencing"}

        try:
            # grangercausalitytests expects [target, signal]
            test_result = grangercausalitytests(df_diff[['target', 'signal']], maxlag=maxlag, verbose=False)
            
            # Extract p-values for the 'ssr_chi2test' or 'ssr_fttest'
            lags_p = {}
            for lag, results in test_result.items():
                p_val = results[0]['ssr_chi2test'][1]
                lags_p[f"lag_{lag}"] = round(p_val, 4)
            
            # Identify if any lag is significant (< 0.05)
            best_p = min(lags_p.values())
            is_significant = best_p < 0.05
            
            return {
                "is_causal": is_significant,
                "confidence_score": round(1.0 - best_p, 4) if is_significant else 0.0,
                "p_values": lags_p,
                "method": "Granger Causality (SSR Chi2)"
            }
        except Exception as e:
            return {"error": str(e)}

    def calculate_elasticity(
        self, signal_avg: float, target_avg: float, signal_delta: float, target_delta: float
    ) -> float:
        """
        Returns the elasticity (E): % Change in Target / % Change in Signal.
        E > 1: Market is highly sensitive to the news signal.
        E < 1: Market is relatively inelastic to the news signal.
        """
        if signal_avg == 0 or signal_delta == 0: return 0.0
        
        pct_signal = (signal_delta / signal_avg)
        pct_target = (target_delta / target_avg) if target_avg != 0 else 0.0
        
        if pct_signal == 0: return 0.0
        return round(pct_target / pct_signal, 4)

causality_engine = CausalityEngine()
