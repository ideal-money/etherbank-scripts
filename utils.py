import os
import json
from eth_keys import keys
from web3 import Web3, HTTPProvider
import config


def get_addresses(etherbank_addr):
    global addresses
    etherbank_contract = w3.eth.contract(
        address=w3.toChecksumAddress(config.ETHERBANK_ADDR),
        abi=config.ABIES['etherbank'])
    addresses = {
        'etherbank':
        etherbank_addr,
        'oracles':
        send_eth_call(etherbank_contract.functions.oraclesAddr(), None),
        'liquidator':
        send_eth_call(etherbank_contract.functions.liquidatorAddr(), None),
        'etherdollar':
        send_eth_call(etherbank_contract.functions.etherDollarAddr(), None)
    }
    return addresses


def get_contracts():
    global contracts
    contracts = {
        'etherbank':
        w3.eth.contract(
            address=addresses['etherbank'], abi=config.ABIES['etherbank']),
        'oracles':
        w3.eth.contract(
            address=addresses['oracles'], abi=config.ABIES['oracles']),
        'liquidator':
        w3.eth.contract(
            address=addresses['liquidator'], abi=config.ABIES['liquidator']),
        'etherdollar':
        w3.eth.contract(
            address=addresses['etherdollar'], abi=config.ABIES['etherdollar'])
    }
    return contracts


def priv2addr(private_key):
    pk = keys.PrivateKey(bytes.fromhex(private_key))
    return pk.public_key.to_checksum_address()


def check_account(ctx, param, value):
    if not value:
        value = config.PRIVATEKEY
    if value.startswith('0x'):
        value = value[2:]
    return value


def send_transaction(func, value, private_key):
    transaction = func.buildTransaction({
        'nonce':
        w3.eth.getTransactionCount(priv2addr(private_key)),
        'from':
        priv2addr(private_key),
        'value':
        value,
        'gas':
        config.GAS,
        'gasPrice':
        config.GAS_PRICE
    })
    signed = w3.eth.account.signTransaction(transaction, private_key)
    raw_transaction = signed.rawTransaction.hex()
    tx_hash = w3.eth.sendRawTransaction(raw_transaction).hex()
    rec = w3.eth.waitForTransactionReceipt(tx_hash)
    if not rec['status']:
        print('Reverted!\nError occured during contract execution', fg='green')


def send_eth_call(func, sender):
    if not sender:
        sender = priv2addr(check_account(None, None, None))
    result = func.call({
        'from': sender,
    })
    return result


def start():
    global addresses, contracts, w3
    w3 = Web3(HTTPProvider(config.NODE_URL))

    if os.path.exists(os.path.expanduser('~/.etherbank.json')):
        with open(os.path.expanduser('~/.etherbank.json'), 'r') as f:
            addresses = json.load(f)
    else:
        addresses = get_addresses(w3.toChecksumAddress(config.ETHERBANK_ADDR))
        with open(os.path.expanduser('~/.etherbank.json'), 'w') as f:
            f.write(json.dumps(addresses))
    get_contracts()


# we are initalizing some variables here
addresses = contracts = w3 = None
start()


# FIXME: infura not supports filtering of events.
# Here we are hacking web3.py filters to use getLogs rpc endpoint instead.
def dummy(*args, **argsdic):
    if len(args) > 0 and args[0] == 'eth_newFilter':
        return 0
    else:
        return original_request_blocking(*args, **argsdic)


original_request_blocking = w3.manager.request_blocking
w3.manager.request_blocking = dummy
