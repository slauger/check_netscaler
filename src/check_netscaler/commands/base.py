"""
Base class for all check commands
"""

from abc import ABC, abstractmethod
from argparse import Namespace
from typing import Any, Dict, List, Optional

from check_netscaler.client import NITROClient


class CheckResult:
    """Result of a check command execution"""

    def __init__(
        self,
        status: int,
        message: str,
        perfdata: Optional[Dict[str, Any]] = None,
        long_output: Optional[List[str]] = None,
    ):
        """
        Initialize check result

        Args:
            status: Exit code (0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN)
            message: Main status message
            perfdata: Performance data dictionary
            long_output: Additional output lines
        """
        self.status = status
        self.message = message
        self.perfdata = perfdata or {}
        self.long_output = long_output or []


class BaseCommand(ABC):
    """Base class for all check commands"""

    def __init__(self, client: NITROClient, args: Namespace):
        """
        Initialize command

        Args:
            client: NITRO API client
            args: Parsed command-line arguments
        """
        self.client = client
        self.args = args

    @abstractmethod
    def execute(self) -> CheckResult:
        """
        Execute the check command

        Returns:
            CheckResult with status, message, and optional perfdata

        Raises:
            NITROException: On API errors
        """
        raise NotImplementedError("Subclasses must implement execute()")
