const anchor = require("@coral-xyz/anchor");
const { PublicKey, Keypair, LAMPORTS_PER_SOL } = require("@solana/web3.js");
const fs = require('fs');

async function main() {
    // 1. 加载说明书 (IDL)
    const idl = JSON.parse(fs.readFileSync("./src/charity_idl.json", "utf8"));
    const programId = new PublicKey("6biq8rnJUgQRLKavwXsbnuPX6aVB..."); // 你的部署ID

    // 2. 连接到 Solana Devnet
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);
    const program = new anchor.Program(idl, programId, provider);

    console.log("🚀 开始为 Solana 账本生成模拟数据...");

    const recipients = [
        { title: "WaterProject", desc: "Clean Water Initiative" },
        { title: "CodingCamp", desc: "Rural Coding Camp" }
    ];

    for (const res of recipients) {
        // 计算活动的 PDA 地址
        const [campaignPda] = await PublicKey.findProgramAddress(
            [Buffer.from("campaign"), provider.wallet.publicKey.toBuffer(), Buffer.from(res.title)],
            program.programId
        );

        try {
            console.log(`正在创建活动: ${res.desc}`);
            await program.methods
                .createCampaign(
                    res.title, 
                    res.desc, 
                    new anchor.BN(5 * LAMPORTS_PER_SOL), // 目标 5 SOL
                    new anchor.BN(Math.floor(Date.now() / 1000) + 86400)
                )
                .accounts({
                    campaign: campaignPda,
                    user: provider.wallet.publicKey,
                    systemProgram: anchor.web3.SystemProgram.programId,
                })
                .rpc();
            
            // 模拟捐款
            console.log(`正在为 ${res.title} 注入模拟捐款...`);
            await program.methods
                .donate(new anchor.BN(0.5 * LAMPORTS_PER_SOL))
                .accounts({
                    campaign: campaignPda,
                    user: provider.wallet.publicKey,
                    systemProgram: anchor.web3.SystemProgram.programId,
                })
                .rpc();
        } catch (e) {
            console.log("该活动可能已存在，跳过创建。");
        }
    }
    console.log("✅ 数据填充完成！现在去刷新你的网页查看成果。");
}

main().catch(console.error);