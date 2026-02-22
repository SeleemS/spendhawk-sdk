"""Tests for metrics client."""
import pytest
from unittest.mock import patch, Mock
import requests

from spend_hawk.client import MetricsClient
from spend_hawk.config import config


class TestMetricsClient:
    
    def test_send_async_not_configured(self):
        """Test that metrics are skipped when not configured."""
        client = MetricsClient()
        
        with patch.object(config, 'is_configured', return_value=False):
            client.send_async({"test": "metric"})
            assert client.queue.qsize() == 0
    
    def test_send_async_configured(self):
        """Test that metrics are queued when configured."""
        client = MetricsClient()
        
        with patch.object(config, 'is_configured', return_value=True):
            metric = {"test": "metric"}
            client.send_async(metric)
            assert client.queue.qsize() == 1
    
    @patch('spend_hawk.client.requests.post')
    def test_send_with_retry_success(self, mock_post):
        """Test successful metric send."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        client = MetricsClient()
        metric = {"provider": "openai", "model": "gpt-4"}
        
        with patch.object(config, 'api_key', 'test_key'):
            with patch.object(config, 'api_endpoint', 'https://test.com'):
                client._send_with_retry(metric, max_retries=1)
        
        assert mock_post.called
        assert mock_post.call_count == 1
    
    @patch('spend_hawk.client.requests.post')
    def test_send_with_retry_failure(self, mock_post):
        """Test metric send with retries on failure."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        client = MetricsClient()
        metric = {"provider": "openai", "model": "gpt-4"}
        
        with patch.object(config, 'api_key', 'test_key'):
            with patch.object(config, 'api_endpoint', 'https://test.com'):
                client._send_with_retry(metric, max_retries=2)
        
        assert mock_post.call_count == 2  # Should retry
    
    @patch('spend_hawk.client.requests.post')
    def test_send_with_retry_auth_error_no_retry(self, mock_post):
        """Test that 401 errors don't trigger retries."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        client = MetricsClient()
        metric = {"provider": "openai", "model": "gpt-4"}
        
        with patch.object(config, 'api_key', 'bad_key'):
            with patch.object(config, 'api_endpoint', 'https://test.com'):
                client._send_with_retry(metric, max_retries=3)
        
        assert mock_post.call_count == 1  # Should not retry auth errors
