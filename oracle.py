import time
import utils
import config
from providers import coinmarketcap


def update_ether_price():
    try:
        coinmarketcap_price = coinmarketcap.get_price()
    except Exception as e:
        print('Coinmarketcap Error: {}'.format(e))
    else:
        coinmarketcap_price = int(round(coinmarketcap_price / config.ETH_TO_USD, 2) * 100)
        contract_price = utils.send_eth_call(
            utils.contracts['etherbank'].functions.etherPrice(), None)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        if abs(coinmarketcap_price -
               contract_price) > .01 * coinmarketcap_price:
            func = utils.contracts['oracles'].functions.vote(
                0, coinmarketcap_price)
            utils.send_transaction(func, 0,
                                   utils.check_account(None, None, None))
            print('{0}\nUpdate ether price from {1} cents to {2} cents\n\n'.
                  format(now, contract_price, coinmarketcap_price))
        else:
            print(
                '{0}\ncontract price: {1} cents\nmarket price: {2} cents\n\n'.
                format(now, contract_price, coinmarketcap_price))


if __name__ == '__main__':
    update_ether_price()
    while True:
        time.sleep(60*60)
        update_ether_price()
