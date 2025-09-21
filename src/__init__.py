"""
AI ToolBox - Main Package
Modern PyQt5 AI araçları koleksiyonu
"""

__version__ = "1.0.0"
__author__ = "AI ToolBox"
__description__ = "AI ToolBox - Modern AI Tools Collection"

from .ui import MainWindow
from .core import VideoProcessor, VideoAnalyzer  
from .utils import app_logger

__all__ = [
    'MainWindow',
    'VideoProcessor',
    'VideoAnalyzer',
    'app_logger'
]
