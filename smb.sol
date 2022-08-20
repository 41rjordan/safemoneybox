pragma solidity ^0.8.7;
// SPDX-License-Identifier: UNLICENSED

interface IERC20 {
    function totalSupply() external view returns (uint);

    function balanceOf(address account) external view returns (uint);

    function transfer(address recipient, uint amount) external returns (bool);

    function allowance(address owner, address spender) external view returns (uint);

    function approve(address spender, uint amount) external returns (bool);

    function transferFrom(
        address sender,
        address recipient,
        uint amount
    ) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint value);
    event Approval(address indexed owner, address indexed spender, uint value);
}

contract safemoneybox {

    address payable owner;
    bytes32 magicwordhash;
    bytes32 secrethash;

    constructor(bytes32 _magicwordhash, bytes32 _secrethash) {
        require(_magicwordhash != _secrethash, err3);
        owner = payable(msg.sender);
        magicwordhash = _magicwordhash;
        secrethash = _secrethash;
    }

    modifier _ownerOnly() {
        require(msg.sender == owner, "sender is not money box owner");
        _;
    }

    event received(address, uint);

    receive() external payable {
        emit received(msg.sender, msg.value);
    }

    string constant err1 = "magic word is incorrect";
    string constant err2 = "new magic word can't be the same as current";
    string constant err3 = "new magic word can't be the same as secret";
    string constant err4 = "insufficient funds";

    function recovery(bytes memory secretReveal, bytes32 newSecretHash) external {
        require(keccak256(secretReveal) == secrethash, "secret is incorrect");
        require(newSecretHash != secrethash, "new secret can't be the same as current");

        secrethash = newSecretHash;
        owner = payable(msg.sender);
    }

    function withdrawETH(uint256 amount, bytes memory magicwordReveal, bytes32 newMagicwordHash) external _ownerOnly {
        require(keccak256(magicwordReveal) == magicwordhash, err1);
        require(newMagicwordHash != magicwordhash, err2);
        require(newMagicwordHash != secrethash, err3);
        magicwordhash = newMagicwordHash;
        require(address(this).balance >= amount, err4);

        owner.transfer(amount);
    }

    function withdrawERC20(address contractAddress, uint256 amount, bytes memory magicwordReveal, bytes32 newMagicwordHash) external _ownerOnly {
        require(keccak256(magicwordReveal) == magicwordhash, err1);
        require(newMagicwordHash != magicwordhash, err2);
        require(newMagicwordHash != secrethash, err3);
        magicwordhash = newMagicwordHash;
        require(IERC20(contractAddress).balanceOf(address(this)) >= amount, err4);
        IERC20(contractAddress).transfer(owner, amount);
    }
}