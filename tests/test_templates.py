"""
Template Rendering Tests
Tests error handling for template loading and processing
"""

import pytest
from unittest.mock import patch
from jinja2 import TemplateNotFound, TemplateError


# -------------------------
# Template Error Handling
# -------------------------


def test_template_not_found(client):
    """Test handling when index.html template is missing"""
    with patch("app.app.render_template") as mock_render:
        mock_render.side_effect = TemplateNotFound("index.html")

        response = client.get("/")

        assert response.status_code == 404


def test_template_processing_error(client):
    """Test handling when template has syntax or rendering errors"""
    with patch("app.app.render_template") as mock_render:
        mock_render.side_effect = TemplateError("Unexpected tag in template")

        response = client.get("/")

        assert response.status_code == 500
