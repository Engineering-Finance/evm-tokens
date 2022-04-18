// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/IERC4626.sol";
import "./EnFi20.sol";

contract EnFi4626 is EnFi20, IERC4626 {

    /// @notice The underlying token the vault accepts.
    ERC20 public immutable asset_;

    uint256 internal baseUnit;
    uint256 public usedFunds;

    /// @notice Creates a new vault that accepts a specific underlying token.
    /// @param _asset The ERC20 compliant token the vault should accept.
    /// @param _name The name for the vault token.
    /// @param _symbol The symbol for the vault token.

    constructor(address _asset, string memory _name, string memory _symbol) EnFi20(_name, _symbol, ERC20(_asset).decimals(), 0) {
        asset_ = ERC20(_asset);
        baseUnit = 10**asset_.decimals();
    }

    function asset() public virtual view returns (address assetTokenAddress){
        return address(asset_);
    }

    function totalAssets() public virtual view returns (uint256 totalManagedAssets) {
        return usedFunds + asset_.balanceOf(address(this));
    }

    function convertToShares(uint256 assets) public virtual view returns (uint256 shares) {
        shares = (assets * baseUnit) / assetsPerShare();
    }

    function convertToAssets(uint256 shares) public virtual view returns (uint256 assets) {
        if (totalSupply() == 0) {
            return 0;
        }
        assets = (shares * assetsPerShare()) / baseUnit;
    }

    function maxDeposit(address receiver) public virtual view returns (uint256 maxAssets){
        maxAssets = type(uint256).max;
    }
    
    function previewDeposit(uint256 assets) public virtual view returns (uint256 shares) {
        return convertToShares(assets);
    }

    function _safeTransferFrom(ERC20 token_, address from_, address to_, uint256 amount_) private returns (uint256 result) {
        uint256 initialBalance = token_.balanceOf(to_);
        token_.transferFrom(from_, to_, amount_);
        result = token_.balanceOf(to_) - initialBalance;
    }

    function deposit(uint256 assets, address receiver) public virtual returns (uint256 shares){
        uint256 exchangeRate_ = assetsPerShare();
        uint256 receivedAssets = _safeTransferFrom(asset_, _msgSender(), address(this), assets);
        shares = (receivedAssets * baseUnit) / exchangeRate_;
        require((shares!=0), "ZERO_SHARES");
        _mint(receiver, shares);
        emit Deposit(_msgSender(), receiver, assets, shares);
    }

    function maxMint(address receiver) public virtual view returns (uint256 maxShares) {
        maxShares = type(uint256).max;
    }

    function previewMint(uint256 shares) public virtual view returns (uint256 assets){
        assets = (shares * assetsPerShare()) / baseUnit;
    }

    function mint(uint256 shares, address receiver) public virtual returns (uint256 assets){
        uint256 exchangeRate_ = assetsPerShare();
        assets = _safeTransferFrom(asset_, _msgSender(), address(this), previewMint(shares));
        uint256 shares_ = (assets * baseUnit) / exchangeRate_;
        require((shares_!=0), "ZERO_SHARES");
        _mint(receiver, shares_);
        emit Deposit(_msgSender(), receiver, assets, shares_);
    }

    function maxWithdraw(address owner) public virtual view returns (uint256 maxAssets){
        //maxAssets = type(uint256).max;

        return assetsOf(owner);
    }
    
    function previewWithdraw(uint256 assets) public virtual view returns (uint256 shares) {
        if (totalSupply() == 0 ) {
            return 0;
        }
        return (assets * baseUnit ) / assetsPerShare();
    }

    function withdraw(uint256 assets, address receiver, address owner) public virtual returns (uint256 shares){
        shares = previewWithdraw(assets);
        _spendAllowance(owner, _msgSender(), shares);
        // Determine the equivalent assets of shares and burn them.
        // This will revert if the user does not have enough shares.
        _burn(owner, shares);
        emit Withdraw(_msgSender(), receiver, owner, assets, shares);
        asset_.transfer(receiver, assets);
    }

    function maxRedeem(address owner) public virtual view returns (uint256 maxShares){
        //maxShares = type(uint256).max;

        return balanceOf(owner);
    }

    function previewRedeem(uint256 shares) public virtual view returns (uint256 assets) {
        return convertToAssets(shares);
    }
    function redeem(uint256 shares, address receiver, address owner) public virtual returns (uint256 assets){
        require((assets = previewRedeem(shares)) != 0, "ZERO_ASSETS");
        _spendAllowance(owner, _msgSender(), shares);
        _burn(owner, shares);

        emit Withdraw(_msgSender(), receiver, owner, assets, shares);
        asset_.transfer(receiver, assets);
    }

    /*///////////////////////////////////////////////////////////////
                        VAULT ACCOUNTING LOGIC
    //////////////////////////////////////////////////////////////*/

    function assetsOf(address depositor) public virtual view returns (uint256 assets) {
        assets = (balanceOf(depositor) * assetsPerShare()) / baseUnit;
    }

    function assetsPerShare() public virtual view returns (uint256 assetsPerUnitShare) {
        uint256 shareSupply = totalSupply();

        if (shareSupply == 0) return baseUnit;

        // Calculate the exchange rate by dividing the total holdings by the share supply.
        assetsPerUnitShare = (totalAssets() * baseUnit) / shareSupply;
    }

    function depositFrom(uint256 assets, address receiver) public virtual returns (uint256 shares) {
        uint256 exchangeRate_ = assetsPerShare();
        // Transfer in underlying tokens from the user.
        uint256 assets_ = _safeTransferFrom(asset_, tx.origin, address(this), assets);
        shares = (assets_ * baseUnit) / exchangeRate_;
        require((shares!=0), "ZERO_SHARES");
        _mint(receiver, shares);
        emit Deposit(tx.origin, receiver, assets_, shares);
    }
}