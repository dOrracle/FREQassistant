import pandas as pd
from typing import Dict, Any, List
import random
from datetime import datetime, timedelta
import time

class SimulatedExchange:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data = self._generate_initial_data()
        self.open_trades = []
        self.trade_id_counter = 1
        self.balance = 1000  # Initial balance

    def _generate_initial_data(self) -> Dict[str, pd.DataFrame]:
        """Generates initial historical data for the pairs."""
        data = {}
        for pair in self.config['exchange']['pair_whitelist']:
            # Create 100 data points for each pair
            index = pd.date_range(datetime.now() - timedelta(days=100), periods=100, freq='D')
            df = pd.DataFrame(
                {
                    'open': [random.uniform(10, 20) for _ in range(100)],
                    'high': [random.uniform(20, 30) for _ in range(100)],
                    'low': [random.uniform(5, 10) for _ in range(100)],
                    'close': [random.uniform(10, 20) for _ in range(100)],
                    'volume': [random.uniform(1000, 2000) for _ in range(100)],
                    'previous_close': [random.uniform(10,20) for _ in range (100)]
                },
                index=index
            )
            df['pair'] = pair  # Add the pair as a column
            data[pair] = df
        return data

    async def get_tickers(self) -> Dict[str, Any]:
        """Simulates fetching live ticker data."""
        tickers = {}
        for pair in self.config['exchange']['pair_whitelist']:
            last_data = self.data[pair].iloc[-1].to_dict()  # Get the last row
            # Simulate price movement
            change_percent = random.uniform(-0.05, 0.05)  # Up to +/- 5% change
            last_data['last'] = last_data['close'] * (1 + change_percent)
            last_data['open'] = last_data['close']
            last_data['high'] = max(last_data['last'], last_data['open']) + random.uniform(0, 2)
            last_data['low'] = min(last_data['last'], last_data['open']) - random.uniform(0, 2)
            #Add previous close for market analysis
            last_data['previous_close'] = last_data['close']
            last_data['close'] = last_data['last']  # Update close to be the same as last
            last_data['volume'] = last_data['volume'] * random.uniform(0.9, 1.1)  # Slight volume change
            tickers[pair] = last_data

            # Update the stored data with the new values
            self.data[pair] = pd.concat([self.data[pair], pd.DataFrame([last_data], index=[datetime.now()])])

        return tickers

    def get_historical_data(self, pair: str, timeframe: str = '1d', limit: int = 100) -> pd.DataFrame:
        """Returns historical data for a pair (simulated)."""
        return self.data[pair].tail(limit)

    def buy(self, pair: str, amount: float, price: float) -> Dict[str, Any]:
        """Simulates a buy order."""
        if self.balance >= amount * price:
            self.balance -= amount * price
            trade = {
                'trade_id': self.trade_id_counter,
                'pair': pair,
                'amount': amount,
                'price': price,
                'timestamp': time.time(),
                'open': True
            }
            self.open_trades.append(trade)
            self.trade_id_counter += 1
            return trade
        else:
            return {'error': 'Insufficient balance'}

    def sell(self, trade_id: int, price: float) -> Dict[str, Any]:
        """Simulates a sell order."""
        for i, trade in enumerate(self.open_trades):
            if trade['trade_id'] == trade_id and trade['open']:
                self.balance += trade['amount'] * price
                trade['sell_price'] = price
                trade['sell_timestamp'] = time.time()
                trade['profit'] = (price - trade['price']) * trade['amount']
                trade['open'] = False  # Mark trade as closed
                self.open_trades[i] = trade # Update the trade
                return trade
        return {'error': 'Trade not found or already closed'}

    def get_open_trades(self) -> List[Dict[str, Any]]:
        """Returns a list of open trades."""
        return [trade for trade in self.open_trades if trade['open']]

    def get_performance(self) -> Dict[str, Any]:
        """Simulates performance metrics."""
        total_profit = sum((trade.get('profit',0)) for trade in self.open_trades)
        num_trades = len(self.open_trades)
        winning_trades = sum(1 for trade in self.open_trades if trade.get('profit', 0) > 0)
        win_rate = (winning_trades / num_trades) if num_trades > 0 else 0.0
        return {
            'profit': total_profit,
            'trades': num_trades,
            'win_rate': win_rate
        }

class SimulatedFreqAIModel:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def predict(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Simulates FreqAI predictions."""
        # Generate some random predictions
        num_rows = 1  # We're only predicting for the current time step
        predictions = pd.DataFrame(
            {
                "pair": [random.choice(self.config['exchange']['pair_whitelist']) for _ in range(num_rows)],
                "predicted_buy": [random.uniform(0, 1) for _ in range(num_rows)],
                "predicted_sell": [random.uniform(0, 1) for _ in range(num_rows)],
                "confidence_buy": [random.uniform(0, 1) for _ in range(num_rows)],
                "confidence_sell": [random.uniform(0, 1) for _ in range(num_rows)],
            },
            index = [datetime.now()]
        )
        return predictions

    def train_and_test(self) -> Dict[str, Any]:
        """Simulates training and testing the model."""
        return {
                "profit": random.uniform(-0.1, 0.1),  # Simulate profit between -10% and +10%
                "trades": random.randint(5, 20),
                "win_rate": random.uniform(0.3, 0.7),
            }
