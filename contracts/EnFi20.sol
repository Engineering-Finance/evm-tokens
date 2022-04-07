// SPDX-License-Identifier: MIT
// based on OpenZeppelin Contracts (token/ERC20/extensions/draft-ERC20Permit.sol)

pragma solidity ^0.8.0;
import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC20/ERC20.sol";
import "../interfaces/IEnFi20.sol";
import "./ERC20Permit.sol";

contract EnFi20 is IEnFi20, ERC20Permit, Roles {
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _supply
    ) ERC20(_name, _symbol) ERC20Permit(_name) {
        _mint(msg.sender, _supply);
    }

    bytes32 public immutable ROLE_xtransfer = keccak256("ROLE_xtransfer");
    bytes32 public immutable ROLE_xapprove = keccak256("ROLE_xapprove");
    bytes32 public immutable ROLE_withdrawEth = keccak256("ROLE_withdrawEth");

    function decimals() public view virtual override (ERC20, IEnFi20) returns (uint8) {
        return super.decimals();
    }
    
    function name() public view virtual override (ERC20, IEnFi20) returns (string memory) {
        return super.name();
    }

    function symbol() public view virtual override (ERC20, IEnFi20) returns (string memory) {
        return super.symbol();
    }

    function getOwner() public view returns (address) {
        return owner();
    }

    function totalSupply() public view virtual override (ERC20, IEnFi20) returns (uint256) {
        return super.totalSupply();
    }

    function balanceOf(address account) public view virtual override (ERC20, IEnFi20) returns (uint256) {
        return super.balanceOf(account);
    }

    function allowance(address _owner, address spender) public view virtual override (ERC20, IEnFi20) returns (uint256) {
        return super.allowance(_owner, spender);
    }

    function xtransfer(address _token, address _creditor, uint256 _value) public active onlyRole(ROLE_xtransfer) returns (bool) {
        return IERC20(_token).transfer(_creditor, _value);
    }

    function xapprove(address _token, address _spender, uint256 _value) public active onlyRole(ROLE_xapprove) returns (bool) {
        return IERC20(_token).approve(_spender, _value);
    }

    function withdrawEth() public active onlyRole(ROLE_withdrawEth) returns (bool) {
        return payable(owner()).send(address(this).balance);
    }

    receive() external payable {
        emit Received(msg.sender, msg.value);
    }

    function transferFrom(address sender, address recipient, uint256 amount) public active virtual override (ERC20, IEnFi20) returns (bool) {
        return super.transferFrom(sender, recipient, amount);
    }

    function transfer(address recipient, uint256 amount) public active virtual override (ERC20, IEnFi20) returns (bool) {
        return super.transfer(recipient, amount);
    }

    function approve(address spender, uint256 amount) public active virtual override (ERC20, IEnFi20) returns (bool) {
        return super.approve(spender, amount);
    }
}