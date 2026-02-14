// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CharityDonation {
    struct Campaign {
        address owner;
        string title;
        string description;
        uint256 target;
        uint256 deadline;
        uint256 amountCollected;
        uint256 amountWithdrawn;
        string image;
        string category;
        address[] donators;
        uint256[] donations;
        uint256[] timestamps;
        string[] messages;
    }

    mapping(uint256 => Campaign) public campaigns;

    uint256 public numberOfCampaigns = 0;
    uint256 public totalReceived = 0;

    event CampaignCreated(uint256 indexed id, address indexed owner, string title, uint256 target, uint256 deadline, string category);
    event DonationReceived(uint256 indexed campaignId, address indexed donor, uint256 amount, string message, uint256 timestamp);
    event Withdrawal(uint256 indexed campaignId, address indexed owner, uint256 amount, uint256 timestamp);
    event CampaignDeleted(uint256 indexed id, address indexed owner);

    function createCampaign(address _owner, string memory _title, string memory _description, uint256 _target, uint256 _deadline, string memory _image, string memory _category) public returns (uint256) {
        Campaign storage campaign = campaigns[numberOfCampaigns];

        // Validate deadline is in the future
        require(_deadline > block.timestamp, "The deadline should be a date in the future.");

        campaign.owner = _owner;
        campaign.title = _title;
        campaign.description = _description;
        campaign.target = _target;
        campaign.deadline = _deadline;
        campaign.amountCollected = 0;
        campaign.amountWithdrawn = 0;
        campaign.image = _image;
        campaign.category = _category;

        emit CampaignCreated(numberOfCampaigns, _owner, _title, _target, _deadline, _category);

        numberOfCampaigns++;

        return numberOfCampaigns - 1;
    }

    function donateToCampaign(uint256 _id, string memory _message) public payable {
        uint256 amount = msg.value;

        Campaign storage campaign = campaigns[_id];

        // Validate campaign and donation
        require(campaign.deadline > 0, "Campaign does not exist");
        require(block.timestamp <= campaign.deadline, "Campaign has ended");
        require(amount > 0, "Donation amount must be greater than 0");

        // Record donation with timestamp
        campaign.donators.push(msg.sender);
        campaign.donations.push(amount);
        campaign.timestamps.push(block.timestamp);
        campaign.messages.push(_message);

        // Update total amounts
        campaign.amountCollected += amount;
        totalReceived += amount;

        emit DonationReceived(_id, msg.sender, amount, _message, block.timestamp);
    }

    // Campaign owner can withdraw funds
    function withdraw(uint256 _campaignId) public {
        Campaign storage campaign = campaigns[_campaignId];
        
        require(msg.sender == campaign.owner, "Only campaign owner can withdraw");
        require(campaign.deadline > 0, "Campaign does not exist");
        
        uint256 balance = campaign.amountCollected - campaign.amountWithdrawn;
        require(balance > 0, "No funds available to withdraw");

        campaign.amountWithdrawn += balance;

        payable(campaign.owner).transfer(balance);

        emit Withdrawal(_campaignId, campaign.owner, balance, block.timestamp);
    }

    // Get available balance for a campaign
    function getCampaignBalance(uint256 _id) public view returns (uint256) {
        Campaign storage campaign = campaigns[_id];
        return campaign.amountCollected - campaign.amountWithdrawn;
    }

    // Get total contract balance
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function getDonators(uint256 _id) view public returns (address[] memory, uint256[] memory, uint256[] memory, string[] memory) {
        return (campaigns[_id].donators, campaigns[_id].donations, campaigns[_id].timestamps, campaigns[_id].messages);
    }

    function getCampaigns() public view returns (Campaign[] memory) {
        Campaign[] memory allCampaigns = new Campaign[](numberOfCampaigns);

        for(uint i = 0; i < numberOfCampaigns; i++) {
            Campaign storage item = campaigns[i];
            allCampaigns[i] = item;
        }

        return allCampaigns;
    }

    function deleteCampaign(uint256 _id) public {
        require(_id < numberOfCampaigns, "Campaign does not exist");
        require(campaigns[_id].owner == msg.sender, "Only the owner can delete the campaign");

        // Ensure all funds are withdrawn before deletion
        require(getCampaignBalance(_id) == 0, "Must withdraw all funds before deleting campaign");

        emit CampaignDeleted(_id, msg.sender);
        
        delete campaigns[_id];
    }
}
