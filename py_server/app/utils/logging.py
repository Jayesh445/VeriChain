"""
Logging configuration for VeriChain application.
"""

import sys
from pathlib import Path
from loguru import logger

from app.core.config import settings


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default logger
    logger.remove()
    print("Setting up logging...")
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File logging
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Agent-specific logging
    logger.add(
        "logs/agents.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | AGENT | {extra[agent_role]} | {message}",
        level="INFO",
        filter=lambda record: "agent_role" in record["extra"],
        rotation="5 MB",
        retention="15 days"
    )
    
    # API logging
    logger.add(
        "logs/api.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | API | {extra[endpoint]} | {message}",
        level="INFO",
        filter=lambda record: "endpoint" in record["extra"],
        rotation="5 MB",
        retention="15 days"
    )
    
    logger.info("Logging configuration completed")


def get_agent_logger(agent_role: str):
    """Get a logger instance for a specific agent."""
    return logger.bind(agent_role=agent_role)


def get_api_logger(endpoint: str):
    """Get a logger instance for a specific API endpoint."""
    return logger.bind(endpoint=endpoint)