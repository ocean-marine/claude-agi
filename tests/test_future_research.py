#!/usr/bin/env python3
"""Future Research tool tests

Tests for AI development research functionality.
Testing search and analysis for Claude Code Action, Jules, and Codex evolution.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.future_research import FutureResearchTool, ResearchConfig


class TestResearchConfig:
    """ResearchConfig class test cases"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = ResearchConfig(topics=["Claude Code Action"])
        assert config.topics == ["Claude Code Action"]
        assert config.max_results_per_topic == 5
        assert config.output_format == "text"
    
    def test_empty_topics(self):
        """Test empty topics validation"""
        with pytest.raises(ValueError):
            ResearchConfig(topics=[])
    
    def test_invalid_max_results(self):
        """Test invalid max_results validation"""
        with pytest.raises(ValueError):
            ResearchConfig(topics=["test"], max_results_per_topic=0)
    
    def test_invalid_format(self):
        """Test invalid format validation"""
        with pytest.raises(ValueError):
            ResearchConfig(topics=["test"], output_format="invalid")


class TestFutureResearchTool:
    """FutureResearchTool class test cases"""
    
    @patch('src.future_research.BraveSearchClient')
    def test_init_success(self, mock_client_class):
        """Test successful initialization"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        tool = FutureResearchTool()
        assert tool.search_client == mock_client
        mock_client_class.assert_called_once_with()
    
    @patch('src.future_research.BraveSearchClient')
    def test_research_single_topic(self, mock_client_class):
        """Test research with single topic"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock search results
        mock_results = Mock()
        mock_web_result = Mock()
        mock_web_result.title = "Claude Code Action Future"
        mock_web_result.url = "http://example.com"
        mock_web_result.description = "Analysis of Claude development"
        mock_results.web_results = [mock_web_result]
        
        mock_client.search.return_value = mock_results
        
        tool = FutureResearchTool()
        config = ResearchConfig(topics=["Claude Code Action"])
        
        results = tool.research(config)
        
        assert "Claude Code Action" in results
        assert len(results["Claude Code Action"]) == 1
        assert results["Claude Code Action"][0]["title"] == "Claude Code Action Future"
    
    @patch('src.future_research.BraveSearchClient')
    def test_research_multiple_topics(self, mock_client_class):
        """Test research with multiple topics"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock search results for different calls
        def mock_search_side_effect(config):
            if "Claude" in config.query:
                mock_results = Mock()
                mock_web_result = Mock()
                mock_web_result.title = "Claude Future"
                mock_web_result.url = "http://claude.com"
                mock_web_result.description = "Claude development"
                mock_results.web_results = [mock_web_result]
                return mock_results
            elif "Jules" in config.query:
                mock_results = Mock()
                mock_web_result = Mock()
                mock_web_result.title = "Jules Evolution"
                mock_web_result.url = "http://jules.com"
                mock_web_result.description = "Jules development"
                mock_results.web_results = [mock_web_result]
                return mock_results
            return None
        
        mock_client.search.side_effect = mock_search_side_effect
        
        tool = FutureResearchTool()
        config = ResearchConfig(topics=["Claude Code Action", "Jules"])
        
        results = tool.research(config)
        
        assert "Claude Code Action" in results
        assert "Jules" in results
        assert len(results) == 2
    
    @patch('src.future_research.BraveSearchClient')
    def test_research_no_results(self, mock_client_class):
        """Test research with no results"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = None
        
        tool = FutureResearchTool()
        config = ResearchConfig(topics=["Nonexistent Topic"])
        
        results = tool.research(config)
        
        assert "Nonexistent Topic" in results
        assert results["Nonexistent Topic"] == []
    
    def test_format_results_text(self):
        """Test format results as text"""
        tool = FutureResearchTool()
        results = {
            "Claude Code Action": [
                {
                    "title": "Claude Future",
                    "url": "http://test.com",
                    "description": "Test description"
                }
            ]
        }
        
        formatted = tool.format_results(results, "text")
        
        assert "Claude Code Action" in formatted
        assert "Claude Future" in formatted
        assert "http://test.com" in formatted
        assert "Test description" in formatted
    
    def test_format_results_json(self):
        """Test format results as JSON"""
        tool = FutureResearchTool()
        results = {
            "Claude Code Action": [
                {
                    "title": "Claude Future",
                    "url": "http://test.com",
                    "description": "Test description"
                }
            ]
        }
        
        formatted = tool.format_results(results, "json")
        data = json.loads(formatted)
        
        assert "Claude Code Action" in data
        assert data["Claude Code Action"][0]["title"] == "Claude Future"
        assert data["Claude Code Action"][0]["url"] == "http://test.com"