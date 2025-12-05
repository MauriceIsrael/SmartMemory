import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from smart_memory.inference.inference_manager import InferenceManager

@pytest.mark.asyncio
async def test_inference_manager_debouncing():
    """Test that inference is debounced."""
    # Short debounce for testing
    manager = InferenceManager(debounce_seconds=0.1)
    callback = AsyncMock()
    manager.register_callback(callback)
    
    await manager.start()
    
    # Trigger multiple times quickly
    manager.trigger_inference()
    manager.trigger_inference()
    manager.trigger_inference()
    
    # Wait for processing
    await manager.wait_until_idle(timeout=1.0)
    
    # Should have run only once
    assert callback.call_count == 1
    
    await manager.stop()

@pytest.mark.asyncio
async def test_inference_manager_callbacks():
    """Test that both async and sync callbacks are executed."""
    manager = InferenceManager(debounce_seconds=0.01)
    
    async_cb = AsyncMock()
    sync_cb = Mock()
    
    manager.register_callback(async_cb)
    manager.register_callback(sync_cb)
    
    await manager.start()
    manager.trigger_inference()
    
    await manager.wait_until_idle(timeout=1.0)
    
    assert async_cb.call_count == 1
    assert sync_cb.call_count == 1
    
    await manager.stop()

@pytest.mark.asyncio
async def test_inference_manager_wait_until_idle():
    """Test wait_until_idle logic."""
    manager = InferenceManager(debounce_seconds=0.1)
    await manager.start()
    
    # Initially idle
    await asyncio.wait_for(manager.wait_until_idle(), timeout=0.1)
    
    # Trigger
    manager.trigger_inference()
    
    # Should block while processing (we can't easily test blocking without a slow callback)
    # But we can test that it returns eventually
    await asyncio.wait_for(manager.wait_until_idle(), timeout=1.0)
    
    await manager.stop()
