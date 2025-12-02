"""
Async Inference Manager.

Handles background processing of inference tasks to avoid blocking the main thread.
Implements a debouncing mechanism to group multiple updates into a single inference pass.
"""

import asyncio
import logging
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


class InferenceManager:
    """
    Manages asynchronous inference tasks with debouncing.
    """

    def __init__(self, debounce_seconds: float = 2.0):
        """
        Initialize the inference manager.

        Args:
            debounce_seconds: Time to wait after last trigger before running inference
        """
        self.debounce_seconds = debounce_seconds
        self._queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._callbacks: List[Callable] = []
        self._is_running = False
        self._processing_lock = asyncio.Lock()
        self._idle_event = asyncio.Event()
        self._idle_event.set()  # Initially idle

    def register_callback(self, callback: Callable) -> None:
        """Register a function to be called during inference."""
        self._callbacks.append(callback)

    def trigger_inference(self) -> None:
        """Trigger a background inference pass (debounced)."""
        self._queue.put_nowait(True)
        self._idle_event.clear()  # Not idle anymore

    async def start(self) -> None:
        """Start the background worker."""
        if self._is_running:
            return
        
        self._is_running = True
        self._worker_task = asyncio.create_task(self._worker_loop())
        logger.info("InferenceManager background worker started")

    async def stop(self) -> None:
        """Stop the background worker."""
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("InferenceManager background worker stopped")

    async def _worker_loop(self) -> None:
        """Main worker loop handling debounced inference."""
        while self._is_running:
            try:
                # Wait for a trigger
                await self._queue.get()
                self._queue.task_done()
                self._idle_event.clear() # Ensure we are marked as busy
                
                # Debounce: wait to see if more triggers come in
                while not self._queue.empty():
                    self._queue.get_nowait()
                    self._queue.task_done()
                
                # Wait for debounce period
                await asyncio.sleep(self.debounce_seconds)
                
                # Check again for new items that arrived during sleep
                while not self._queue.empty():
                    self._queue.get_nowait()
                    self._queue.task_done()
                    await asyncio.sleep(self.debounce_seconds)

                # Run inference
                async with self._processing_lock:
                    logger.info("Starting background inference pass...")
                    for callback in self._callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback()
                            else:
                                callback()
                        except Exception as e:
                            logger.error(f"Error in inference callback: {e}", exc_info=True)
                    logger.info("Background inference pass complete")
                
                # Mark as idle if queue is empty
                if self._queue.empty():
                    self._idle_event.set()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in inference worker: {e}", exc_info=True)
                # Ensure we don't get stuck in non-idle state on error
                if self._queue.empty():
                    self._idle_event.set()

    async def wait_until_idle(self, timeout: float = 30.0) -> None:
        """
        Wait until all pending inferences are complete.
        Useful for testing.
        """
        try:
            await asyncio.wait_for(self._idle_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Timed out waiting for inference to settle")

