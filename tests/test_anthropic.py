"""Tests for Anthropic patching."""
import pytest
from unittest.mock import Mock, patch

from spend_hawk.providers.anthropic import patch_anthropic, unpatch_anthropic


def test_patch_anthropic():
    """Test patching Anthropic."""
    with patch('spend_hawk.providers.anthropic.Messages') as mock_messages:
        original = Mock()
        mock_messages.create = original
        
        patch_anthropic()
        
        # Check that create was replaced
        assert mock_messages.create != original


def test_patched_anthropic_extracts_metrics():
    """Test that patched Anthropic extracts metrics correctly."""
    with patch('spend_hawk.providers.anthropic.Messages') as mock_messages:
        with patch('spend_hawk.providers.anthropic.send_metric') as mock_send:
            # Setup mock response
            mock_response = Mock()
            mock_response.model = "claude-3-sonnet-20240229"
            mock_response.usage = Mock()
            mock_response.usage.input_tokens = 100
            mock_response.usage.output_tokens = 50
            
            original = Mock(return_value=mock_response)
            mock_messages.create = original
            
            # Patch
            patch_anthropic()
            
            # Call patched method
            from spend_hawk.providers.anthropic import _patched_create
            result = _patched_create(None)
            
            # Check that metric was sent
            assert mock_send.called
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs['provider'] == 'anthropic'
            assert call_kwargs['model'] == 'claude-3-sonnet-20240229'
            assert call_kwargs['input_tokens'] == 100
            assert call_kwargs['output_tokens'] == 50
            
            # Check that original response is returned
            assert result == mock_response


def test_patched_anthropic_handles_errors():
    """Test that patched Anthropic handles errors gracefully."""
    with patch('spend_hawk.providers.anthropic.Messages') as mock_messages:
        # Setup mock that raises error
        original = Mock(side_effect=Exception("API Error"))
        mock_messages.create = original
        
        # Patch
        patch_anthropic()
        
        # Call should raise the original error
        from spend_hawk.providers.anthropic import _patched_create
        with pytest.raises(Exception, match="API Error"):
            _patched_create(None)
