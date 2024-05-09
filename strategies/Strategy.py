import pandas as pd

class Strategy:
    """Base strategy for inheritance, requires data for strategy to be passed at initialization"""
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def generate_signals(self) -> pd.Series:
        """
        Generate signals based on the pre-stored data.

        Returns:
            A pandas Series of floats (signals) between -1 and 1 where, 
            -1 indicates the strongest sell signal & 1 indicates the strongest buy signal 
        """
        raise NotImplementedError("Should implement generate_signals() method.")
