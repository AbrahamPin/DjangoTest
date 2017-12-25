import urllib.request
import json

class CurrencyConverter:
    rates = {}
    def __init__(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': 'howCode Currency Bot'})
        data = urllib.request.urlopen(req).read()
        data = json.loads(data.decode('utf-8'))
        self.rates = data["rates"]

    def convert(self, amount, from_currency, to_currency):
        initial_amount = float(amount)
        if from_currency != "EUR":
            amount = amount / self.rates[from_currency]
        if to_currency == "EUR":
            return initial_amount, from_currency, '=', amount, to_currency
        else:
            total = initial_amount * self.rates[to_currency]
            return total
