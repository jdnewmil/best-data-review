
"""Commandline start of shiny app in package."""

import shiny
from best_data_review.shiny_app.app import best_app


def run_best_shiny_app():
    """Run shiny app."""
    shiny.run_app(
        app=best_app()
        , host='localhost'
        , port=5000
        , launch_browser=True)
