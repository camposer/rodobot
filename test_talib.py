import talib
import numpy

def test_smoke_check():
  c = numpy.random.randn(100)
  # this is the library function
  k, d = talib.STOCHRSI(c)
  assert k is not None
  assert d is not None

def test_ema():
  c = numpy.random.randn(100)
  # this is the library function
  d = talib.EMA(c, timeperiod = 30)
  print(c)
  print(d)
  assert False
 
