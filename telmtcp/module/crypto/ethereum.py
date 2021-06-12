import requests
import random

from hexbytes import HexBytes
from web3 import Web3
from eth_account import Account
from telmtcp.module.telmtcp import constant as my_constant
import time
from pycoingecko import CoinGeckoAPI
# ***********************************************************************************
# @function: Get Gas Price
# ***********************************************************************************

my_constant.WEB3_LIST.clear()
for endpoint in my_constant.WEB3_ENDPOINT:
    my_constant.WEB3_LIST.append(Web3(Web3.HTTPProvider(endpoint)))

COIN_GECKO_API = CoinGeckoAPI()


def get_web3():
    if my_constant.WEB3_INDEX >= len(my_constant.WEB3_LIST):
        my_constant.WEB3_INDEX = 0
    res = my_constant.WEB3_LIST[my_constant.WEB3_INDEX]
    my_constant.WEB3_INDEX += 1
    return res


def create_wallet():
    while True:
        try:
            random_str = f'{random.randint(1000000000, 9999999999)}_{random.randint(1000000000, 9999999999)}'
            eth_account = Account.create(random_str)
            return eth_account
        except Exception as e:
            print("ethereum:create_wallet:" + str(e))
            time.sleep(1)


def get_eth_balance(wallet_address):
    try:
        web3 = get_web3()
        eth_balance = web3.eth.getBalance(wallet_address)
        eth_balance = web3.fromWei(eth_balance, 'ether')
        return float(eth_balance)
    except Exception as e:
        print("get_eth_balance:" + str(e), "ERROR", 3)
        return 0


def transfer_eth(source_address, source_private_key, dest_address, amount, gas_limit, gas_price, wait=False):
    result = {'code': -1, 'tx': '', 'message': ''}
    try:
        eth_balance = get_eth_balance(source_address)
        eth_limit = gas_limit * gas_price / pow(10, 9)

        if eth_balance < amount + eth_limit:
            result['code'] = -3
            result['message'] = 'not enough money'
            result['tx'] = ''
            return result
        web3 = get_web3()
        # ---------- sign and do transaction ---------- #
        signed_txn = web3.eth.account.signTransaction(dict(
                        nonce=web3.eth.getTransactionCount(source_address),
                        gasPrice=web3.toWei(gas_price, 'gwei'),
                        gas=gas_limit,
                        to=dest_address,
                        value=web3.toWei(amount, 'ether')
                      ), private_key=source_private_key)
        txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

        # @FIXME ----- check if transaction is success ----- #
        if wait is True:
            txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash, my_constant.ETH_LIMIT_WAIT_TIME)
            if txn_receipt is None or 'status' not in txn_receipt or txn_receipt['status'] != 1 or 'transactionIndex' not in txn_receipt:
                result['code'] = 0
                result['message'] = 'waiting failed'
                result['tx'] = txn_hash.hex()
                return result
        result['code'] = 0
        result['message'] = ''
        result['tx'] = txn_hash.hex()
        return result
    except Exception as e:
        print("transfer_eth:" + str(e))
        result['code'] = -2
        result['message'] = str(e)
        result['tx'] = ''
        return result


def calc_exact_eth_dst_amount(address, gas_price, gas_limit):
    while True:
        try:
            web3 = get_web3()
            eth_balance = web3.eth.getBalance(address)
            eth_limit = gas_limit * web3.toWei(gas_price, 'gwei')
            eth_dst_wei = eth_balance - eth_limit
            if eth_dst_wei <= 0:
                print("calc_exact_eth_dst_amount: not enough balance, eth:" + str(eth_balance) + ", gas:" + str(eth_limit))
                return eth_dst_wei
            dst_amt = float(web3.fromWei(eth_dst_wei, 'ether'))
            return dst_amt
        except Exception as e:
            print("calc_exact_eth_dst_amount:" + str(e))
            time.sleep(1)


def get_gas_price():
    while True:
        try:
            res = requests.get(my_constant.GAS_ENDPOINT).json()
            return int(res[my_constant.ETH_GAS_LEVEL] / 10)
        except Exception as e:
            print("get_gas_price:" + str(e))
            time.sleep(1)


def get_exchange_price():
    price = 0
    try:
        data = COIN_GECKO_API.get_price(ids='ethereum', vs_currencies='usd')
        data = data['ethereum']['usd']
        price = float(data)
    except Exception as err:
        print("get_exchange_price for eth_usd:" + str(err))
    return price


def check_transaction(order, balance, original_balance):
    try:
        if order['address'] is None:
            result = {'status': 0, 'received': 0, 'txs': '', 'refunded': 0, 'ref_code': 0, 'ref_message': '', 'ref_tx': ''}
            return result
        '''
        block = web3.eth.getBlock('latest')
        transactions = block.transactions
        received = 0
        txs = ''
        from_address = ''
        for tx_hash in transactions:
            tx = web3.eth.getTransaction(tx_hash)
            if tx.to is None:
                continue
            if tx.to.lower() != order['address'].lower():
                continue
            received += web3.fromWei(tx.value, 'ether')
            txs += tx_hash.hex()
            from_address = tx['from']
        if received == 0:
            result = {'status': 0, 'received': 0, 'txs': txs, 'refunded': 0, 'ref_code': 0, 'ref_message': '', 'ref_tx': ''}
            return result
        if received + my_constant.LIMIT_ETH_UNDERPAYMENT < order['amount']:
            refund = received - my_constant.ETH_GAS_LIMIT * order['gas_price'] / pow(10, 9)
            if refund <= 0:
                result = {'status': -3, 'received': received, 'txs': txs, 'refunded': 0, 'ref_code': 0, 'ref_message': '', 'ref_tx': ''}
                return result
            ret = transfer_eth(order['address'], HexBytes(order['private']), from_address, refund, my_constant.ETH_GAS_LIMIT, order['gas_price'], False)
            print(ret['message'])
            result = {'status': -2, 'received': received, 'txs': txs, 'refunded': refund, 'ref_code': ret['code'], 'ref_message': ret['message'], 'ref_tx': ret['tx']}
            return result
        '''
        received = balance - original_balance
        if received <= my_constant.LIMIT_ETH_UNDERPAYMENT:
            result = {'status': 0, 'received': received, 'txs': '', 'refunded': 0, 'ref_code': 0, 'ref_message': '',
                      'ref_tx': ''}
        elif received + my_constant.LIMIT_ETH_UNDERPAYMENT < order['amount']:
            result = {'status': -3, 'received': received, 'txs': '', 'refunded': 0, 'ref_code': 0, 'ref_message': '', 'ref_tx': ''}
        else:
            result = {'status': 2, 'received': received, 'txs': '', 'refunded': 0, 'ref_code': 0, 'ref_message': '', 'ref_tx': ''}
        return result
    except Exception as e:
        print(str(e))
    result = {'status': 0, 'received': 0, 'txs': '', 'refunded': 0, 'ref_code': 0, 'ref_message': '', 'ref_tx': ''}
    return result