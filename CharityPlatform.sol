// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CharityPlatform {
    struct Donor {
        string name;
        address wallet;
    }

    struct Recipient {
        string name;
        address wallet;
        uint256 totalReceived;
    }

    mapping(address => Donor) public donors;
    mapping(address => Recipient) public recipients;

    event DonorRegistered(address indexed wallet, string name);
    event RecipientRegistered(address indexed wallet, string name);
    event DonationReceived(address indexed donor, address indexed recipient, uint256 amount);

    function registerDonor(string memory _name) public {
        donors[msg.sender] = Donor(_name, msg.sender);
        emit DonorRegistered(msg.sender, _name);
    }

    function registerRecipient(string memory _name) public {
        recipients[msg.sender] = Recipient(_name, msg.sender, 0);
        emit RecipientRegistered(msg.sender, _name);
    }

    function donate(address _recipient) public payable {
        require(msg.value > 0, "Donation must be greater than 0");
        require(bytes(recipients[_recipient].name).length > 0, "Recipient not registered");

        recipients[_recipient].totalReceived += msg.value;
        
        // In a real app, funds might be held or transferred. 
        // For this seed script visualization, we just emit the event and transfer.
        payable(_recipient).transfer(msg.value);

        emit DonationReceived(msg.sender, _recipient, msg.value);
    }
}
