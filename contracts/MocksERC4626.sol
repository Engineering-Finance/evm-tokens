// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC4626.sol";

contract MockERC4626 is ERC4626 {

    constructor(ERC20 _asset, string memory _name, string memory _symbol) ERC4626(_asset, _name, _symbol)
    {

    }

    function DEBUG_steal_tokens(uint256 amount) external {
        asset_.transfer(msg.sender, amount);
    }
    

}