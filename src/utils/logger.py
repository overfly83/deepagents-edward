import logging
import os

class CustomLogger(logging.Logger):
    """
    Custom Logger subclass that extends standard logging methods to accept a source parameter.
    """
    def debug(self, msg, *args, source=None, **kwargs):
        """Log a debug message with optional source parameter."""
        if source or hasattr(self, 'source'):
            extra = kwargs.pop('extra', {})
            extra['source'] = source or self.source
            kwargs['extra'] = extra
        super().debug(msg, *args, **kwargs)

    def info(self, msg, *args, source=None, **kwargs):
        """Log an info message with optional source parameter."""
        if source or hasattr(self, 'source'):
            extra = kwargs.pop('extra', {})
            extra['source'] = source or self.source
            kwargs['extra'] = extra
        super().info(msg, *args, **kwargs)

    def warning(self, msg, *args, source=None, **kwargs):
        """Log a warning message with optional source parameter."""
        if source or hasattr(self, 'source'):
            extra = kwargs.pop('extra', {})
            extra['source'] = source or self.source
            kwargs['extra'] = extra
        super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, source=None, **kwargs):
        """Log an error message with optional source parameter."""
        if source or hasattr(self, 'source'):
            extra = kwargs.pop('extra', {})
            extra['source'] = source or self.source
            kwargs['extra'] = extra
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, source=None, **kwargs):
        """Log a critical message with optional source parameter."""
        if source or hasattr(self, 'source'):
            extra = kwargs.pop('extra', {})
            extra['source'] = source or self.source
            kwargs['extra'] = extra
        super().critical(msg, *args, **kwargs)

class ColoredLogFormatter(logging.Formatter):
    """
    Custom formatter for logging that colors different log levels:
    - debug: blue
    - info: normal (no color)
    - warning: yellow
    - error: red
    - critical: orange-red
    """
    # ANSI color codes
    BLUE = '\033[94m'
    GREY = '\033[38;5;240m'  # ANSI 8-bit color for grey
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ORANGE_RED = '\033[38;5;208m'  # ANSI 8-bit color for lighter orange-red
    RESET = '\033[0m'
    
    def format(self, record):
        """
        Format the log record with appropriate colors for different log levels.
        """
        # Get the source from the record or from the logger itself
        source = getattr(record, 'source', '')
        if not source and hasattr(record, 'name'):
            logger = logging.getLogger(record.name)
            source = getattr(logger, 'source', '')
        
        source_prefix = f"[{source}] " if source else ""
        
        # Apply color based on log level
        if record.levelno == logging.DEBUG:
            record.msg = f"{self.BLUE}{source_prefix}{record.msg}{self.RESET}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{self.YELLOW}{source_prefix}{record.msg}{self.RESET}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{self.RED}{source_prefix}{record.msg}{self.RESET}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{self.ORANGE_RED}{source_prefix}{record.msg}{self.RESET}"
        elif record.levelno == logging.INFO:
            record.msg = f"{self.GREY}{source_prefix}{record.msg}{self.RESET}"
        else:  # Other levels
            record.msg = f"{source_prefix}{record.msg}"
            
        return super().format(record)

def get_logger(name: str, level: int = None, source: str = None) -> logging.Logger:
    """
    Get a logger with colored formatting for different log levels.
    
    Args:
        name: The name of the logger
        level: Optional logging level (default: DEBUG if DEBUG environment variable is '1', otherwise INFO)
        source: Optional custom source identifier that appears at the beginning of log messages
        
    Returns:
        A configured logger instance
    """
    # Check if the logger class has been set to our custom logger
    if logging.getLoggerClass() != CustomLogger:
        logging.setLoggerClass(CustomLogger)
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Ensure the logger is an instance of CustomLogger
    if not isinstance(logger, CustomLogger):
        # Create a new CustomLogger instance and copy handlers
        new_logger = CustomLogger(name)
        new_logger.level = logger.level
        for handler in logger.handlers:
            new_logger.addHandler(handler)
        new_logger.propagate = logger.propagate
        logger = new_logger
    
    # Set logging level
    if level is None:
        level = logging.DEBUG if os.environ.get('DEBUG') == '1' else logging.INFO
    
    logger.setLevel(level)
    
    # Check if logger already has handlers to avoid duplicate logs
    if not logger.handlers:
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        
        # Create formatter with color
        formatter = ColoredLogFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(ch)
    
    # If source is provided, store it in the logger
    if source:
        logger.source = source
    
    return logger

def log_with_source(logger: logging.Logger, level: int, msg: str, *args, source: str = None, **kwargs):
    """
    Log a message with a custom source that appears at the beginning of the log message.
    
    Args:
        logger: The logger instance to use
        level: The log level (logging.DEBUG, logging.INFO, etc.)
        msg: The log message
        source: Optional custom source identifier (overrides the logger's default source if provided)
        *args: Additional positional arguments for the log message
        **kwargs: Additional keyword arguments for the log message
    """
    # Create a log record with the source
    if source or hasattr(logger, 'source'):
        extra = {'source': source or logger.source}
        kwargs['extra'] = extra
    
    logger.log(level, msg, *args, **kwargs)

def get_colored_formatter() -> ColoredLogFormatter:
    """
    Get the colored log formatter instance.
    
    Returns:
        ColoredLogFormatter instance
    """
    return ColoredLogFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')