"""
Centralized logging configuration for GameCock AI processors.
"""
import logging
import os
from datetime import datetime
from typing import Optional

class ProcessingLogger:
    _instance = None
    
    def __new__(cls, log_dir: str = None):
        if cls._instance is None:
            cls._instance = super(ProcessingLogger, cls).__new__(cls)
            cls._instance._initialized = False
            # Use absolute path for logs directory
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            cls._instance.log_dir = os.path.abspath(log_dir) if log_dir else os.path.join(base_dir, 'logs')
        return cls._instance
    
    def __init__(self, log_dir: str = None):
        if self._initialized:
            return
            
        self.log_dir = log_dir or self.log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a timestamped log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(self.log_dir, f'processing_{timestamp}.log')
        
        # Configure root logger if not already configured
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(level=logging.INFO)
        
        # Create our own logger
        self.logger = logging.getLogger('gamecock_processor')
        self.logger.setLevel(logging.INFO)
        
        # Remove any existing handlers to avoid duplicate logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        
        # Console handler (only show errors by default)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent the logger from propagating to the root logger
        self.logger.propagate = False
        
        self._initialized = True

def get_processor_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance for a processor module.
    
    Args:
        name: Name of the processor module (e.g., 'cftc_swaps')
        
    Returns:
        Configured logger instance
    """
    if name:
        return logging.getLogger(f'gamecock_processor.{name}')
    return logging.getLogger('gamecock_processor')
