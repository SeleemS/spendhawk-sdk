"""Tests for Google Generative AI patching."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from spend_hawk.providers.google import patch_google, unpatch_google


@pytest.fixture
def mock_google():
    """Mock Google Generative AI module."""
    with patch('spend_hawk.providers.google.GenerativeModel') as mock_gm:
        mock_generate = Mock()
        mock_gm.generate_content = mock_generate
        yield mock_generate


def test_patch_google():
    """Test patching Google Generative AI."""
    with patch('spend_hawk.providers.google.GenerativeModel') as mock_gm:
        original = Mock()
        mock_gm.generate_content = original
        
        patch_google()
        
        # Check that generate_content was replaced
        assert mock_gm.generate_content != original


def test_patched_google_extracts_metrics():
    """Test that patched Google Generative AI extracts metrics correctly."""
    with patch('spend_hawk.providers.google.GenerativeModel') as mock_gm:
        with patch('spend_hawk.providers.google.send_metric') as mock_send:
            # Setup mock response with usage_metadata
            mock_response = Mock()
            mock_response.usage_metadata = Mock()
            mock_response.usage_metadata.prompt_token_count = 100
            mock_response.usage_metadata.candidates_token_count = 50
            
            original = Mock(return_value=mock_response)
            mock_gm.generate_content = original
            
            # Patch
            patch_google()
            
            # Create a mock self with model_name
            mock_self = Mock()
            mock_self.model_name = "gemini-pro"
            
            # Call patched method
            from spend_hawk.providers.google import _patched_generate_content
            result = _patched_generate_content(mock_self)
            
            # Check that metric was sent
            assert mock_send.called
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs['provider'] == 'google'
            assert call_kwargs['model'] == 'gemini-pro'
            assert call_kwargs['input_tokens'] == 100
            assert call_kwargs['output_tokens'] == 50
            
            # Check that original response is returned
            assert result == mock_response


def test_patched_google_handles_missing_usage_metadata():
    """Test that patched Google handles missing usage_metadata gracefully."""
    with patch('spend_hawk.providers.google.GenerativeModel') as mock_gm:
        with patch('spend_hawk.providers.google.send_metric') as mock_send:
            # Setup mock response without usage_metadata
            mock_response = Mock()
            mock_response.usage_metadata = None
            
            original = Mock(return_value=mock_response)
            mock_gm.generate_content = original
            
            # Patch
            patch_google()
            
            # Create a mock self with model_name
            mock_self = Mock()
            mock_self.model_name = "gemini-pro"
            
            # Call patched method
            from spend_hawk.providers.google import _patched_generate_content
            result = _patched_generate_content(mock_self)
            
            # Check that send_metric was NOT called (no usage_metadata)
            assert not mock_send.called
            
            # Check that original response is still returned
            assert result == mock_response


def test_patched_google_handles_errors():
    """Test that patched Google handles errors gracefully."""
    with patch('spend_hawk.providers.google.GenerativeModel') as mock_gm:
        # Setup mock that raises error
        original = Mock(side_effect=Exception("API Error"))
        mock_gm.generate_content = original
        
        # Patch
        patch_google()
        
        # Call should raise the original error
        mock_self = Mock()
        from spend_hawk.providers.google import _patched_generate_content
        with pytest.raises(Exception, match="API Error"):
            _patched_generate_content(mock_self)


def test_unpatch_google():
    """Test unpatching Google Generative AI."""
    with patch('spend_hawk.providers.google.GenerativeModel') as mock_gm:
        original = Mock()
        mock_gm.generate_content = original
        
        # Patch then unpatch
        patch_google()
        unpatch_google()
        
        # Original should be restored
        assert mock_gm.generate_content == original


def test_google_cost_calculation():
    """Test that Google pricing is correctly configured."""
    from spend_hawk.utils import calculate_cost
    
    # Test gemini-pro pricing
    cost = calculate_cost("google", "gemini-pro", 1000, 1000)
    # 1000 input tokens = 1K tokens = $0.0005
    # 1000 output tokens = 1K tokens = $0.0015
    # Total = $0.002
    assert cost == 0.002
    
    # Test gemini-1.5-pro pricing
    cost = calculate_cost("google", "gemini-1.5-pro", 500, 500)
    # 500 input tokens = 0.5K tokens = $0.5 * 0.00075 = $0.000375
    # 500 output tokens = 0.5K tokens = $0.5 * 0.003 = $0.0015
    # Total = $0.001875
    assert cost == 0.001875
    
    # Test unknown model (should return 0)
    cost = calculate_cost("google", "unknown-model", 1000, 1000)
    assert cost == 0.0


def test_google_integration_with_patch_all():
    """Test that Google is included in patch_all()."""
    from spend_hawk.patch import patch_all, unpatch_all
    
    with patch('spend_hawk.patch.patch_openai'):
        with patch('spend_hawk.patch.patch_anthropic'):
            with patch('spend_hawk.patch.patch_google') as mock_patch_google:
                patch_all()
                assert mock_patch_google.called
    
    with patch('spend_hawk.patch.unpatch_openai'):
        with patch('spend_hawk.patch.unpatch_anthropic'):
            with patch('spend_hawk.patch.unpatch_google') as mock_unpatch_google:
                unpatch_all()
                assert mock_unpatch_google.called
