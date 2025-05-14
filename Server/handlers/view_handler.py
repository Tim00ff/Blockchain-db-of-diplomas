from ..utils import response_formatter
from ..models import Blockchain

def handle_view_block(blockchain: Blockchain, block_id: str) -> str:
    """Обработка запроса на просмотр блока"""
    try:
        block = blockchain.get_block(int(block_id))
        return response_formatter.format_response("VIEW_BLOCK", block)
    except (ValueError, IndexError):
        return response_formatter.format_error("Invalid block ID")