import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Vercel entry point
from assessment_engine.api import app

# Vercel requires the app to be named 'app'
# which it already is
