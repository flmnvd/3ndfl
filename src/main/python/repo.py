from PySide2.QtCore import QDateTime
from PySide2.QtCore import QDate
from decimal import Decimal
import currencyrates
import datatypes

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
    _infos = {} # Dict ticker/Financial instrument information
    _currencyRates = {} # Dict of "currency - dict QDate/price_in_rub"
    _deals = [] # List of all deals
    _takes = [] # Dict ticker/take
    _totalTaxRub = 0 # Whole Rub tax

    def clear(self):
        self._infos = {}
        self._currencyRates = {}
        self._deals = []
        self._calc = []
        self._totalTaxRub = 0

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
        self._updateTakeProceeds()

    def getRate(self, currency:str, date:QDate):
        rates = self._currencyRates[currency]
        d = date.date() if type(date) is QDateTime else date
        if not d in rates:
            rate = currencyrates.getCbRate(currency, d)
            rates[d] = rate
            return rate
        return rates[d]

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
            rates = currencyrates.getCbRates(currency, dtfrom, dtto)
            self._currencyRates[currency] = rates
        for deal in self._deals:
            deal.rate = self.getRate(deal.currency, deal.dateTime)

    def _updateTotal(self):
        for deal in self._deals:
            if deal.price:
                deal.total = deal.count * deal.price - deal.fee
                deal.totalRub = deal.total * deal.rate

    """FIFO"""
    def _updateTakes(self):
        return # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        currTicker = None
        fifo = []
        for deal in self._deals:
            if currTicker!=deal.ticker:
                currTicker = deal.ticker
                # TODO: PROCESS LEFTOVERS AND REMAINS !!!
                fifo.clear()
            if deal.isOpenDeal:
                fifo.append(datatypes.OpenDeal(deal))
            else:
                print("TAKE",deal)
                take = datatypes.Take(deal)
                self._takes.append(take)
                take.count = deal.count
                for i in range(len(fifo)):
                    openDeal = fifo[0]
                    print("====", take.count, openDeal.left, "====", openDeal.deal)
                    take.openDeals.append(openDeal)
                    # Checks
                    assert openDeal.left!=0
                    if openDeal.left > 0:   assert take.count < 0 # long
                    else:                   assert take.count > 0 # short
                    # Calculate
                    if abs(openDeal.left) >= abs(take.count): # full cover
                        openDeal.left += take.count
                        take.count = 0
                    else:
                        take.count += openDeal.left
                        openDeal.left = 0
                    # If something stocks in open deal left - let deal stay in fifo for later takes. Else remove it.
                    if openDeal.left == 0:
                        fifo.pop(0)
                    # Enough open deals for this take.
                    if take.count == 0:
                        break
                # Close count must be less than open
                #print(take)
                #assert take.count==0
                # TODO: CHECK LEFTOVERS AND REMAINS !!!

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

if __name__ == '__main__':
    repo = Repo()
    repo.addIbReports(["c:/Users/dokvo/3ndfl_reports/my-test/2020.csv","c:/Users/dokvo/3ndfl_reports/my-test/2019.csv"])
    for take in repo._takes:
        print(take)
        print()