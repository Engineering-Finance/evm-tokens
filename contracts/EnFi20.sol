// SPDX-License-Identifier: MIT
// based on OpenZeppelin Contracts (token/ERC20/extensions/draft-ERC20Permit.sol)

pragma solidity ^0.8.0;
import "./ERC20.sol";
import "./ERC20Permit.sol";
import "../interfaces/IEnFi20.sol";
import "../interfaces/IOwnableInit.sol";

contract EnFi20 is IEnFi20, ERC20Permit, Roles {
    uint8 _decimals;

    bytes32 public constant ROLE_xtransfer = keccak256("ROLE_xtransfer");
    bytes32 public constant ROLE_xapprove = keccak256("ROLE_xapprove");
    bytes32 public constant ROLE_withdrawEth = keccak256("ROLE_withdrawEth");
    bytes32 public constant ROLE_clone = keccak256("ROLE_clone");
    bytes32 public constant ROLE_init = keccak256("ROLE_init");

    address master_contract;
    bool internal is_initialized;

    mapping (bytes32 => address) public clones;

    constructor(
        string memory _name,
        string memory _symbol,
        uint8 decimals_,
        uint256 _supply
    ) ERC20(_name, _symbol) ERC20Permit(_name) Roles() {
        _decimals = decimals_;
        _mint(msg.sender, _supply * 10**_decimals);
        master_contract = address(this);
    }

    function decimals() public view virtual override (ERC20, IEnFi20) returns (uint8) {
        return _decimals;
    }
    
    function name() public view virtual override (ERC20, IEnFi20) returns (string memory) {
        return super.name();
    }

    function symbol() public view virtual override (ERC20, IEnFi20) returns (string memory) {
        return super.symbol();
    }

    function getOwner() public view virtual returns (address) {
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

    function xtransfer(address _token, address _creditor, uint256 _value) public virtual active onlyRole(ROLE_xtransfer) returns (bool) {
        return IERC20(_token).transfer(_creditor, _value);
    }

    function xapprove(address _token, address _spender, uint256 _value) public virtual active onlyRole(ROLE_xapprove) returns (bool) {
        return IERC20(_token).approve(_spender, _value);
    }

    function withdrawEth() public virtual active onlyRole(ROLE_withdrawEth) returns (bool) {
        return payable(owner()).send(address(this).balance);
    }

    receive() external virtual payable {
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

    function isMasterContract() public view returns(bool) {
        return master_contract == address(this);
    }

    function getParams(
        string memory _name,
        string memory _symbol,
        uint8 decimals_,
        uint256 _supply
    ) public pure returns (bytes memory) {
        return abi.encode(_name, _symbol, decimals_, _supply);
    }

    function EnFi20_init(string memory _name, string memory _symbol, uint8 decimals_, uint256 _supply) internal {
        ERC20_init(_name, _symbol);
        ERC20Permit_init(_name);
        Roles_init();
        _decimals = decimals_;
        _mint(msg.sender, _supply * 10**_decimals);
    }

    function init(bytes memory _initdata) public virtual onlyRole(ROLE_init) {
        require(!is_initialized, "Collateral already initialized");
        (string memory _name, string memory _symbol, uint8 decimals_, uint256 _supply) = abi.decode(_initdata, (string, string, uint8, uint256));
        EnFi20_init(_name, _symbol, decimals_, _supply);
        is_initialized = true;
    }

    function clone() public virtual onlyRole(ROLE_clone) returns (address instance_){
        require(isMasterContract(), "Only master contract can clone");

        // Takes the first 20 bytes of the masterContract's address
        bytes20 _bytes = bytes20(address(this));
        bytes32 _cloneid = keccak256(abi.encodePacked(master_contract, _bytes));
        if(clones[_cloneid] != address(0)) {
            return clones[_cloneid];
        }

        // Creates clone, more info here: https://blog.openzeppelin.com/deep-dive-into-the-minimal-proxy-contract/
        assembly {
            let _clone := mload(0x40)
            mstore(_clone, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73000000000000000000000000)
            mstore(add(_clone, 0x14), _bytes)
            mstore(add(_clone, 0x28), 0x5af43d82803e903d91602b57fd5bf30000000000000000000000000000000000)
            instance_ := create2(0, _clone, 0x37, _cloneid)
        }
        clones[_cloneid] = instance_;

        // transfer ownership to message sender.
        IOwnableInit(instance_).initializeOwnership(_msgSender());
    }
}