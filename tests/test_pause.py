# nvm use 14
# brownie test tests/test_roles.py -s --interactive
import pytest
from brownie import *
from brownie import reverts


@pytest.fixture
def mock():
    print("deploy mock token")
    return accounts[0].deploy(EnFi20, "Mock", "FOO", 9, 1000)


def test_transfer(mock):
    assert(mock.address != ZERO_ADDRESS)

    # test transfer of tokens
    assert(mock.balanceOf(accounts[0]) == 1000*10**9)
    assert(mock.balanceOf(accounts[1]) == 0)
    mock.transfer(accounts[1], 100*10**9, {"from": accounts[0]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 100*10**9)


def test_transferFrom(mock):
    assert(mock.address != ZERO_ADDRESS)

    # test approve and transferFrom
    assert(mock.allowance(accounts[0], accounts[1]) == 0)
    mock.approve(accounts[1], 100*10**9, {"from": accounts[0]})
    assert(mock.allowance(accounts[0], accounts[1]) == 100*10**9)
    mock.transferFrom(accounts[0], accounts[2], 100*10**9, {"from": accounts[1]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 0)
    assert(mock.balanceOf(accounts[2]) == 100*10**9)


def test_pause(mock):
    assert(mock.address != ZERO_ADDRESS)

    # pause the contract
    assert(not mock.paused({'from': accounts[0]}))
    mock.pause({'from': accounts[0]})
    assert(not mock.paused({'from': accounts[0]}))
    assert(mock.paused({'from': accounts[1]}))

    # test transfer of tokens
    assert(mock.balanceOf(accounts[0]) == 1000*10**9)
    assert(mock.balanceOf(accounts[1]) == 0)

    # should work for contract owner...
    mock.transfer(accounts[1], 100*10**9, {"from": accounts[0]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 100*10**9)

    # should not work the other way around since the contract is paused
    with reverts():
        mock.transfer(accounts[0], 100*10**9, {"from": accounts[1]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 100*10**9)

    # try to unpause the contract from somewhere else, shouldn't work
    with reverts():
        mock.unpause({'from': accounts[1]})
        mock.transfer(accounts[0], 100*10**9, {"from": accounts[1]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 100*10**9)

    # unpause from owner, should be fine
    mock.unpause({'from': accounts[0]})
    mock.transfer(accounts[0], 100*10**9, {"from": accounts[1]})
    assert(mock.balanceOf(accounts[0]) == 1000*10**9)
    assert(mock.balanceOf(accounts[1]) == 0)


def test_pause_address(mock):
    assert(mock.address != ZERO_ADDRESS)

    # pause the contract
    assert(not mock.paused(accounts[1]))
    mock.pause(accounts[1], {'from': accounts[0]})
    assert(mock.paused(accounts[1]))
    assert(not mock.paused(accounts[2]))

    # test transfer of tokens
    assert(mock.balanceOf(accounts[0]) == 1000*10**9)
    assert(mock.balanceOf(accounts[1]) == 0)

    # should work for contract owner...
    mock.transfer(accounts[1], 100*10**9, {"from": accounts[0]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 100*10**9)

    # should not work the other way around since the contract is paused
    with reverts():
        mock.transfer(accounts[0], 100*10**9, {"from": accounts[1]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 100*10**9)

    # try to unpause the contract from somewhere else, shouldn't work
    with reverts():
        mock.unpause(accounts[1], {'from': accounts[1]})
        mock.transfer(accounts[0], 100*10**9, {"from": accounts[1]})
    assert(mock.balanceOf(accounts[0]) == 900*10**9)
    assert(mock.balanceOf(accounts[1]) == 100*10**9)

    # unpause from owner, should be fine
    mock.unpause(accounts[1], {'from': accounts[0]})
    mock.transfer(accounts[0], 100*10**9, {"from": accounts[1]})
    assert(mock.balanceOf(accounts[0]) == 1000*10**9)
    assert(mock.balanceOf(accounts[1]) == 0)