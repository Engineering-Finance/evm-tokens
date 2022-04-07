// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v4.5.0) (token/ERC20/IERC20.sol)

pragma solidity ^0.8.0;
interface IRole {

    /** access control functions **/

    /**
     * @dev function hasRole(account, role)
     * @dev returns true if account is the owner of the token
     * @dev or if account has the defined _role
     */
    function hasRole(address account, bytes32 role) external view returns (bool has_role);

    /**
     * @dev function hasRole(role)
     * @dev returns true if sender is the owner of the token
     * @dev or if sender has the defined _role
     */
    function hasRole(bytes32 role) external view returns (bool has_role);

    /**
     * @dev function addRole(account, role)
     * @dev adds role to account
     */
    function addRole(address account, bytes32 role) external;

    /**
     * @dev function removeRole(account, role)
     * @dev removes role from account
     */
    function removeRole(address account, bytes32 role) external;

    /**
     * @dev function pause()
     * @dev pauses the token
     */
    function pause() external;

    /**
     * @dev function pause(account)
     * @dev pauses the token for this account.
     */
    function pause(address account) external;

    /**
     * @dev function unpause()
     * @dev unpauses the token
     */
    function unpause() external;

    /**
     * @dev function unpause(account)
     * @dev unpauses the token for this account.
     */
    function unpause(address account) external;
}