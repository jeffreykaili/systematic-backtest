import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.realpath(__file__))
if current_dir not in sys.path: 
    sys.path.insert(0, current_dir)
from Strategy import Strategy

class EWMACrossover(Strategy):
    """
    Class to implement exponentially weighted moving average (EWMA) crossover strategy.
    Idea is that fast EWMA responds more greatly to recent price changes, while slow EWMA 
    is less responsive and represents longer-term trends. Thus, when the fast EWMA crosses 
    the slow EWMA, this indicates upwards momentum (buy signal) and vice versa. 
    """
    
    def __init__(
        self, 
        data: pd.DataFrame, 
        fast_window: int = 9, # Number of days for fast EWMA
        slow_window: int = 21, # Number of days for slow EWMA
        show_crossover_graphs = False,
    ):
        self.data = data
        assert fast_window < slow_window, "Fast window must be shorter than slow window."
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.show_crossover_graphs = show_crossover_graphs

    @staticmethod
    def calculate_EWMA(
        data: pd.Series,
        half_life: float,
    ) -> float:
        """
        Calculate EWMA of data, with half-life `half_life`.

        Parameters: 
            data (pd.Series): series used for EWMA calculation
            half_life (float): the number of points at which the weighting factor 
                               for the data points decays to half of its original value
        """
        def half_life_to_alpha(half_life):
            return 1 - np.exp(-np.log(2) / half_life)
        alpha = half_life_to_alpha(half_life)

        data = data.to_list()
        ewma = []

        for i, px in enumerate(data):
            if i == 0:
                ewma.append(px)
                continue 
            cur_ewma = alpha * px + (1 - alpha) * ewma[i - 1]
            ewma.append(cur_ewma)
        
        return ewma[-1]
    
    def generate_signals(self) -> pd.Series:
        """
        Generate signals based on EWMA crossovers:
        - Buy signal when fast EWMA crosses above slow EWMA.
        - Sell signal when fast EWMA crosses below slow EWMA.
        """

        signals = pd.Series(index=self.data.index, data=np.nan)

        if self.show_crossover_graphs: 
            fst = pd.Series(index=self.data.index, data=np.nan)
            slow = pd.Series(index=self.data.index, data=np.nan)
            px = self.data['Close']

        for end_date in self.data.index[self.slow_window:]:
            fast_EWMA = self.calculate_EWMA(self.data.loc[:end_date]['Close'], self.fast_window)
            slow_EWMA = self.calculate_EWMA(self.data.loc[:end_date]['Close'], self.slow_window)

            if self.show_crossover_graphs: 
                fst.at[end_date] = fast_EWMA
                slow.at[end_date] = slow_EWMA

            # Use signed only signals for now 
            if fast_EWMA > slow_EWMA:
                signals.at[end_date] = 1
            else:
                signals.at[end_date] = -1

        if self.show_crossover_graphs: 
            plt.figure(figsize=(10, 5))  
            px.plot(label='Price Data', color='gray')
            fst.plot(label='Fast EWMA', color='red') 
            slow.plot(label='Slow EWMA', color='blue')

            plt.title('Price and EWMA Crossover')
            plt.xlabel('Date') 
            plt.ylabel('Value')
            plt.legend()  
            plt.grid(True) 
            plt.show() 

        return signals
    
if __name__ == "__main__":
    from FinanceDataReader import FinanceDataReader
    data_reader = FinanceDataReader()

    df = data_reader.get_historical_data("GOOG")
    crossover = EWMACrossover(df, show_crossover_graphs=True)
    crossover.generate_signals()
