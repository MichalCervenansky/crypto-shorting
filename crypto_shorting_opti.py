import backtrader as bt
import backtrader.feeds as btfeeds
import numpy as np

class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 5),
        ('slope_ma_period', 2),
        ('slope_diff', 0.007)
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)
        self.slope_sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slope_ma_period)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        # print('%s, %s' % (dt, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def stop(self):
        print('(%2d %2d %4f):%.2f' % (
            self.params.maperiod, self.params.slope_ma_period, self.params.slope_diff,
            self.broker.getvalue() - start_cash))

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Not trading while MAs are not computed
        if len(self) < self.params.slope_ma_period + self.params.maperiod:
            return
        # Difference between actual MA and MA slope_ma_period before
        diff = (self.slope_sma[0] / self.slope_sma[-1 * self.params.slope_ma_period] - 1) / self.params.slope_ma_period
        if not self.position:
            # If actual price > smooth moving average
            if self.dataclose[0] > self.sma[0]:
                # If difference between actual MA and MA slope_ma_period before is bigger then some threshold
                if diff > self.params.slope_diff:
                    self.order = self.buy(
                        size=cerebro.broker.get_cash() // (data.close[0] * (1 + 2 * commission)))
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
        else:
            if self.dataclose[0] < self.sma[0]:
                if diff < -1 * self.params.slope_diff:
                    self.order = self.sell(size=self.position.size)
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    start_cash = 100000000.0
    cerebro.broker.setcash(start_cash)

    commission = 0.001
    cerebro.broker.setcommission(commission=commission)

    data = btfeeds.GenericCSVData(dataname='btcsideways.csv', dtformat=('%Y-%m-%d %H:%M:%S'),
                                  timeframe=bt.TimeFrame.Minutes,
                                  datetime=0,
                                  high=3,
                                  low=4,
                                  open=1,
                                  close=2,
                                  volume=5,
                                  openinterest=-1)

    cerebro.adddata(data)

    strats = cerebro.optstrategy(
        MyStrategy,
        maperiod=range(3, 10, 1),
        slope_ma_period=range(3, 10, 1),
        slope_diff=np.arange(0.001, 0.005, 0.0005))

    stats = cerebro.run()
