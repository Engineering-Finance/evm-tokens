# nvm use 14
# brownie test tests/test_roles.py -s --interactive
import pytest
from brownie import *

@pytest.fixture
def mock():
    print("deploy mock token")
    return accounts[0].deploy(EnFi20, "Mock", "FOO")


def test_deposit(mock):
    assert(mock.address != ZERO_ADDRESS)

    # uint256 public constant ROLE_setRateStrategy = 1;
    # uint256 public constant ROLE_setTax = 2;
    # uint256 public constant ROLE_setTaxWallet = 4;
    # uint256 public constant ROLE_borrow = 8;
    # uint256 public constant ROLE_repay = 16;
    # uint256 public constant ROLE_collectTax = 32;
    # uint256 public constant ROLE_addRole = 64;
    # uint256 public constant ROLE_removeRole = 128;
    # uint256 public constant ROLE_mintToBentobox = 256;
    assert(mock.hasRole(mock.ROLE_xtransfer(), {"from": accounts[0]}))
    assert(mock.hasRole(mock.ROLE_xapprove(), {"from": accounts[0]}))
    assert(mock.hasRole(mock.ROLE_withdrawEth(), {"from": accounts[0]}))
    assert(not mock.hasRole(mock.ROLE_xtransfer(), {"from": accounts[1]}))
    assert(not mock.hasRole(mock.ROLE_xapprove(), {"from": accounts[1]}))
    assert(not mock.hasRole(mock.ROLE_withdrawEth(), {"from": accounts[1]}))

    # make sure mock.addRole() is working as expected
    assert(not mock.hasRole(mock.ROLE_xtransfer(), {"from": accounts[2]}))
    mock.addRole(accounts[2], mock.ROLE_xtransfer(), {"from": accounts[0]})
    assert(mock.hasRole(mock.ROLE_xtransfer(), {"from": accounts[2]}))

    # also check removeRole() is working as expected
    mock.addRole(accounts[2], mock.ROLE_xtransfer(), {"from": accounts[0]})
    assert(mock.hasRole(mock.ROLE_xtransfer(), {"from": accounts[2]}))
    mock.removeRole(accounts[2], mock.ROLE_xtransfer(), {"from": accounts[0]})
    assert(not mock.hasRole(mock.ROLE_xtransfer(), {"from": accounts[2]}))
    