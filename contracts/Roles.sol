// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;
import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/access/Ownable.sol";
import "../interfaces/IRole.sol";

abstract contract Roles is Ownable, IRole {

    mapping(address => mapping(bytes32 => bool)) public roles;
    bytes32 public immutable ROLE_addRole = keccak256("ROLE_addRole");
    bytes32 public immutable ROLE_removeRole = keccak256("ROLE_removeRole");
    bytes32 public immutable ROLE_pause = keccak256("ROLE_pause");
    bytes32 public immutable ROLE_unpause = keccak256("ROLE_unpause");
    
    bool public is_paused = false;
    mapping(address => bool) internal blacklist;

    function hasRole(address account, bytes32 role) public virtual view returns (bool) {
        return roles[account][role] || owner() == _msgSender();
    }

    function hasRole(bytes32 role) public virtual view returns (bool) {
        return hasRole(_msgSender(), role);
    }

    function addRole(address account, bytes32 _role) public virtual onlyRole(ROLE_addRole) {
        roles[account][_role] = true;
    }

    function removeRole(address account, bytes32 _role) public virtual onlyRole(ROLE_removeRole) {
        roles[account][_role] = false;
    }

    function pause() public virtual onlyRole(ROLE_pause) {
        is_paused = true;
    }

    function pause(address account) public virtual onlyRole(ROLE_pause) {
        blacklist[account] = true;
    }

    function unpause() public virtual onlyRole(ROLE_unpause) {
        is_paused = false;
    }

    function unpause(address account) public virtual onlyRole(ROLE_unpause) {
        blacklist[account] = false;
    }

    function paused(address account) public virtual view returns (bool) {
        if(owner() == account) return false;
        return is_paused || blacklist[account];
    }

    function paused() public virtual view returns (bool) {
        return paused(_msgSender());
    }

    modifier active() {
        if(owner() != _msgSender()) {
            require(!is_paused, "Contract is paused");
            require(!blacklist[_msgSender()], "Account is blacklisted");
        }
        _;
    }

    modifier onlyRole(bytes32 _role) {
        if(owner() != _msgSender()) {
            require(hasRole(_role), "Role not allowed");
        }
        _;
    }
}