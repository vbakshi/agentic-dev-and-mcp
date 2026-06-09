"""Agent factories for the sales orchestration workflow."""

from .emailer import EmailerPipeline
from .sales_manager import SalesManagerFactory
from .sales_writers import SalesWriterPool

__all__ = [
    "EmailerPipeline",
    "SalesManagerFactory",
    "SalesWriterPool",
]
