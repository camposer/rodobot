from binance.client import Client
from enum import Enum
import numpy
import os
import pytest
import talib
from unittest.mock import MagicMock

def get_config():
    return {
        'API_KEY': os.getenv('BINANCE_API_KEY'),
        'API_SECRET': os.getenv('BINANCE_API_SECRET')
    }

class KlinesEnum(Enum):
    OPEN_TIME = 0
    OPEN = 1
    HIGH = 2
    LOW = 3
    CLOSE = 4
    VOLUME = 5
    CLOSE_TIME = 6
    QUOTE_ASSET_VOLUME = 7
    NUMBER_OF_TRADES = 8
    TAKER_BUY_BASE_ASSET_VOLUME = 9
    TAKER_BUY_QUOTE_ASSET_VOLUME = 10
    IGNORE = 11

class TrendEnum(Enum):
    UPWARD = 0
    DOWNWARD = 1
    SIDEWAYS = 3

class KlinesTimeSpan(Enum):
    THIRTY_MIN = "30 min ago UTC"
    FIVE_MIN = "5 min ago UTC"

class TradeService:
    def __init__(self, client):
        self.__client = client

    # Currently only considering UPWARD trend
    def is_moment_to_buy(self, ticker):
        general_prices = self.__get_closing_prices(ticker, KlinesTimeSpan.THIRTY_MIN)
        general_trend = self.__get_ema_trend(general_prices)
        if general_trend == TrendEnum.SIDEWAYS:
            return False

        instant_prices = self.__get_closing_prices(ticker, KlinesTimeSpan.FIVE_MIN)
        instant_trend = self.__get_ema_trend(instant_prices)
        if (
            instant_trend == TrendEnum.SIDEWAYS 
            or general_trend != instant_trend 
            or general_trend == TrendEnum.DOWNWARD # Not considering downward trends for now
        ): 
            return False

        # TODO Check RSI + Sthocastic
        return True

    def __get_closing_prices(self, ticker, time_span):
        klines = self.__client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE, time_span.value)
        return numpy.array([float(kline[KlinesEnum.CLOSE.value]) for kline in klines])

    def __get_ema_trend(self, prices):
        fast = talib.EMA(prices, timeperiod = 9)
        medium = talib.EMA(prices, timeperiod = 26)
        slow = talib.EMA(prices, timeperiod = 50)
        if self.__compare(fast, medium, numpy.greater) and self.__compare(medium, slow, numpy.greater):
            return TrendEnum.UPWARD
        elif self.__compare(fast, medium, numpy.less) and self.__compare(medium, slow, numpy.less):
            return TrendEnum.DOWNWARD
        return TrendEnum.SIDEWAYS

    def __compare(self, a, b, compare_fn):
        return compare_fn(
            a, b, 
            where = numpy.logical_not(numpy.logical_or(
                numpy.isnan(a), 
                numpy.isnan(b)
            ))
        ).all()

ticker = "BNBBTC"
mock_client = True # Change for specific tests 

class TestTradeService_UpwardTrend:
    @pytest.fixture
    def trade_service(self):
        client = create_client(get_historical_klines_upward)
        return TradeService(client)
        
    def test_is_moment_to_buy(self, trade_service):
        assert trade_service.is_moment_to_buy(ticker)

class TestTradeService_DownwardTrend:
    @pytest.fixture
    def trade_service(self):
        client = create_client(get_historical_klines_downward)
        return TradeService(client)
        
    def test_is_moment_to_buy(self, trade_service):
        assert not trade_service.is_moment_to_buy(ticker)

class TestTradeService_SidewaysTrend:
    @pytest.fixture
    def trade_service(self):
        client = create_client(get_historical_klines_sideways)
        return TradeService(client)
        
    def test_is_moment_to_buy(self, trade_service):
        assert not trade_service.is_moment_to_buy(ticker)


def create_client(get_historical_klines_fn):
    if not mock_client:
        config = get_config()
        return Client(config['API_KEY'], config['API_SECRET'])
    client = MagicMock()
    client.get_historical_klines = MagicMock(side_effect=get_historical_klines_fn)
    return client

def get_historical_klines_upward(ticker, interval, time_span):
    if time_span == KlinesTimeSpan.THIRTY_MIN.value:
        return [[None, None, None, None, i] for i in range(30)]
    else: # time_span == KlinesTimeSpan.FIVE_MIN.value:
        return [[None, None, None, None, i] for i in range(5)]
    
def get_historical_klines_downward(ticker, interval, time_span):
    if time_span == KlinesTimeSpan.THIRTY_MIN.value:
        return [[None, None, None, None, i] for i in range(29, 0, -1)]
    else: # time_span == KlinesTimeSpan.FIVE_MIN.value:
        return [[None, None, None, None, i] for i in range(4, 0, -1)]

def get_historical_klines_sideways(ticker, interval, time_span):
    if time_span == KlinesTimeSpan.THIRTY_MIN.value:
        return [[None, None, None, None, 1] for _ in range(30)]
    else: # time_span == KlinesTimeSpan.FIVE_MIN.value:
        return [[None, None, None, None, 1] for i in range(5)]
