"""rxn4chemistry initialization."""
__name__ = "RXN4Chemistry"
__version__ = "1.0.0"

import os
import sys
from loguru import logger

if not bool(int(os.environ.get("RXN4CHEMISTRY_DEBUG", "0"))):
    logger.remove()
    logger.add(sys.stderr, level="INFO")

from .core import RXN4ChemistryWrapper  # noqa
