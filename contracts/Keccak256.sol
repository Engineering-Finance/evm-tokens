// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts v4.4.1 (utils/cryptography/draft-EIP712.sol)

pragma solidity ^0.8.0;

contract Keccak256 {
    function process(string memory _input) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(_input));
    }
}
