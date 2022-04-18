from brownie import Keccak256, accounts
import os

# check we have the correct environment variables set
try:
    os.environ["WALLET"]
except KeyError:
    print("Please set a WALLET environment variable")
    exit(1)

def main(thing):
    # wallet_name = os.environ['WALLET']
    # acct = accounts.load(wallet_name)
    k = Keccak256.deploy({"from": accounts[0]})
    print("keccak256(%s) = %s" % (thing, k.process(thing)))