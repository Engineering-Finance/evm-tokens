import pytest
from brownie import MockERC20, MockERC4626

@pytest.fixture
def sudo(accounts):
    return accounts[-1]


@pytest.fixture
def token(sudo):
    return sudo.deploy(MockERC20, "TEST", "TEST")


@pytest.fixture
def vault(sudo, token):
    return sudo.deploy(MockERC4626, token, "ERC4626", "ERC4626")
    
AMOUNT = 100 * 10 ** 18


def test_asset(vault, token):
    assert vault.asset() == token


def test_max_methods(accounts, vault):
    a = accounts[0]

    assert vault.maxDeposit(a) == 2 ** 256 - 1
    assert vault.maxMint(a) == 2 ** 256 - 1
    assert vault.maxWithdraw(a) == vault.assetsOf(a) #2 ** 256 - 1
    assert vault.maxRedeem(a) == vault.balanceOf(a) #2 ** 256 - 1


def test_preview_methods(accounts, token, vault):
    a = accounts[0]

    assert vault.totalAssets() == 0
    assert vault.convertToAssets(10 ** 18) == 0  # no assets
    assert vault.convertToShares(10 ** 18) == 10 ** 18  # 1:1 price
    assert vault.previewDeposit(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewMint(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewWithdraw(AMOUNT) == 0  # but no assets
    assert vault.previewRedeem(AMOUNT) == 0  # but no assets

    token.DEBUG_mint(a, AMOUNT, {'from':a})
    token.approve(vault, AMOUNT, {'from':a})
    vault.deposit(AMOUNT, a, {'from':a})

    assert vault.totalAssets() == AMOUNT
    assert vault.convertToAssets(10 ** 18) == 10 ** 18  # 1:1 price
    assert vault.convertToShares(10 ** 18) == 10 ** 18  # 1:1 price
    assert vault.previewDeposit(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewMint(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewWithdraw(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewRedeem(AMOUNT) == AMOUNT  # 1:1 price

    token.DEBUG_mint(vault, AMOUNT, {'from':a})

    assert vault.totalAssets() == 2 * AMOUNT
    assert vault.convertToAssets(10 ** 18) == 2 * 10 ** 18  # 2:1 price
    assert vault.convertToShares(2 * 10 ** 18) == 10 ** 18  # 2:1 price
    assert vault.previewDeposit(AMOUNT) == AMOUNT // 2  # 2:1 price
    assert vault.previewMint(AMOUNT // 2) == AMOUNT  # 2:1 price
    assert vault.previewWithdraw(AMOUNT) == AMOUNT // 2  # 2:1 price
    assert vault.previewRedeem(AMOUNT // 2) == AMOUNT  # 2:1 price

    vault.DEBUG_steal_tokens(AMOUNT, {'from':a})

    assert vault.totalAssets() == AMOUNT
    assert vault.convertToAssets(10 ** 18) == 10 ** 18  # 1:1 price
    assert vault.convertToShares(10 ** 18) == 10 ** 18  # 1:1 price
    assert vault.previewDeposit(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewMint(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewWithdraw(AMOUNT) == AMOUNT  # 1:1 price
    assert vault.previewRedeem(AMOUNT) == AMOUNT  # 1:1 price

    vault.DEBUG_steal_tokens(AMOUNT // 2, {'from':a})

    assert vault.totalAssets() == AMOUNT // 2
    assert vault.convertToAssets(10 ** 18) == 10 ** 18 // 2  # 1:2 price
    assert vault.convertToShares(10 ** 18 // 2) == 10 ** 18  # 1:2 price
    assert vault.previewDeposit(AMOUNT) == 2 * AMOUNT  # 1:2 price
    assert vault.previewMint(2 * AMOUNT) == AMOUNT  # 1:2 price
    assert vault.previewWithdraw(AMOUNT) == 2 * AMOUNT  # 1:2 price
    assert vault.previewRedeem(2 * AMOUNT) == AMOUNT  # 1:2 price
