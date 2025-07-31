"""Base command interface for CLI commands"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommandContext:
    """Context object containing all information needed by commands"""

    args: Any  # Parsed command line arguments
    config: Dict[str, Any]  # Configuration settings
    dependencies: Dict[str, Any]  # Injected dependencies (use cases, services, etc.)

    def get_dependency(self, key: str) -> Any:
        """Get a dependency by key

        Args:
            key: Dependency key

        Returns:
            Dependency instance

        Raises:
            KeyError: If dependency not found
        """
        if key not in self.dependencies:
            raise KeyError(f"Dependency '{key}' not found in context")
        return self.dependencies[key]


@dataclass
class CommandResult:
    """Result of command execution"""

    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None

    @property
    def failed(self) -> bool:
        """Check if command failed"""
        return not self.success


class Command(ABC):
    """Abstract base class for all CLI commands"""

    def __init__(self, name: str, description: str):
        """Initialize command

        Args:
            name: Command name
            description: Command description
        """
        self.name = name
        self.description = description
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def execute(self, context: CommandContext) -> CommandResult:
        """Execute the command

        Args:
            context: Command context with args and dependencies

        Returns:
            Command result
        """
        pass

    def validate(self, context: CommandContext) -> Optional[str]:
        """Validate command arguments and context

        Args:
            context: Command context

        Returns:
            Error message if validation fails, None otherwise
        """
        return None

    def __call__(self, context: CommandContext) -> CommandResult:
        """Make command callable

        Args:
            context: Command context

        Returns:
            Command result
        """
        # Validate first
        error_msg = self.validate(context)
        if error_msg:
            return CommandResult(
                success=False, message=f"Validation failed: {error_msg}"
            )

        # Execute command
        try:
            self._logger.debug(f"Executing command: {self.name}")
            result = self.execute(context)

            if result.success:
                self._logger.info(f"Command {self.name} completed successfully")
            else:
                self._logger.error(f"Command {self.name} failed: {result.message}")

            return result

        except Exception as e:
            self._logger.exception(f"Error executing command {self.name}")
            return CommandResult(
                success=False, message=f"Command execution failed: {str(e)}", error=e
            )


class CompositeCommand(Command):
    """Command that executes multiple sub-commands"""

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self._commands: list[Command] = []

    def add_command(self, command: Command):
        """Add a sub-command

        Args:
            command: Command to add
        """
        self._commands.append(command)

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute all sub-commands in order

        Args:
            context: Command context

        Returns:
            Combined result
        """
        results = []

        for command in self._commands:
            result = command(context)
            results.append(result)

            # Stop on first failure
            if result.failed:
                return CommandResult(
                    success=False,
                    message=f"Sub-command '{command.name}' failed: {result.message}",
                    data={"results": results},
                )

        return CommandResult(
            success=True,
            message=f"All {len(self._commands)} sub-commands completed successfully",
            data={"results": results},
        )
