# coding=utf-8
from PySide2.QtCore import Qt
from PySide2.QtCore import QDateTime
from decimal import Decimal
import datatypes
import codecs
import re

ASSET_INFO = ["Financial Instrument Information","Информация о финансовом инструменте"]
CORPORATE_ACTIONS = ["Corporate Actions"]
OPEN_POSITIONS = ["Open Positions","Открытые позиции"]
TRADES = ["Trades","Сделки"]
DATA = ["Data"]
ORDER = ["Order"]
STOCKS = ["Stocks","Акции"]
FUTURES = ["Futures","Фьючерсы"]
BONDS = ["Bonds","Облигации"]
FOREX = ["Forex"]

#__corp_action_rexp = re.compile("Data,Stocks,[^,]*,[^,]*,[^,]*,[^,]*,\"([^(]*)[^ ]* CUSIP\/ISIN Change to \([^(]*\(([^,]*)")
__corp_action_split_rexp = re.compile("([^(]*)\(([^)]*)\) ([^(]*) \(([^,]*), [^,]*, ([^)]*).*")
__corp_action_change_rexp = re.compile("([^(]*)\(([^)]*)\) ([^(]*) \(([^)]*)\) \(([^,]*), [^,]*, ([^)]*).*")

def _splitCsvLine(s:str):
    arr = []
    if len(s)==0:
        return arr
    ignoreComma = False
    closePos = 0
    first = 0
    for i in range(len(s)):
        c = s[i]
        if ignoreComma:
            if c=='\"':
                ignoreComma = False
                closePos = i
        else:
            if c==',':
                end = closePos if closePos>0 else i
                arr.append(s[first:end])
                first = i+1
                closePos = 0
            elif c=='\"':
                ignoreComma = True
                first = i+1
    if first<=len(s):
        arr.append(s[first : closePos if closePos>0 else len(s)])
    return arr

def _parseDateTime(s):
    dt = QDateTime.fromString(s,"yyyy-MM-dd, hh:mm:ss")  # 2020-12-07, 09:50:16
    dt.setTimeSpec(Qt.UTC)
    return dt

def _parseDealType(sTypes:str, assetClass):
    types = sTypes.strip().split(';')
    dt = datatypes.DealType.NONE
    # 'P' # Partial
    if 'O' in types: dt |= datatypes.DealType.OPEN_DEAL
    if 'C' in types: dt |= datatypes.DealType.CLOSE_DEAL
    if dt==datatypes.DealType.NONE and assetClass!=datatypes.AssetClass.FOREX:
        raise Exception("Unknown deal type: "+sTypes)
    return dt

def _parseAssetClass(asset):
    if asset in STOCKS:     return datatypes.AssetClass.STOCKS
    if asset in FUTURES:    return datatypes.AssetClass.FUTURES
    if asset in BONDS:      return datatypes.AssetClass.BONDS
    if asset in FOREX:      return datatypes.AssetClass.FOREX
    else:                   raise Exception("Unknown asset type "+asset)

def _parseTradeDataOrderLine(l):
    deal = datatypes.Deal()
    deal.assetClass = _parseAssetClass(l[0])
    deal.currency = l[1].upper()
    deal.origTicker = l[2].upper()
    deal.dateTime = _parseDateTime(l[3])
    deal.count = Decimal(l[4].replace(',',''))
    deal.price = Decimal(l[5])
    deal.proceeds = Decimal(l[7])
    deal.fee = Decimal(l[8])
    deal.dealType = _parseDealType(l[12], deal.assetClass)
    return deal

def _parseInfoDataLine(l):
    info = datatypes.InstrumentInfo()
    info.assetClass = _parseAssetClass(l[2])
    info.ticker = l[3].replace(' ','').upper().split(',')  # Can be several: "NCPL, VSTRD"
    info.name = l[4]
    info.conid = l[5]  # Conid
    info.securityid = l[6]  # Security ID
    info.exchange = l[7]  # Listing Exch
    info.multiplier = l[8]  # Multiplier
    assert(int(info.multiplier)==1)  # TODO: WTF multiplier is?
    info.type = l[9]  # Type
    code = l[10]
    #assert (len(code) == 0)  # TODO: WTF code is? X on BOND X Corp US912909AN84
    return info

