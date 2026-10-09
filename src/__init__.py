"""
src package initialization for Smart Campus Analytics.
"""

from src.config import CATEGORY_WEIGHTS, SEGMENT_THRESHOLDS
from src.data_loader import DataLoader
from src.integrator import DataIntegrator
from src.scoring import StudentSuccessScorer
from src.risk_analyzer import RiskAnalyzer
from src.segmentation import StudentSegmenter
from src.recommendations import RecommendationEngine
from src.service import AnalyticsService

__all__ = [
    "CATEGORY_WEIGHTS",
    "SEGMENT_THRESHOLDS",
    "DataLoader",
    "DataIntegrator",
    "StudentSuccessScorer",
    "RiskAnalyzer",
    "StudentSegmenter",
    "RecommendationEngine",
    "AnalyticsService",
]
