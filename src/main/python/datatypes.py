from PySide2.QtCore import QFlag
import enum

# Класс актива
class AssetClass(enum.Enum):
    STOCKS = 0
    FUTURES = 1
    BONDS = 2
    FOREX = 3

    def tostr(asset):
        #if asset == None:               return ""
        if asset == AssetClass.STOCKS:  return "Акция"
        if asset == AssetClass.FUTURES: return "Фьючерс"
        if asset == AssetClass.BONDS:   return "Облигация"
        if asset == AssetClass.FOREX:   return "Форекс"
        assert 0

    def __str__(self):
        return AssetClass.tostr(self)

# Код
@QFlag
class DealType(enum.Flag):
    NONE = 0
    # Deals
    OPEN_DEAL = enum.auto()
    CLOSE_DEAL = enum.auto()
    # Corporate Actions
    SPLIT = enum.auto()
    RENAME = enum.auto()

    def tostr(dealType):
        s = ""
        if bool(dealType & DealType.SPLIT):      return "SPLIT"
        if bool(dealType & DealType.RENAME):     return "RENAME"
        if bool(dealType & DealType.OPEN_DEAL):  s += "O,"
        if bool(dealType & DealType.CLOSE_DEAL): s += "C,"
        s = s[:-1]
        return s

    def __str__(self):
        return DealType.tostr(self)

class InstrumentInfo:
    def __init__(self):
        self.assetClass = None
        self.ticker = None
        self.name = None
        self.exchange = None
        self.type = None

    def __str__(self):
        return "Asset: {} Ticker: {} Name: {} Exchenge: {} Type: {}"\
            .format(self.assetClass,self.ticker,self.name,self.exchange,self.type)

class Deal:
    def __init__(self):
        self.assetClass = None
        self.currency = None
        self.ticker = None  # Current ticker after renaming
        self.origTicker = None  # Original deal ticker
        self.dateTime = None
        self.count = None
        self.price = None
        self.proceeds = None
        self.fee = None
        self.dealType = None
        # Duplicated field
        self.rate = None
        # Calculated fields
        self.total = None
        self.totalRub = None

    def __str__(self):
        return "Asset: {} Currency: {} Ticker: {}({}) DT: {} Count: {} Price: {} Fee: {} Open: {} Rate: {}"\
            .format(self.assetClass,self.currency,self.ticker,self.origTicker,self.dateTime.toString("yyyy-MM-dd hh:mm:ss"),self.count,self.price,self.fee,self.dealType,self.rate)

class OpenDeal:
    def __init__(self, deal:Deal):
        self.deal = deal
        self.left = deal.count
        # don't remember why it is here: self.count = None # If count != 0 - there is absent open deals (from previous periods?)

class Take:
    def __init__(self, closeDeal:Deal):
        self.count = None
        self.openDeals = []
        self.closeDeal = closeDeal

        self.proceeds = None
        self.proceedsRub = None
        self.tax = None

    def __str__(self):
        s = self.closeDeal.__str__()
        s += '\n' + "Count: {}".format(self.count)
        for deal in self.openDeals:
            s += "\n===="
            s += deal.__str__()
        return s