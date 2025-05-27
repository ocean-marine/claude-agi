#!/usr/bin/env python3
"""Brave Search API basic tests

Basic API functionality tests for environment setup validation.
Essential connectivity and configuration testing only.
"""
from __future__ import annotations

import os
import pytest


class TestBraveAPISetup:
    """Basic API setup tests"""
    
    def test_api_key_environment(self):
        """Test API key environment variable availability"""
        # This test will be skipped if no API key is set
        api_key = os.getenv('BRAVE_API_KEY')
        if not api_key:
            pytest.skip("BRAVE_API_KEY environment variable not set")
        
        assert len(api_key) > 0, "API key should not be empty"
    
    @pytest.mark.skipif(not os.getenv('BRAVE_API_KEY'), reason="No API key available")
    def test_brave_import(self):
        """Test brave library import"""
        try:
            from brave import Brave
            brave_client = Brave()
            assert brave_client is not None
        except ImportError:
            pytest.fail("brave-search library not available")
        except Exception as e:
            pytest.fail(f"Failed to initialize Brave client: {e}")