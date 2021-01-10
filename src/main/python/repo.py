from PySide2.QtCore import QDateTime
from PySide2.QtCore import QDate
from decimal import Decimal
import currencyrates
import datatypes
import storage

def _getDealDateDiapason(deals):
    diapasons = {}
    for deal in deals:
        if deal.currency not in diapasons:
            diapasons[deal.currency] = (QDateTime.currentDateTimeUtc(), QDateTime())
        dtfrom = diapasons[deal.currency][0]
        dtto = diapasons[deal.currency][1]
        if deal.dateTime < dtfrom:
            diapasons[deal.currency] = (deal.dateTime, dtto)
        if deal.dateTime > dtto:
            diapasons[deal.currency] = (dtfrom, deal.dateTime)
    return diapasons

class Repo:
    def __init__(self):
        self._infos = {}  # Dict ticker/Financial instrument information
        self._currencyRates = storage.loadCurrencyRates()  # Dict of "currency - dict QDate/price_in_rub"
        self._deals = []  # List of all deals
        self._takes = []  # Dict ticker/take
        self._calc = []
        self._totalTaxRub = 0  # Whole Rub tax

    def clear(self):
        self.__init__()

    """ibreports - list of csv report file paths"""
    def addIbReports(self, ibreports):
        self.clear()
        allrenames = {}
        import reportparser
        for report in ibreports:
            year,infos,deals,renames = reportparser.parseIbReportCsv(str(report))
            self._infos.update(infos)
            self._deals += deals
            assert(year not in allrenames)
            allrenames[year] = renames
        self._renameTickers(allrenames)
        self._sortDeals()
        self._updateRates()
        self._updateTotal()
        self._updateTakes()
        #self._updateTakeProceeds()
        storage.storeCurrencyRates(self._currencyRates)

    def getRate(self, currency:str, date:QDate):
        rates = self._currencyRates[currency]
        d = date.date() if type(date) is QDateTime else date
        if d not in rates:
            rate = currencyrates.getCbRate(currency, d)
            rates[d] = rate
            return rate
        return rates[d]

    def otcReport(self):
        txt = ""
        class SummaryTake(object):
            def __init__(self):
                self.ticker = None
                self.sum = Decimal(0)
                self.gain = Decimal(0)
        total = SummaryTake()
        curr = SummaryTake()
        for take in self._takes:
            if take.left != 0: continue  # All open deals was not found.
            if take.closeDeal.assetClass != datatypes.AssetClass.STOCKS: continue
            if take.closeDeal.dealType != datatypes.DealType.CLOSE_DEAL: continue
            info = self._infos[take.closeDeal.ticker]
            if info.exchange != "PINK": continue
            # Flush current
            if curr.ticker != take.closeDeal.ticker:
                if curr.ticker:
                    curr.gain += curr.sum  # Don't take into account return. Only profit.
                    total.gain += curr.gain
                    total.sum += curr.sum
                    percent = curr.gain * 100 / curr.sum
                    txt += "{} {:.0f}%\n".format(curr.ticker, -percent)
                    curr.__init__()
                curr.ticker = take.closeDeal.ticker
            # Calculate
            curr.gain += take.count()*take.closeDeal.price - take.closeDeal.fee
            for openDeal in take.openDeals:
                if openDeal.deal.dealType != datatypes.DealType.OPEN_DEAL: continue
                curr.gain -= openDeal.deal.fee
                curr.sum += openDeal.count*openDeal.price
        txt += "Итого возврат с вложенного: {:.0f}%".format(-total.gain*100/total.sum)
        return txt

    def _renameTickers(self, renames):
        redict = {}  # United rename dict.
        for ren in sorted(renames.items()):
            redict.update(ren[1])

        for deal in self._deals:
            #if deal.dealType == datatypes.DealType.SPLIT: continue
            #if deal.dealType == datatypes.DealType.RENAME: continue
            #if deal.ticker: continue
            if deal.ticker is None:
                deal.ticker = deal.origTicker
            while deal.ticker in redict:  # TODO: Detect cycle?
                deal.ticker = redict[deal.ticker]

    def _sortDeals(self):
        from operator import attrgetter
        self._deals = sorted(self._deals, key=attrgetter('ticker', 'dateTime'))

    def _updateRates(self):
        diapasons = _getDealDateDiapason(self._deals)
        for currency in diapasons:
            dtfrom, dtto = diapasons[currency]
            dtfrom = dtfrom.date()
            dtto = dtto.date()
            # Check existing rates.
            if currency in self._currencyRates:
                havefrom, haveto = min(self._currencyRates[currency]), max(self._currencyRates[currency])
                if havefrom <= dtfrom and haveto >= dtto: continue
            # Get rates.
            rates = currencyrates.getCbRates(currency, dtfrom, dtto)
            self._currencyRates[currency] = rates
        for deal in self._deals:
            deal.rate = self.getRate(deal.currency, deal.dateTime)

    def _updateTotal(self):
        for deal in self._deals:
            if deal.price:
                deal.total = deal.count * deal.price - deal.fee
                deal.totalRub = deal.total * deal.rate

    """FIFO
    Don't subtract fees."""
    def _updateTakes(self):
        currTicker = None
        fifo = []
        for deal in self._deals:
            if currTicker!=deal.ticker:
                currTicker = deal.ticker
                # TODO: PROCESS LEFTOVERS AND REMAINS !!!
                fifo.clear()
            # Don't take RENAME yet
            if (not deal.dealType & datatypes.DealType.CLOSE_DEAL) and (not deal.dealType & datatypes.DealType.RENAME):  #in (datatypes.DealType.OPEN_DEAL, datatypes.DealType.SPLIT):
                fifo.append(datatypes.OpenDeal(deal))
            if deal.dealType & datatypes.DealType.CLOSE_DEAL:
                #print("TAKE",deal)
                take = datatypes.Take(deal)
                self._takes.append(take)
                for i in range(len(fifo)):
                    openDeal = fifo.pop(0)
                    #print("====", take.left, openDeal.left, "====", openDeal.deal)
                    take.openDeals.append(openDeal)
                    # Checks
                    assert openDeal.left != 0
                    if openDeal.left > 0:   assert take.left < 0  # long
                    else:                   assert take.left > 0  # short
                    # Split
                    if deal.dealType & datatypes.DealType.SPLIT:
                        for k in range(i):
                            fifo[k].count *= deal.split
                            openDeal.left *= deal.split
                            fifo[k].price /= deal.split
                        fifo.pop(0)
                    # Normal deal
                    else:
                        # Combine
                        if abs(openDeal.left) >= abs(take.left):  # full cover
                            openDeal.left += take.left  # they have different signs
                            openDeal.count = -take.left
                            take.left = 0
                        else:
                            take.left += openDeal.left
                            openDeal.count = openDeal.left
                            openDeal.left = 0
                        # If something stocks in open deal left - let deal stay in fifo for later takes. Else remove it.
                        if openDeal.left != 0:
                            fifo.insert(0, openDeal.__copy__())
                        # Enough open deals for this take.
                        if take.left == 0:
                            break
                        # Open-close deal
                        if not fifo and deal.dealType & (datatypes.DealType.OPEN_DEAL | datatypes.DealType.CLOSE_DEAL):
                            openCloseDeal = datatypes.OpenDeal(deal)
                            openCloseDeal.count = take.left
                            openCloseDeal.left = take.left
                            fifo.append(openCloseDeal)
                            break
                # Close count must be less than open
                #print(take)
                #assert take.count==0
                # TODO: CHECK LEFTOVERS AND REMAINS !!!
    """
    def _updateTakeProceeds(self):
        for take in self._takes:
            if take.count!=0:
                continue
            if take.closeDeal.assetClass==datatypes.AssetClass.FOREX:
                continue # TODO: Calculation for Forex.
            take.proceeds = abs(take.closeDeal.total) + take.closeDeal.fee
            take.proceedsRub = take.proceeds * take.closeDeal.rate
            take.count = abs(take.closeDeal.count)
            print(take.count, take.closeDeal)
            for openDeal in take.openDeals:
                deal = openDeal.deal
                print("----",take.count, deal)
                assert take.count>0
                if take.count<=0:
                    break
                count = abs(deal.count if deal.count<=take.count else take.count)
                take.count -= count
                fee = abs(deal.fee if count==deal.count else deal.fee*count/deal.count)
                expense = count * deal.price
                take.proceeds -= expense + fee
                take.proceedsRub -= (expense + fee)*deal.rate
            assert take.count==0
            take.tax = take.proceedsRub * Decimal(0.13)
            self._totalTaxRub += take.tax
    """

if __name__ == '__main__':
    from PySide2 import QtWidgets
    from fbs_runtime.application_context.PySide2 import ApplicationContext
    appctxt = ApplicationContext()
    app = QtWidgets.QApplication.instance()
    app.setApplicationName("3ndfl")
    app.setOrganizationName("finhack")
    app.setOrganizationDomain("tech")

    repo = Repo()
    repo.addIbReports(["c:/Users/dokvo/3ndfl_reports/my/2018.csv", "c:/Users/dokvo/3ndfl_reports/my/2019.csv", "c:/Users/dokvo/3ndfl_reports/my/2020.csv"])
    print("-----------------------------------------")
    for take in repo._takes:
        print(take)
        print()

    print("-----------------------------------------")
    print(repo.otcReport())