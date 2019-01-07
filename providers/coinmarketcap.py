import requests

COINMARKETCAP_ADDR = 'https://api.coinmarketcap.com/v1/ticker/ethereum/'


def get_price():
    response = requests.get(COINMARKETCAP_ADDR).json()
    if 'error' in response:
        raise RuntimeError(response['error'])
    market_price = float(response[0]['price_usd'])
    return market_price


if __name__ == '__main__':
    print(get_price())
