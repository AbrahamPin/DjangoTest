import requests


def get_rate(symbol, base='EUR'):
    # url = 'https://api.fixer.io/latest'
    # params = {'base': base, 'symbols': symbol}
    # r = requests.get(url, params=params)
    # return r.json()
    r = requests.get('https://api.fixer.io/latest', params={'base': base, 'symbols': symbol})
    return requests.get('https://api.fixer.io/latest', params={'base': base, 'symbols': symbol}).json()['rates'][symbol]
