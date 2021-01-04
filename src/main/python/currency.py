
# For 13.12.2020
currencies = {'AUD': 'R01010', 'ATS': 'R01015', 'AZN': 'R01020A', 'GBP': 'R01035', 'AON': 'R01040F', 'AMD': 'R01060', 'BYN': 'R01090B', 'BEF': 'R01095', 'BGN': 'R01100', 'BRL': 'R01115', 'HUF': 'R01135', 'HKD': 'R01200', 'GRD': 'R01205', 
'DKK': 'R01215', 'USD': 'R01235', 'EUR': 'R01239', 'INR': 'R01270', 'IEP': 'R01305', 'ISK': 'R01310', 'ESP': 'R01315', 'ITL': 'R01325', 'KZT': 'R01335', 'CAD': 'R01350', 'KGS': 'R01370', 'CNY': 'R01375', 'KWD': 'R01390', 'LVL': 'R01405', 'LBP': 'R01420', 'LTL': 'R01435', None: 'R01720A', 'MDL': 'R01500', 'DEM': 'R01510A', 'NLG': 'R01523', 'NOK': 'R01535', 'PLN': 'R01565', 'PTE': 'R01570', 'ROL': 'R01585', 'RON': 'R01585F', 'XDR': 'R01589', 'SGD': 'R01625', 'SRD': 'R01665A', 'TJS': 'R01670', 'TJR': 'R01670B', 'TRY': 'R01700J', 'TMM': 'R01710', 'TMT': 'R01710A', 'UZS': 'R01717', 'UAH': 'R01720', 'FIM': 'R01740', 'FRF': 'R01750', 'CZK': 'R01760', 'SEK': 'R01770', 'CHF': 'R01775', 'XEU': 'R01790', 'EEK': 'R01795', 'YUN': 'R01805', 'ZAR': 'R01810', 'KRW': 'R01815', 'JPY': 'R01820'}

# Get list from http://www.cbr.ru/scripts/XML_valFull.asp
def _parseCbCurrencyList(file):
    currencies = {}
    from xml.etree import ElementTree
    tree = ElementTree.parse(file)
    root = tree.getroot()
    for item in root:
        id = item.attrib["ID"]
        code = item.find("ISO_Char_Code").text
        currencies[code] = id

    if len(currencies) == 0:
        raise Exception("Faled to load currency list")

    return currencies

if __name__ == '__main__':
    currencies = _parseCbCurrencyList("t:/tmp/currency_list_XML_valFull.xml")
    if len(currencies) == 0:
        raise Exception("Faled to load ")
    print(currencies)