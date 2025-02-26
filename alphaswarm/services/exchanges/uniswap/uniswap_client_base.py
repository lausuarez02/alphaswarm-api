import logging
from abc import abstractmethod
from decimal import Decimal
from typing import List, Tuple

from alphaswarm.config import ChainConfig, TokenInfo
from alphaswarm.core.token import TokenAmount
from alphaswarm.services.chains.evm import ERC20Contract, EVMClient, EVMSigner
from alphaswarm.services.exchanges.base import DEXClient, QuoteResult, SwapResult
from eth_typing import ChecksumAddress, HexAddress
from pydantic import BaseModel
from web3.types import TxReceipt

# Set up logger
logger = logging.getLogger(__name__)


class UniswapQuote(BaseModel):
    pool_address: ChecksumAddress


class UniswapClientBase(DEXClient[UniswapQuote]):
    def __init__(self, chain_config: ChainConfig, version: str) -> None:
        super().__init__(chain_config, UniswapQuote)
        self.version = version
        self._evm_client = EVMClient(chain_config)
        self._router = self._get_router()
        self._factory = self._get_factory()

        logger.info(f"Created {self.__class__.__name__} instance for chain {self.chain}")

    # TODO this would need to become an input parameter for relevant functions
    def get_signer(self) -> EVMSigner:
        return EVMSigner(self.chain_config.private_key)

    @property
    def wallet_address(self) -> ChecksumAddress:
        return EVMClient.to_checksum_address(self.chain_config.wallet_address)

    @abstractmethod
    def _get_router(self) -> ChecksumAddress:
        pass

    @abstractmethod
    def _get_factory(self) -> ChecksumAddress:
        pass

    @abstractmethod
    def _swap(
        self,
        quote: QuoteResult[UniswapQuote],
        slippage_bps: int,
    ) -> List[TxReceipt]:
        pass

    @abstractmethod
    def _get_token_price(self, token_out: TokenInfo, amount_in: TokenAmount) -> QuoteResult[UniswapQuote]:
        pass

    @abstractmethod
    def _get_markets_for_tokens(self, tokens: List[TokenInfo]) -> List[Tuple[TokenInfo, TokenInfo]]:
        pass

    @staticmethod
    def _get_final_swap_amount_received(
        swap_receipt: TxReceipt, token_address: HexAddress, user_address: str, token_decimals: int
    ) -> Decimal:
        """Calculate the final amount of tokens received from a swap by parsing Transfer events.

        Looks through the transaction receipt logs for Transfer events where the recipient matches
        the user's address and sums up the transferred amounts.

        Args:
            swap_receipt (dict): The transaction receipt from the swap
            token_address (HexAddress): Hexed Address of the token to track transfers for
            user_address (str): Address of the user receiving the tokens
            token_decimals (int): Number of decimals for the token

        Returns:
            Decimal: Total amount of tokens received, normalized by token decimals
        """

        TRANSFER_SIG = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

        total_received = 0  # Might be multiple logs if multi-hop or partial fills

        for log in swap_receipt["logs"]:
            if (
                log["address"].lower() == token_address.lower()
                and len(log["topics"]) == 3
                and log["topics"][0].hex().lower() == TRANSFER_SIG
            ):
                # Decode 'from' and 'to'
                # from_addr = "0x" + log["topics"][1].hex()[-40:]
                to_addr = "0x" + log["topics"][2].hex()[-40:]

                if to_addr.lower() == user_address.lower():
                    raw_amount = int(log["data"].hex(), 16)
                    total_received += raw_amount

        # Convert to human-readable amount
        return Decimal(total_received) / (10**token_decimals)

    def swap(
        self,
        quote: QuoteResult[UniswapQuote],
        slippage_bps: int = 100,
    ) -> SwapResult:
        # Create contract instances
        token_out = quote.token_out
        token_out_contract = ERC20Contract(self._evm_client, token_out.checksum_address)
        token_in = quote.token_in
        token_in_contract = ERC20Contract(self._evm_client, token_in.checksum_address)
        amount_in = token_in.to_amount(quote.amount_in)

        logger.info(f"Initiating token swap for {token_in.symbol} to {token_out.symbol}")
        logger.info(f"Wallet address: {self.wallet_address}")

        # Gas balance
        gas_balance = self._evm_client.get_native_balance(self.wallet_address)

        # Log balances
        out_balance = token_out.to_amount_from_base_units(token_out_contract.get_balance(self.wallet_address))
        in_balance = token_in.to_amount_from_base_units(token_in_contract.get_balance(self.wallet_address))
        eth_balance = TokenInfo.Ethereum().to_amount_from_base_units(gas_balance)

        logger.info(f"Out Balance: {out_balance}")
        logger.info(f"In Balance: {in_balance}")
        logger.info(f"Gas balance: {eth_balance}")

        if in_balance < amount_in:
            raise ValueError(f"Cannot perform swap, as you have {in_balance}. Need at least {amount_in}")

        # Each DEX trade is two transactions
        # 1) ERC-20.approve()
        # 2) swap (various functions)

        receipts = self._swap(
            quote=quote,
            slippage_bps=slippage_bps,
        )

        # Get the actual amount of base token received from the swap receipt
        swap_receipt = receipts[1]
        amount_out = self._get_final_swap_amount_received(
            swap_receipt, token_out.checksum_address, self.wallet_address, token_out.decimals
        )

        return SwapResult.build_success(
            amount_out=amount_out,
            amount_in=amount_in.value,
            tx_hash=swap_receipt["transactionHash"].hex(),  # Return the swap tx hash, not the approved tx
        )

    def _approve_token_spending(self, amount: TokenAmount) -> TxReceipt:
        """Handle token approval and return fresh nonce and approval receipt.

        Args:
            amount (TokenAmount): Amount to approve for spending

        Returns:
            TxReceipt: approval_receipt

        Raises:
            ValueError: If approval transaction fails
        """
        token_contract = ERC20Contract(self._evm_client, amount.token_info.checksum_address)
        tx_receipt = token_contract.approve(self.get_signer(), self._router, amount.base_units)
        return tx_receipt

    def get_token_price(self, token_out: TokenInfo, amount_in: TokenAmount) -> QuoteResult[UniswapQuote]:
        logger.debug(
            f"Getting price for {token_out.symbol}/{amount_in.token_info.symbol} on {self.chain} using Uniswap {self.version}"
        )

        return self._get_token_price(token_out=token_out, amount_in=amount_in)

    def get_markets_for_tokens(self, tokens: List[TokenInfo]) -> List[Tuple[TokenInfo, TokenInfo]]:
        """Get list of valid trading pairs between the provided tokens.

        Args:
            tokens: List of tokens to find trading pairs between

        Returns:
            List of token pairs (base, quote) that form valid markets
        """
        return self._get_markets_for_tokens(tokens)
