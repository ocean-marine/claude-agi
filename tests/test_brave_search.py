#!/usr/bin/env python3
"""Brave Search tool tests

Critical tests for BraveSearchClient functionality.
Focused on essential functionality with minimal test coverage.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.brave_search import BraveSearchClient, SearchConfig


class TestSearchConfig:
    """SearchConfig class test cases"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = SearchConfig(query="test query")
        assert config.query == "test query"
        assert config.count == 10
        assert config.output_format == "text"
    
    def test_invalid_count(self):
        """Test invalid count validation"""
        with pytest.raises(ValueError):
            SearchConfig(query="test", count=0)
    
    def test_invalid_format(self):
        """Test invalid format validation"""
        with pytest.raises(ValueError):
            SearchConfig(query="test", output_format="invalid")


class TestBraveSearchClient:
    """BraveSearchClient class test cases"""
    
    def test_init_no_api_key(self):
        """Test initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                BraveSearchClient()
    
    @patch('src.brave_search.Brave')
    def test_init_with_api_key(self, mock_brave):
        """Test initialization with API key"""
        client = BraveSearchClient(api_key="test_key")
        assert client._api_key == "test_key"
        mock_brave.assert_called_once()
    
    @patch('src.brave_search.Brave')
    def test_search_empty_query(self, mock_brave):
        """Test search with empty query"""
        client = BraveSearchClient(api_key="test_key")
        config = SearchConfig(query="")
        
        with pytest.raises(ValueError):
            client.search(config)
    
    @patch('src.brave_search.Brave')
    def test_search_success(self, mock_brave):
        """Test successful search"""
        mock_instance = Mock()
        mock_brave.return_value = mock_instance
        mock_result = Mock()
        mock_instance.search.return_value = mock_result
        
        client = BraveSearchClient(api_key="test_key")
        config = SearchConfig(query="test query")
        
        result = client.search(config)
        assert result == mock_result
        mock_instance.search.assert_called_once_with(q="test query", count=10)
    
    def test_format_results_no_results(self):
        """Test format results with no results"""
        client = BraveSearchClient(api_key="test_key")
        result = client.format_results(None)
        assert "No search results found" in result
    
    def test_format_results_text(self):
        """Test format results as text"""
        mock_results = Mock()
        mock_web_result = Mock()
        mock_web_result.title = "Test Title"
        mock_web_result.url = "http://test.com"
        mock_web_result.description = "Test description"
        mock_results.web_results = [mock_web_result]
        
        client = BraveSearchClient(api_key="test_key")
        result = client.format_results(mock_results, "text")
        
        assert "Test Title" in result
        assert "http://test.com" in result
        assert "Test description" in result
    
    def test_format_results_json(self):
        """Test format results as JSON"""
        mock_results = Mock()
        mock_web_result = Mock()
        mock_web_result.title = "Test Title"
        mock_web_result.url = "http://test.com"
        mock_web_result.description = "Test description"
        mock_results.web_results = [mock_web_result]
        
        client = BraveSearchClient(api_key="test_key")
        result = client.format_results(mock_results, "json")
        
        data = json.loads(result)
        assert data["results"][0]["title"] == "Test Title"
        assert data["results"][0]["url"] == "http://test.com"
        assert data["results"][0]["description"] == "Test description"