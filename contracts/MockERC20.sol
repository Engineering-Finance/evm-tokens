
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC20/ERC20.sol";

contract MockERC20 is ERC20 {

    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_){
    }

    function DEBUG_mint(address receiver, uint256 amount) public {
        _mint(receiver, amount);
    }
}