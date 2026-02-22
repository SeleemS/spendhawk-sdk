"""Context management for dynamic tagging."""
from contextvars import ContextVar
from typing import Optional, Dict, Any
from contextlib import contextmanager


# Context variables for thread-safe and async-safe storage
_project_id_var: ContextVar[Optional[str]] = ContextVar('project_id', default=None)
_agent_var: ContextVar[Optional[str]] = ContextVar('agent', default=None)
_custom_tags_var: ContextVar[Dict[str, Any]] = ContextVar('custom_tags', default={})


def set_context(
    project_id: Optional[str] = None,
    agent: Optional[str] = None,
    **custom_tags
) -> None:
    """
    Set context for Spend Hawk tracking.
    
    Args:
        project_id: Project identifier
        agent: Agent identifier
        **custom_tags: Additional custom tags
    """
    if project_id is not None:
        _project_id_var.set(project_id)
    if agent is not None:
        _agent_var.set(agent)
    if custom_tags:
        current = _custom_tags_var.get()
        updated = {**current, **custom_tags}
        _custom_tags_var.set(updated)


def get_context() -> Dict[str, Any]:
    """
    Get current context.
    
    Returns:
        Dictionary with project_id, agent, and custom tags
    """
    return {
        'project_id': _project_id_var.get(),
        'agent': _agent_var.get(),
        **_custom_tags_var.get()
    }


@contextmanager
def context(**kwargs):
    """
    Context manager for temporary context setting.
    
    Usage:
        with context(project_id="mint", agent="vance"):
            # API calls here will use this context
            pass
    """
    # Save current values
    old_project = _project_id_var.get()
    old_agent = _agent_var.get()
    old_tags = _custom_tags_var.get()
    
    # Set new values
    set_context(**kwargs)
    
    try:
        yield
    finally:
        # Restore old values
        _project_id_var.set(old_project)
        _agent_var.set(old_agent)
        _custom_tags_var.set(old_tags)
