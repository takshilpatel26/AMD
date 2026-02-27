"""
ML Service for FastAPI Gateway - Uses trained models from ML directory
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import from ML folder
current_dir = Path(__file__).resolve().parent
# ML folder is located at <workspace>/SH/ML — two levels up from backend/ml_gateway
# current_dir -> backend/ml_gateway, current_dir.parent -> backend, current_dir.parent.parent -> SH
ml_dir = current_dir.parent.parent / 'ML'
sys.path.insert(0, str(ml_dir))

try:
    from analytics_engine import GramBrain
    ML_MODELS_AVAILABLE = True
except ImportError:
    ML_MODELS_AVAILABLE = False
    print("Warning: Could not import GramBrain from ML directory")

# Global ML service instance
_gram_brain = None

def get_gram_brain():
    """Get singleton instance of GramBrain"""
    global _gram_brain
    if _gram_brain is None and ML_MODELS_AVAILABLE:
        _gram_brain = GramBrain()
    return _gram_brain
