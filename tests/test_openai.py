"""Tests for OpenAI patching."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from spend_hawk.providers.openai import patch_openai, unpatch_openai


@pytest.fixture
def mock_openai():
    """Mock OpenAI module."""
    with patch('spend_hawk.providers.openai.completions') as mock_completions:
        mock_create = Mock()
        mock_completions.Completions.create = mock_create
        yield mock_create


def test_patch_openai():
    """Test patching OpenAI."""
    with patch('spend_hawk.providers.openai.completions') as mock_completions:
        original = Mock()
        mock_completions.Completions.create = original
        
        patch_openai()
        
        # Check that create was replaced
        assert mock_completions.Completions.create != original


def test_patched_openai_extracts_metrics():
    """Test that patched OpenAI extracts metrics correctly."""
    with patch('spend_hawk.providers.openai.completions') as mock_completions:
        with patch('spend_hawk.providers.openai.send_metric') as mock_send:
            # Setup mock response
            mock_response = Mock()
            mock_response.model = "gpt-4"
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = 100
            mock_response.usage.completion_tokens = 50
            
            original = Mock(return_value=mock_response)
            mock_completions.Completions.create = original
            
            # Patch
            patch_openai()
            
            # Call patched method
            from spend_hawk.providers.openai import _patched_create
            result = _patched_create(None)
            
            # Check that metric was sent
            assert mock_send.called
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs['provider'] == 'openai'
            assert call_kwargs['model'] == 'gpt-4'
            assert call_kwargs['input_tokens'] == 100
            assert call_kwargs['output_tokens'] == 50
            
            # Check that original response is returned
            assert result == mock_response


def test_patched_openai_handles_errors():
    """Test that patched OpenAI handles errors gracefully."""
    with patch('spend_hawk.providers.openai.completions') as mock_completions:
        # Setup mock that raises error
        original = Mock(side_effect=Exception("API Error"))
        mock_completions.Completions.create = original
        
        # Patch
        patch_openai()
        
        # Call should raise the original error
        from spend_hawk.providers.openai import _patched_create
        with pytest.raises(Exception, match="API Error"):
            _patched_create(None)
