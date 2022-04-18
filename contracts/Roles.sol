// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;
import "../interfaces/IRole.sol";
import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/Context.sol";

abstract contract Ownable is Context {
    address private _owner;
    bool private is_ownership_initialized;
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev Initializes the contract setting the deployer as the initial owner.
     */
    constructor() {
        _transferOwnership(_msgSender());
    }

    function initializeOwnership(address _account) public {
        require(!is_ownership_initialized, "Ownership is already initialized.");
        _transferOwnership(_account);
        is_ownership_initialized = true;
    }

    function Ownable_init() internal {
        _transferOwnership(_msgSender());
    }

    /**
     * @dev Returns the address of the current owner.
     */
    function owner() public view virtual returns (address) {
        return _owner;
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier onlyOwner() {
        require(owner() == _msgSender(), "Ownable: caller is not the owner");
        _;
    }

    /**
     * @dev Leaves the contract without owner. It will not be possible to call
     * `onlyOwner` functions anymore. Can only be called by the current owner.
     *
     * NOTE: Renouncing ownership will leave the contract without an owner,
     * thereby removing any functionality that is only available to the owner.
     */
    function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Can only be called by the current owner.
     */
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(newOwner);
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Internal function without access restriction.
     */
    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}


abstract contract Roles is Ownable, IRole {

    mapping(address => mapping(bytes32 => bool)) public roles;
    bytes32 public constant ROLE_addRole = keccak256("ROLE_addRole");
    bytes32 public constant ROLE_removeRole = keccak256("ROLE_removeRole");
    bytes32 public constant ROLE_pause = keccak256("ROLE_pause");
    bytes32 public constant ROLE_unpause = keccak256("ROLE_unpause");
    
    bool public is_paused = false;
    mapping(address => bool) internal blacklist;

    /**
     * @dev Initializes the contract setting the deployer as the initial owner.
     */
    constructor() Ownable() {}

    function Roles_init() internal {
        Ownable_init();
    }

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