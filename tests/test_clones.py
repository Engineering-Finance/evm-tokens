# nvm use 14
# brownie test tests/test_clones.py -s --interactive
import pytest
from brownie import *


@pytest.fixture
def mock():
    print("deploy mock token")
    return accounts[0].deploy(EnFi20, "Mock", "FOO", 9, 1000*18**18)


def test_clones(mock):
    assert(mock.address != ZERO_ADDRESS)
    init_params = mock.getParams("Mock 2", "FOO 2", 9, 1000*18**18)
    print("clone params:", init_params)
    tx = mock.clone({"from": accounts[0]})
    other_address = tx.return_value
    other = EnFi20.at(other_address)
    other.init(init_params, {"from": accounts[0]})
    assert(other.address != ZERO_ADDRESS)
    print("mock address", mock.address)
    print("other address", other.address)
    # clone again
    tx = mock.clone()
    other_address = tx.return_value
    other = EnFi20.at(other_address)
    assert(other.address != ZERO_ADDRESS)
    print("other address", other.address)
    print("xapprove: ", other.ROLE_xapprove())
    print("withdrawEth: ", other.ROLE_withdrawEth())