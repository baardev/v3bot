#!/usr/bin/python
import sys
import getopt
import json
import toml
import ccxt
import lib_v2_globals as g
import lib_v2_ohlc as o
import lib_v2_binance as b

g.cvars = toml.load(g.cfgfile)

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]
verbose = False
cancel_order = False
try:
    opts, args = getopt.getopt(argv, "-hvc", ["help", "verbose", "cancel"])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print("-v --verbose")
        print("-c --cancel")
        sys.exit(0)

    if opt in ("-v", "--verbose"):
        verbose = True
    if opt in ("-c", "--cancel"):
        cancel_order = True
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)

g.keys = o.get_secret()
g.ticker_src = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 50000,
    'apiKey': g.keys['binance']['testnet']['key'],
    'secret': g.keys['binance']['testnet']['secret'],
})

g.ticker_src.set_sandbox_mode(g.keys['binance']['testnet']['testnet'])
if g.keys['binance']['testnet']['testnet']:
    b.Oprint(f" MODE:SANDBOX")

if verbose:
    g.ticker_src.verbose = True


try:
    print("----------\nOPEN ORDERS\n-----------")
    openorders = g.ticker_src.fetch_open_orders(symbol=g.cvars['pair'])
    for oo in openorders:
        t = oo['type']
        p = oo['price']
        s = oo['stopPrice']
        i = oo['side']
        a = oo['amount']
        o = oo['id']

        oostr = f"{t} {i} {a} @ {p} ({o})"
        b.Dprint(oostr)

    if cancel_order:
        rs = g.ticker_src.cancel_all_orders(symbol=g.cvars['pair'])
        for oo in rs:
            t = oo['type']
            p = oo['price']
            s = oo['stopPrice']
            i = oo['side']
            a = oo['amount']
            o = oo['id']

            oostr = f"CANCELLED: {t} {i} {a} @ {p} ({o})"
            b.Dprint(oostr)

except ccxt.DDoSProtection as e:
    print(type(e).__name__, e.args, 'DDoS Protection (ignoring)')
except ccxt.RequestTimeout as e:
    print(type(e).__name__, e.args, 'Request Timeout (ignoring)')
except ccxt.ExchangeNotAvailable as e:
    print(type(e).__name__, e.args, 'Exchange Not Available due to downtime or maintenance (ignoring)')
except ccxt.AuthenticationError as e:
    print(type(e).__name__, e.args, 'Authentication Error (missing API keys, ignoring)')
except ccxt.ExchangeError as e:
    print(type(e).__name__, e.args, 'Loading markets failed')
