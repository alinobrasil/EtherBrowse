from flask import Flask, render_template, flash, redirect
import config
from web3 import Web3
import ccxt
import time
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('INFURA_URL')))

def get_ethereum_price():
    binance = ccxt.binance()
    ethereum_price = binance.fetch_ticker('ETH/USDC')

    return ethereum_price


@app.route("/")
def index():
    ethereum_price = get_ethereum_price()
    gas_price = w3.eth.gas_price/1000000000
    
    latest_blocks=[]
    for block_number in range(w3.eth.block_number, w3.eth.block_number-10, -1):
        block = w3.eth.get_block(block_number)
        latest_blocks.append(block)
        
    latest_transactions=[]
    for tx in latest_blocks[-1]['transactions'][-10:]:
        transaction = w3.eth.get_transaction(tx)
        latest_transactions.append(transaction)
        
    current_time= time.time()
    
    return render_template("index.html", 
                           ethereum_price=ethereum_price, 
                           gas_price=gas_price,
                           miners=config.MINERS,
                           current_time = current_time,
                           latest_blocks=latest_blocks,
                           latest_transactions=latest_transactions
                           )


@app.route("/address/<addr>")
def address(addr):
    ethereum_price = get_ethereum_price()
    try:
        address = w3.toChecksumAddress(addr)
    except:
        flash('Invalid address', 'danger')
        return redirect('/')
    
    balance = w3.eth.get_balance(address)
    balance = w3.fromWei(balance, 'ether')
    
    return render_template("address.html", 
                           address = address,
                           ethereum_price=ethereum_price,
                           balance=balance
                           )


@app.route("/tx/<hash>")
def transaction(hash):
    transaction = w3.eth.get_transaction(hash)
    return render_template("transaction.html", hash=hash, transaction=transaction)

@app.route("/block/<block_number>")
def block(block_number):
    block =  w3.eth.get_block(int(block_number))
    return render_template("block.html", 
                           block=block)


