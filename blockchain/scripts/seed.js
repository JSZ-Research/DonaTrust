const hre = require("hardhat");

async function main() {
  console.log("Starting seed script...");

  const signers = await hre.ethers.getSigners();
  if (signers.length < 20) {
    console.warn(`Warning: Requested 20 accounts but only got ${signers.length}. Ensure hardhat.config.js is configured with enough accounts.`);
  }

  const institutionalDonors = [
    { name: "Global Hope Foundation", signerIndex: 0 }, 
    { name: "Apex Capital Charity",   signerIndex: 1 }, 
    { name: "Future Education Trust", signerIndex: 2 }, 
  ];

  const individualDonors = [
    { name: "Liam Johnson",    signerIndex: 3 }, 
    { name: "Emma Williams",   signerIndex: 4 }, 
    { name: "Noah Brown",      signerIndex: 5 }, 
    { name: "Olivia Jones",    signerIndex: 6 }, 
    { name: "Sophia Garcia",   signerIndex: 7 }, 
  ];

  const recipients = [
    { name: "Student: Lucas Miller",         signerIndex: 8 },  
    { name: "Student: Ava Davis",            signerIndex: 9 },  
    { name: "Project: Clean Water Initiative", signerIndex: 10 }, 
    { name: "Project: Rural Coding Camp",    signerIndex: 11 }, 
    { name: "Family: The Wilson Family",     signerIndex: 12 }, 
    { name: "Scholarship: STEM for Girls",   signerIndex: 13 }, 
  ];

  console.log("Deploying CharityPlatform...");
  const CharityPlatform = await hre.ethers.getContractFactory("CharityPlatform");
  const charity = await CharityPlatform.deploy();
  await charity.waitForDeployment();
  const charityAddress = await charity.getAddress();
  console.log(`CharityPlatform deployed to: ${charityAddress}`);

  
  console.log("\n--- Registering Users ---");

  
  for (const donor of institutionalDonors) {
    const signer = signers[donor.signerIndex];
    const tx = await charity.connect(signer).registerDonor(donor.name);
    await tx.wait();
    console.log(`Registered Institutional Donor: ${donor.name} (${signer.address})`);
  }

  
  for (const donor of individualDonors) {
    const signer = signers[donor.signerIndex];
    const tx = await charity.connect(signer).registerDonor(donor.name);
    await tx.wait();
    console.log(`Registered Individual Donor: ${donor.name} (${signer.address})`);
  }

  
  for (const recipient of recipients) {
    const signer = signers[recipient.signerIndex];
    const tx = await charity.connect(signer).registerRecipient(recipient.name);
    await tx.wait();
    console.log(`Registered Recipient: ${recipient.name} (${signer.address})`);
  }

  
  console.log("\n--- Generating 30 Random Donations ---");

  const donations = [];
  const recipientDonationCounts = new Map(); 

  recipients.forEach(r => recipientDonationCounts.set(r.name, new Set())); 

 
  const getRandomAmount = (min, max) => {
    const amount = Math.random() * (max - min) + min;
    return hre.ethers.parseEther(amount.toFixed(4)); 
  };

  const allDonors = [...institutionalDonors, ...individualDonors];

  for (let i = 0; i < 30; i++) {
    let donor, recipient;
    let amount;

    
    const needyRecipients = recipients.filter(r => recipientDonationCounts.get(r.name).size < 2);

    if (needyRecipients.length > 0) {
      
      recipient = needyRecipients[Math.floor(Math.random() * needyRecipients.length)];
      
      
      donor = allDonors[Math.floor(Math.random() * allDonors.length)];
      
      
      const existingDonors = recipientDonationCounts.get(recipient.name);
      const availableDonors = allDonors.filter(d => !existingDonors.has(d.name));
      
      if (availableDonors.length > 0) {
        donor = availableDonors[Math.floor(Math.random() * availableDonors.length)];
      } else {
         
         donor = allDonors[Math.floor(Math.random() * allDonors.length)]; 
      }

    } else {
     
      donor = allDonors[Math.floor(Math.random() * allDonors.length)];
      recipient = recipients[Math.floor(Math.random() * recipients.length)];
    }

    
    const isInstitution = institutionalDonors.some(d => d.name === donor.name);
    if (isInstitution) {
      amount = getRandomAmount(5.0, 10.0); 
    } else {
      amount = getRandomAmount(0.1, 1.0);  
    }

   
    recipientDonationCounts.get(recipient.name).add(donor.name);

    donations.push({ donor, recipient, amount });
  }

  
  for (const [index, donation] of donations.entries()) {
    const donorSigner = signers[donation.donor.signerIndex];
    const recipientSigner = signers[donation.recipient.signerIndex];
    
    
    const tx = await charity.connect(donorSigner).donate(recipientSigner.address, { value: donation.amount });
    await tx.wait();

    const amountEth = hre.ethers.formatEther(donation.amount);
    console.log(`[${index + 1}/30] [Transferred] ${donation.donor.name} -> ${donation.recipient.name} (${amountEth} ETH)`);
  }

  console.log("\nSeeding Complete!");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
