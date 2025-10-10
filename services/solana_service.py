# services/solana_service.py
from typing import List
from base64 import b64encode

from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import MessageV0
from solders.hash import Hash
from solders.transaction import VersionedTransaction
from solders.null_signer import NullSigner

from services.rpc import Rpc
from core.types import BuiltTx
from core.config import USDC_MINT

TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
RENT_SYSVAR_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

USDC_DECIMALS = 6
MIN_LAMPORTS_FOR_FEES = 2000000  # ~0.002 SOL buffer for fee + small rent

def _u64_le(n: int) -> bytes:
    return n.to_bytes(8, byteorder="little", signed=False)

def _get_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    ata, _ = Pubkey.find_program_address(
        [bytes(owner), bytes(TOKEN_PROGRAM_ID), bytes(mint)],
        ASSOCIATED_TOKEN_PROGRAM_ID,
    )
    return ata

def _ix_create_associated_token_account(payer: Pubkey, owner: Pubkey, mint: Pubkey) -> Instruction:
    ata = _get_associated_token_address(owner, mint)
    metas = [
        AccountMeta(pubkey=payer,             is_signer=True,  is_writable=True),
        AccountMeta(pubkey=ata,               is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner,             is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint,              is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID,  is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT_SYSVAR_ID,    is_signer=False, is_writable=False),
    ]
    return Instruction(ASSOCIATED_TOKEN_PROGRAM_ID, b"", metas)

def _ix_transfer_checked(source: Pubkey, mint: Pubkey, dest: Pubkey, owner: Pubkey, amount: int, decimals: int) -> Instruction:
    data = bytes([12]) + _u64_le(amount) + bytes([decimals])
    metas = [
        AccountMeta(pubkey=source, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint,   is_signer=False, is_writable=False),
        AccountMeta(pubkey=dest,   is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner,  is_signer=True,  is_writable=False),
    ]
    return Instruction(TOKEN_PROGRAM_ID, data, metas)

class SolanaService:
    def __init__(self, rpc: Rpc, usdc_mint: str = USDC_MINT):
        self.rpc = rpc
        self.usdc_mint = Pubkey.from_string(usdc_mint)

    def build_usdc_transfer(self, sender_pubkey: str, recipient_pubkey: str, amount_ui: float) -> BuiltTx:
        sender = Pubkey.from_string(sender_pubkey)
        recipient = Pubkey.from_string(recipient_pubkey)

        # ----------- PRECHECKS: SOL fee & USDC balance -----------
        lamports = self.rpc.get_balance_lamports(str(sender))
        if lamports < MIN_LAMPORTS_FOR_FEES:
            need_sol = (MIN_LAMPORTS_FOR_FEES - lamports) / 1_000_000_000
            raise ValueError(f"Insufficient SOL to pay fees. Top up ~{need_sol:.5f} SOL and try again.")

        # Find sender USDC ATA (may not exist yet)
        sender_token_acc = self.rpc.get_token_account_by_owner(str(sender), str(self.usdc_mint))
        if sender_token_acc is None:
            # If there is no USDC ATA yet, user cannot send a positive amount (balance = 0).
            if amount_ui > 0:
                raise ValueError("Your USDC account doesn't exist yet or has 0 balance. Receive USDC first.")
        else:
            bal_ui = self.rpc.get_token_balance_ui(sender_token_acc)
            if bal_ui < amount_ui:
                raise ValueError(f"Insufficient USDC balance. You have {bal_ui:.6f}, need {amount_ui:.6f}.")

        # ---------------------------------------------------------

        sender_ata = _get_associated_token_address(sender, self.usdc_mint)
        recipient_ata = _get_associated_token_address(recipient, self.usdc_mint)

        ixs: List[Instruction] = []

        # Create ATAs if missing (sender pays)
        if self.rpc.get_account_info(str(sender_ata)) is None:
            ixs.append(_ix_create_associated_token_account(payer=sender, owner=sender, mint=self.usdc_mint))
        if self.rpc.get_account_info(str(recipient_ata)) is None:
            ixs.append(_ix_create_associated_token_account(payer=sender, owner=recipient, mint=self.usdc_mint))

        amount = int(round(amount_ui * (10 ** USDC_DECIMALS)))
        ixs.append(_ix_transfer_checked(
            source=sender_ata, mint=self.usdc_mint, dest=recipient_ata, owner=sender, amount=amount, decimals=USDC_DECIMALS
        ))

        recent = self.rpc.get_latest_blockhash()
        msg = MessageV0.try_compile(
            payer=sender,
            instructions=ixs,
            recent_blockhash=Hash.from_string(recent),
            address_lookup_table_accounts=[],
        )

        # Placeholder Signer for payer; Phantom will replace with a real sig
        signers = [NullSigner(sender)]
        tx = VersionedTransaction(msg, signers)

        return BuiltTx(
            unsigned_b64=b64encode(bytes(tx)).decode(),
            recent_blockhash=recent,
            sender_ata=str(sender_ata),
            recipient_ata=str(recipient_ata),
        )

    def send_signed(self, signed_b64: str) -> str:
        return self.rpc.send_raw_transaction(signed_b64)
