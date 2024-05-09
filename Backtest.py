from strategies.Strategy import Strategy
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 
from scipy.stats import norm
from prettytable import PrettyTable

class Backtest:
    """
    Backtest class to calculate historic performance (P&L, volatility, risk (ETL), etc.) 
    of a systematic strategy. 
    """
    def __init__(
        self, 
        strategy: Strategy, 
        data: pd.DataFrame, 
        column_name: str = "Price",
        initial_capital: int=10000.0
    ):
        # Class uses 'Price' column for price data, unless `column_name` is specified
        self.data = data
        self.strategy = strategy(data)
        self.column_name = column_name
        self.initial_capital = initial_capital

    def run(self):
        self.data['base_signal'] = self.strategy.generate_signals()
        # Shift by 1 since signal uses price data up to current index 
        self.data['signal'] = self.data['base_signal'].shift(1) 
        self.data['position'] = self.data['signal'] * self.initial_capital
        self.data['position'] = np.nan

        fvi = self.data['signal'].first_valid_index()
        if fvi is None:
            raise Exception("All signals are NaN!")

        self.data['Percent Change'] = self.data[self.column_name].pct_change()

        self.data.at[fvi, 'position'] = self.initial_capital * self.data.loc[fvi, 'signal']
        self.data['P&L'] = np.nan 
        self.data.at[fvi, 'P&L'] = self.data.at[fvi, 'position'] * self.data.at[fvi, 'Percent Change'] 

        fvi_index = self.data.index.get_loc(fvi)
        for idx in range(fvi_index + 1, len(self.data)):
            i = self.data.index[idx]
            prev_i = self.data.index[idx - 1]
            prev_pos = self.data.at[prev_i, 'position']
            prev_pnl = self.data.at[prev_i, 'P&L']
            self.data.at[i, 'position'] = abs(prev_pos) + prev_pnl
            self.data.at[i, 'position'] *= self.data.loc[fvi, 'signal']
            self.data.at[i, 'P&L'] = self.data.at[i, 'position'] * self.data.at[i, 'Percent Change'] 

        self.data['P&L'] = self.data['P&L'].fillna(0)
        self.data['Cumulative P&L'] = self.data['P&L'].cumsum()

        self.data['Mean Return Percent'] = self.data['signal'].mul(self.data['Percent Change'])
        print(self.data)

        mean_return = self.data.loc[fvi:, 'Mean Return Percent'].mean()
        std = self.data.loc[fvi:, 'Mean Return Percent'].std()
        z_score = norm.ppf(0.01)
        estimated_tail_loss = mean_return + (z_score * std)

        print("Values given as a percentage!")
        table = PrettyTable()
        table.field_names = ["Data", "Value"]
        table.add_row(["Principal Investment", self.initial_capital])
        table.add_row(["Mean Return", mean_return])
        table.add_row(["Standard Deviation", std])
        table.add_row(["ETL (risk)", estimated_tail_loss])
        print(table)
        
        x = np.arange(0, len(self.data['Mean Return Percent']))
        y_mean = np.full_like(x, mean_return)
        plt.figure(figsize=(10, 6))  
        plt.plot(x, y_mean, 'k-', label='Mean P&L')
        plt.plot(x, self.data['Mean Return Percent'], 'g-', label='P&L (%)', linewidth=2)
        
        colors = ['blue', 'red', 'green', 'purple', 'orange']  
        alpha_values = [0.1 + 0.03 * i for i in range(5, 0, -1)]  
        for i in range(1, 6):  
            y_plus_sd = y_mean + i * std
            y_minus_sd = y_mean - i * std
            plt.fill_between(x, y_minus_sd, y_plus_sd, color=colors[i - 1], alpha=alpha_values[i - 1], label=f'±{i} SD')
        
        plt.title('P&L Cone Chart')
        plt.xlabel('Date')
        plt.ylabel('P&L (%)')
        plt.legend()
        plt.show()

        plt.figure(figsize=(10, 5))  
        self.data['position'].plot(label='Value', color='red') 
        plt.title('Portfolio Value')
        plt.xlabel('Date') 
        plt.ylabel('Value')
        plt.legend()  
        plt.grid(True) 
        plt.show() 

if __name__ == "__main__":
    from utils.FinanceDataReader import FinanceDataReader
    data_reader = FinanceDataReader()

    df = data_reader.get_historical_data("AAPL")
    
    from strategies.EWMACrossoverStrategy import EWMACrossover
    pd.set_option('display.max_rows', None)
    bt = Backtest(EWMACrossover, df, column_name='Close')
    bt.run()