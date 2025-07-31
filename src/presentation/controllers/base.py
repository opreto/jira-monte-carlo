"""Base controller for presentation layer"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any
import logging

# Type variables for request and response
TRequest = TypeVar('TRequest')
TResponse = TypeVar('TResponse')

logger = logging.getLogger(__name__)


class Controller(ABC, Generic[TRequest, TResponse]):
    """Base controller class for handling presentation logic"""
    
    def __init__(self, name: str):
        """Initialize controller
        
        Args:
            name: Controller name for logging
        """
        self.name = name
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def handle(self, request: TRequest) -> TResponse:
        """Handle the request and return response
        
        Args:
            request: Request model
            
        Returns:
            Response model
        """
        pass
    
    def validate_request(self, request: TRequest) -> None:
        """Validate the request
        
        Args:
            request: Request to validate
            
        Raises:
            ValueError: If request is invalid
        """
        if request is None:
            raise ValueError("Request cannot be None")
    
    def log_request(self, request: TRequest) -> None:
        """Log the incoming request
        
        Args:
            request: Request to log
        """
        self._logger.debug(f"Handling {self.name} request: {request}")
    
    def log_response(self, response: TResponse) -> None:
        """Log the outgoing response
        
        Args:
            response: Response to log
        """
        self._logger.debug(f"{self.name} response: {response}")
    
    def __call__(self, request: TRequest) -> TResponse:
        """Make controller callable
        
        Args:
            request: Request model
            
        Returns:
            Response model
        """
        try:
            self.log_request(request)
            self.validate_request(request)
            response = self.handle(request)
            self.log_response(response)
            return response
        except Exception as e:
            self._logger.exception(f"Error in {self.name} controller")
            raise


class CompositeController(Controller[TRequest, TResponse]):
    """Controller that delegates to multiple sub-controllers"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._controllers = []
    
    def add_controller(self, controller: Controller) -> None:
        """Add a sub-controller
        
        Args:
            controller: Controller to add
        """
        self._controllers.append(controller)
    
    def handle(self, request: TRequest) -> TResponse:
        """Handle request by delegating to sub-controllers
        
        Args:
            request: Request model
            
        Returns:
            Combined response
        """
        # This is a simplified implementation
        # In practice, you'd need to define how to combine responses
        results = []
        for controller in self._controllers:
            result = controller.handle(request)
            results.append(result)
        
        # Return the last result for now
        # Override this method for specific combination logic
        return results[-1] if results else None