"""
EdgePulse-Pi5 Source Package
Real-time Health Monitoring System
"""

__version__ = '1.0.0'
__author__ = 'EdgePulse Team'

from .sensors import SensorManager
from .analyzer import VitalSignsAnalyzer
from .alerts import AlertManager
from .data_handler import DataHandler

__all__ = [
    'SensorManager',
    'VitalSignsAnalyzer',
    'AlertManager',
    'DataHandler'
]
