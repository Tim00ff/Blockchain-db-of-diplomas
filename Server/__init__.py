"""
Main package initialization
Exposes core components for easy access
"""

# Core components
from .core import (
    BlockchainServer,
    RequestRouter
)
# Models
from .models import (
    User,
    MiningTask,
    Blockchain,
    Block
)
# Handlers
from .handlers import (
    handle_add_block,
    handle_mine_command,
    handle_view_block,
    authenticate
)

# Utils
from .utils import (
    format_response,
    format_error,
    validate_block_data,
    validate_credentials
)

# Entrypoint
from .entrypoints import (
 start_server
)

__all__ = [
    # Core
    'BlockchainServer',
    'RequestRouter',

    # Models
    'User',
    'MiningTask',
    'Blockchain',
    'Block',

    # Handlers
    'handle_add_block',
    'handle_mine_command',
    'handle_view_block',
    'authenticate',

    # Utils
    'format_response',
    'format_error',
    'validate_block_data',
    'validate_credentials',

    # Entrypoint
    'start_server'
]
