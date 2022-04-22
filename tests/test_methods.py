import pytest
from brownie import MockERC20, MockERC4626


num_decimals = 9
total_supply_i = 10 * (10**6) 
total_supply = total_supply_i * 10**num_decimals


@pytest.fixture
def sudo(accounts):
    return accounts[-1]


@pytest.fixture
def token(sudo, accounts):
    _token = sudo.deploy(MockERC20, "TEST", "TEST")
    _token.DEBUG_mint(sudo, total_supply, {'from':sudo})
    return _token


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




def test_withrebase(sudo, accounts, token, vault):
    user = accounts[1]
    balance = token.balanceOf(sudo)
    # test staking and unstaking
    AMOUNT = int(balance / 100)
    # send token (AMOUNT) from sudo to user
    tx = token.transfer(user, AMOUNT, {'from': sudo})
    assert (token.balanceOf(user) == AMOUNT)
    # deposit
    tx = token.approve(vault, AMOUNT, {'from':user})
    assert (token.allowance(user, vault) >= AMOUNT)
    tx = vault.deposit(AMOUNT, user, {'from':user})
    assert (token.balanceOf(user) == 0)
    assert (vault.balanceOf(user) == AMOUNT)
    assert (vault.assetsOf(user) == AMOUNT)

    # creating a rebase
    AMOUNT_REBASE = AMOUNT / 4
    tx = token.transfer(vault, AMOUNT_REBASE, {'from': sudo})
    # test balance
    assert (vault.assetsOf(user) == AMOUNT + AMOUNT_REBASE)
    # withdraw
    tx = vault.withdraw(vault.assetsOf(user), user, user, {'from':user})
    assert (token.balanceOf(user) == AMOUNT + AMOUNT_REBASE)
    assert (vault.balanceOf(user) == 0)
    assert (vault.assetsOf(user) == 0)
    


def test_withrebase2(sudo, accounts, token, vault):
    user = accounts[1]
    balance = token.balanceOf(sudo)
    AMOUNT = int(balance / 100)
    # send token (AMOUNT) from sudo to user
    tx = token.transfer(user, AMOUNT, {'from': sudo})
    assert (token.balanceOf(user) == AMOUNT)
    # staking
    tx = token.approve(vault, AMOUNT, {'from':user})
    assert (token.allowance(user, vault) >= AMOUNT)
    tx = vault.deposit(AMOUNT, user, {'from':user})
    assert (token.balanceOf(user) == 0)
    assert (vault.balanceOf(user) == AMOUNT)
    assert (vault.assetsOf(user) == AMOUNT)

    # creating a rebase
    AMOUNT_REBASE = AMOUNT / 4
    tx = token.transfer(vault, AMOUNT_REBASE, {'from': sudo})
    # test balance
    assert (vault.assetsOf(user) == AMOUNT + AMOUNT_REBASE)
    assert (vault.balanceOf(user) == AMOUNT)

    user2 = accounts[2]
    AMOUNT2 = int(balance/400)
    tx = token.transfer(user2, AMOUNT2, {'from': sudo})
    assert (token.balanceOf(user2) == AMOUNT2)

    # deposit
    tx = token.approve(vault, AMOUNT2, {'from':user2})
    assert (token.allowance(user2, vault) >= AMOUNT2)
    tx = vault.deposit(AMOUNT2, user2, {'from':user2})
    assert (token.balanceOf(user2) == 0)
    assert (vault.assetsOf(user2) == AMOUNT2)
    assert (vault.assetsOf(user) == AMOUNT + AMOUNT_REBASE)
    # withdraw
    tx = vault.withdraw(vault.assetsOf(user2), user2, user2, {'from':user2})
    assert (vault.balanceOf(user2) == 0)
    assert (vault.assetsOf(user2) == 0)
    assert (token.balanceOf(user2) == AMOUNT2)



    # withdraw
    tx = vault.withdraw(vault.assetsOf(user), user, user, {'from':user})
    assert (token.balanceOf(user) == AMOUNT + AMOUNT_REBASE)
    assert (vault.balanceOf(user) == 0)
    assert (vault.assetsOf(user) == 0)