def _parseCorporateAction(l):
    if l[2] == "Total": return None
    assert(l[2] in STOCKS)  # TODO: Process other Asset Category for Corporate Actions.
    deal = datatypes.Deal()
    deal.assetClass = datatypes.AssetClass.STOCKS
    deal.dateTime = _parseDateTime(l[5])
    deal.description = l[6]
    deal.count = Decimal(l[7])
    deal.currency = l[3]
    assert(l[8] == '0')  # TODO: how to process?
    assert(l[9] == '0')
    assert(l[10] == '0')
    assert(l[11] == '')
    if "Split" in deal.description:
        m = __corp_action_split_rexp.search(deal.description)
        assert (m is not None)
        deal.dealType = datatypes.DealType.SPLIT
        deal.origTicker = m.group(4).upper()
        deal.ticker = m.group(1).upper()
    elif "CUSIP/ISIN Change" in deal.description:
        m = __corp_action_change_rexp.search(deal.description)
        assert (m is not None)
        deal.dealType = datatypes.DealType.RENAME
        deal.origTicker = m.group(5).upper()
        deal.ticker = m.group(1).upper()
    else: assert(False)
    return deal

# Find last actual tickers for renamed ticker sets.
def _generateTickerRenameMap(tickers, openPositions, deals):
    renmap = {}
    tickersets = {id(t):t for t in tickers.values()}.values()
    for tickerset in tickersets:
        # Find in open positions first. Open positions is the last actual info.
        actualTicker = None
        for ticker in tickerset:
            if ticker in openPositions:
                assert(actualTicker is None)  # Must survive only one.
                actualTicker = ticker
        # If not fount - look at last deal with this ticker.
        if actualTicker is None:
            for deal in reversed(deals):
                if deal.origTicker in tickerset:
                    actualTicker = deal.origTicker
                    break
        # Generate map.
        assert (actualTicker is not None)
        for ticker in tickerset:
            if actualTicker != ticker:
                renmap[ticker] = actualTicker
    return renmap

def parseIbReportCsv(filename):
    year = None
    infos = {}
    deals = []
    corporateActions = []
    tickerSetDict = {}
    openPositions = set()

    f = codecs.open(filename, encoding="utf-8")
    # TODO: Skip beginning \ueff unicode mark.

    for line in f:
        l = _splitCsvLine(line.strip())
        if len(l)==0: continue
        if len(l)<2: continue
        if not l[1] in DATA: continue
        head = l[0]
        if head in TRADES and l[2] in ORDER:
            deal = _parseTradeDataOrderLine(l[3:])
            if deal is not None:
                deals.append(deal)
        elif head in ASSET_INFO:
            info = _parseInfoDataLine(l)
            if info is not None:
                for ticker in info.ticker:
                    if ".OLD" not in ticker:  # It seems .OLD is used only in Corporate Actions and Financial Instrument Information.
                        infos[ticker] = info
        elif head in OPEN_POSITIONS:
            openPositions.add(l[5])
        elif head in CORPORATE_ACTIONS:
            deal = _parseCorporateAction(l)
            if deal is not None:
                corporateActions.append(deal)
                tickerAliases = None
                if deal.origTicker in tickerSetDict:
                    tickerAliases = tickerSetDict[deal.origTicker]
                elif deal.ticker in tickerSetDict:
                    tickerAliases = tickerSetDict[deal.ticker]
                else:
                    tickerAliases = set()
                tickerAliases.add(deal.origTicker)
                tickerAliases.add(deal.ticker)
                tickerSetDict[deal.origTicker] = tickerSetDict[deal.ticker] = tickerAliases
        if head == "Statement" and l[2] == "Period":
            year = int(l[3].split('-')[0].split(',')[1].strip())
            yearEnd = int(l[3].split('-')[1].split(',')[1].strip())
            assert(year == yearEnd)
    f.close()
    renameMap = _generateTickerRenameMap(tickerSetDict, openPositions, deals)  # Before corporate actions joining.
    deals += corporateActions
    return year, infos, deals, renameMap

if __name__ == '__main__':
    year, infos, deals, renameMap = parseIbReportCsv('c:/Users/dokvo/3ndfl_reports/my/2020.csv')
    for info in infos:
        print(info,': ',infos[info])
#    _splitCsvLine(", 2 ,\"3,3,3\", \"4,\" ,5")
#    _splitCsvLine("0, 2 ,\"3\", \"4\" ,")