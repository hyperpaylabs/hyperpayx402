import express from "express";
import cors from "cors";
import { config } from "dotenv";
import bs58 from "bs58";
import nacl from "tweetnacl";
import admin from "firebase-admin";
import { Connection, PublicKey, Transaction } from "@solana/web3.js";
import { getAssociatedTokenAddress, TOKEN_PROGRAM_ID } from "@solana/spl-token";
import crypto from "crypto";

config();

const app = express();
app.use(express.json());
app.use(cors({ origin: "*", allowedHeaders: ["Content-Type", "X-PAYMENT"] }));

// Firebase Admin
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert("./serviceAccount.json"),
    databaseURL: process.env.FIREBASE_DB_URL,
  });
}

// Solana connection
const RPC_URL = process.env.RPC_URL!;
const connection = new Connection(RPC_URL, "confirmed");
const MEMO_PROGRAM_ID = new PublicKey("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr");
const USDC_MINT = process.env.USDC_MINT || "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";
const USDC_DECIMALS = Number(process.env.USDC_DECIMALS || 6);
const seen = new Set<string>();

// Wallet login verification
app.post("/auth/verify-wallet", async (req, res) => {
  try {
    const { publicKey, signature } = req.body;
    if (!publicKey || !signature) return res.status(400).json({ error: "Missing fields" });

    const message = new TextEncoder().encode("Login to Hyper Pay");
    const sig = bs58.decode(signature);
    const pub = bs58.decode(publicKey);
    const verified = nacl.sign.detached.verify(message, sig, pub);
    if (!verified) return res.status(401).json({ error: "Invalid signature" });

    const token = await admin.auth().createCustomToken(publicKey);
    res.json({ token });
  } catch (e: any) {
    res.status(500).json({ error: e.message });
  }
});

// x402 Requirement
app.get("/pay", (req, res) => {
  const { recipient, amount, note } = req.query;
  if (!recipient || !amount) return res.status(400).json({ error: "Missing params" });

  const atomic = BigInt(Math.round(Number(amount) * 10 ** USDC_DECIMALS)).toString();
  const requirement = {
    scheme: "exact",
    network: "solana",
    payTo: recipient,
    asset: { address: USDC_MINT, decimals: USDC_DECIMALS },
    amount: atomic,
    note: note || undefined,
  };
  return res.status(402).json({ x402Version: 1, accepts: [requirement], facilitator: "httpay" });
});

app.post("/pay", async (req, res) => {
  try {
    const xHeader = Array.isArray(req.headers["x-payment"])
      ? req.headers["x-payment"][0]
      : req.headers["x-payment"];
    const { serializedTransaction } = req.body;
    if (!xHeader || !serializedTransaction)
      return res.status(400).json({ error: "Missing data" });

    const requirement = JSON.parse(Buffer.from(xHeader, "base64").toString());
    const raw = Buffer.from(serializedTransaction, "base64");
    const hash = crypto.createHash("sha256").update(raw).digest("hex");
    if (seen.has(hash)) return res.status(409).json({ error: "Replay detected" });

    const tx = Transaction.from(raw);
    const payer = tx.feePayer!;
    const mint = new PublicKey(USDC_MINT);
    const recipient = new PublicKey(requirement.payTo);
    const expectedSourceATA = await getAssociatedTokenAddress(mint, payer);
    const expectedDestATA = await getAssociatedTokenAddress(mint, recipient);

    let transferVerified = false;
    let memoVerified = requirement.note ? false : true;

    for (const ix of tx.instructions) {
      if (ix.programId.equals(TOKEN_PROGRAM_ID)) {
        const data = Buffer.from(ix.data);
        const discr = data[0];
        if (discr !== 3 && discr !== 12) continue;
        const src = ix.keys[0].pubkey;
        const dest = ix.keys[discr === 12 ? 2 : 1].pubkey;
        if (!src.equals(expectedSourceATA) || !dest.equals(expectedDestATA)) continue;
        transferVerified = true;
      }
      if (requirement.note && ix.programId.equals(MEMO_PROGRAM_ID)) {
        const memo = Buffer.from(ix.data).toString();
        if (memo === requirement.note) memoVerified = true;
      }
    }

    if (!transferVerified) return res.status(400).json({ error: "No USDC transfer" });
    if (!memoVerified) return res.status(400).json({ error: "Memo mismatch" });

    const sig = await connection.sendRawTransaction(raw);
    await connection.confirmTransaction(sig, "confirmed");

    seen.add(hash);

    // Construct full x402-compliant response
    const paymentResponse = {
      x402Version: 1,
      settled: true,
      scheme: "exact",
      facilitator: "hyperpay",
      network: "solana",
      txHash: sig,
      payTo: requirement.payTo,
      asset: requirement.asset,
      amount: requirement.amount,
      note: requirement.note || null,
      timestamp: new Date().toISOString(),
    };

    // Add base64 header for decodeXPaymentResponse()
    res.setHeader(
      "X-PAYMENT-RESPONSE",
      Buffer.from(JSON.stringify(paymentResponse)).toString("base64")
    );

    // Return full JSON as body too
    res.status(200).json(paymentResponse);
  } catch (e: any) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});


app.listen(4021, () => console.log("Hyper Pay x402 server running on port 4021"));