def test_withrebase3(sudo, accounts, token, vault):
    user = accounts[1]
    balance = token.balanceOf(sudo)
    AMOUNT = int(balance / 100)
    # send token (AMOUNT) from sudo to user
    tx = token.transfer(user, AMOUNT, {'from': sudo})
    assert (token.balanceOf(user) == AMOUNT)
    # staking
    tx = token.approve(vault, AMOUNT, {'from':user})
    assert (token.allowance(user, vault) >= AMOUNT)
    tx = vault.deposit(AMOUNT, user, {'from':user})
    share_value1 = tx.return_value
    assert (token.balanceOf(user) == 0)
    assert (vault.balanceOf(user) == AMOUNT)
    assert (vault.assetsOf(user) == AMOUNT)

    # creating a rebase
    AMOUNT_REBASE = AMOUNT / 4
    tx = token.transfer(vault, AMOUNT_REBASE, {'from': sudo})
    # test balance
    assert (vault.assetsOf(user) == AMOUNT + AMOUNT_REBASE)

    user2 = accounts[2]
    AMOUNT2 = int(balance/400)
    tx = token.transfer(user2, AMOUNT2, {'from': sudo})
    assert (token.balanceOf(user2) == AMOUNT2)

    # deposit
    tx = token.approve(vault, AMOUNT2, {'from':user2})
    assert (token.allowance(user2, vault) >= AMOUNT2)
    tx = vault.deposit(AMOUNT2, user2, {'from':user2})
    share_value2 = tx.return_value
    assert (token.balanceOf(user2) == 0)
    b2 = vault.assetsOf(user2)
    assert (b2 == AMOUNT2)
    b = vault.assetsOf(user) 
    assert (b == AMOUNT + AMOUNT_REBASE)

    # creating a second rebase
    AMOUNT_REBASE2 = AMOUNT / 5
    tx = token.transfer(vault, AMOUNT_REBASE2, {'from': sudo})
    # test balance
    assert abs(vault.assetsOf(user) - int(b * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5
    assert abs(vault.assetsOf(user2) - int(b2 * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5

    user3 = accounts[3]
    bal1 = vault.balanceOf(user)
    vault.transfer(user3, bal1, {'from':user})
    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(user3) == bal1
    vault.transfer(user, bal1, {'from':user3})
    assert vault.balanceOf(user) == bal1
    assert vault.balanceOf(user3) == 0
    

    # redeem
    #tx = vault.withdraw(user2, vault.assetsOf(user2),{'from':user2})
    assert share_value2 == vault.balanceOf(user2)
    tx = vault.redeem(share_value2, user2, user2, {'from':user2})
    assert (vault.balanceOf(user2) == 0)
    assert (vault.assetsOf(user2) == 0)
    assert abs(token.balanceOf(user2) - int(b2 * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5



    # withdraw
    tx = vault.withdraw(vault.assetsOf(user), user, user, {'from':user})
    assert abs(token.balanceOf(user) - int(b * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5
    assert (vault.balanceOf(user) == 0)
    assert (vault.assetsOf(user) == 0)



def test_withrebase_removeaddfunds(sudo, accounts, token, vault):
    user = accounts[1]
    balance = token.balanceOf(sudo)
    AMOUNT = int(balance / 100)
    # send token (AMOUNT) from sudo to user
    tx = token.transfer(user, AMOUNT, {'from': sudo})
    assert (token.balanceOf(user) == AMOUNT)
    # staking
    tx = token.approve(vault, AMOUNT, {'from':user})
    assert (token.allowance(user, vault) >= AMOUNT)
    tx = vault.deposit(AMOUNT, user, {'from':user})
    share_value1 = tx.return_value
    assert (token.balanceOf(user) == 0)
    assert (vault.balanceOf(user) == AMOUNT)
    assert (vault.assetsOf(user) == AMOUNT)

    # creating a rebase
    AMOUNT_REBASE = AMOUNT / 4
    tx = token.transfer(vault, AMOUNT_REBASE, {'from': sudo})
    # test balance
    assert (vault.assetsOf(user) == AMOUNT + AMOUNT_REBASE)

    user2 = accounts[2]
    AMOUNT2 = int(balance/400)
    tx = token.transfer(user2, AMOUNT2, {'from': sudo})
    assert (token.balanceOf(user2) == AMOUNT2)

    # deposit
    tx = token.approve(vault, AMOUNT2, {'from':user2})
    assert (token.allowance(user2, vault) >= AMOUNT2)
    tx = vault.deposit(AMOUNT2, user2, {'from':user2})
    share_value2 = tx.return_value
    assert (token.balanceOf(user2) == 0)
    b2 = vault.assetsOf(user2)
    assert (b2 == AMOUNT2)
    b = vault.assetsOf(user) 
    assert (b == AMOUNT + AMOUNT_REBASE)

    # creating a second rebase
    AMOUNT_REBASE2 = AMOUNT / 5
    tx = token.transfer(vault, AMOUNT_REBASE2, {'from': sudo})
    # test balance
    assert abs(vault.assetsOf(user) - int(b * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5
    assert abs(vault.assetsOf(user2) - int(b2 * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5

    user3 = accounts[3]
    bal1 = vault.balanceOf(user)
    vault.transfer(user3, bal1, {'from':user})
    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(user3) == bal1
    vault.transfer(user, bal1, {'from':user3})
    assert vault.balanceOf(user) == bal1
    assert vault.balanceOf(user3) == 0
    
    # removeFunds
    ibal = token.balanceOf(sudo)
    vault.removeFunds(AMOUNT, sudo, {'from':sudo})
    assert (token.balanceOf(sudo) == ibal + AMOUNT)

    # redeem
    #tx = vault.withdraw(user2, vault.assetsOf(user2),{'from':user2})
    assert share_value2 == vault.balanceOf(user2)
    tx = vault.redeem(share_value2, user2, user2, {'from':user2})
    assert (vault.balanceOf(user2) == 0)
    assert (vault.assetsOf(user2) == 0)
    assert abs(token.balanceOf(user2) - int(b2 * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5

    # add back Funds
    ibal = token.balanceOf(sudo)
    token.approve(vault, AMOUNT, {'from':sudo})
    vault.addFunds(AMOUNT, {'from':sudo})
    assert (token.balanceOf(sudo) == ibal - AMOUNT)


    # withdraw
    tx = vault.withdraw(vault.assetsOf(user), user, user, {'from':user})
    assert abs(token.balanceOf(user) - int(b * (1 + AMOUNT_REBASE2/(b+b2)))) < 10**5
    assert (vault.balanceOf(user) == 0)
    assert (vault.assetsOf(user) == 0)