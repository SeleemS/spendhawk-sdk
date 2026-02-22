"""Tests for context management."""
import pytest
from spend_hawk.context import set_context, get_context, context


def test_set_and_get_context():
    """Test setting and getting context."""
    set_context(project_id="test_project", agent="test_agent")
    
    ctx = get_context()
    assert ctx['project_id'] == "test_project"
    assert ctx['agent'] == "test_agent"


def test_context_manager():
    """Test context manager."""
    # Set initial context
    set_context(project_id="initial")
    
    # Use context manager
    with context(project_id="temporary", agent="temp_agent"):
        ctx = get_context()
        assert ctx['project_id'] == "temporary"
        assert ctx['agent'] == "temp_agent"
    
    # Context should be restored
    ctx = get_context()
    assert ctx['project_id'] == "initial"


def test_custom_tags():
    """Test custom tags in context."""
    set_context(project_id="test", custom_field="custom_value")
    
    ctx = get_context()
    assert ctx['project_id'] == "test"
    assert ctx['custom_field'] == "custom_value"


def test_thread_safety():
    """Test that context is thread-safe using contextvars."""
    import threading
    
    results = {}
    
    def worker(thread_id):
        set_context(project_id=f"project_{thread_id}")
        import time
        time.sleep(0.01)  # Simulate work
        ctx = get_context()
        results[thread_id] = ctx['project_id']
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    # Each thread should have its own context
    for i in range(5):
        assert results[i] == f"project_{i}"
