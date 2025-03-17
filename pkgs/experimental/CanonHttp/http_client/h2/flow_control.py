"""
h2/flow_control.py

Provides a basic implementation of HTTP/2 flow control management.
This module manages both connection-level and stream-level flow control windows.
Note: This is a simplified version and does not cover the full complexity of HTTP/2 flow control.
"""

import asyncio

# Default window sizes as per HTTP/2 specification.
DEFAULT_INITIAL_STREAM_WINDOW = 65535
DEFAULT_INITIAL_CONNECTION_WINDOW = 65535

class FlowControlManager:
    def __init__(self, initial_stream_window=DEFAULT_INITIAL_STREAM_WINDOW,
                 initial_connection_window=DEFAULT_INITIAL_CONNECTION_WINDOW):
        """
        Initialize the flow control manager.
        
        :param initial_stream_window: Default window size for new streams.
        :param initial_connection_window: Initial window size for the connection.
        """
        self.connection_window = initial_connection_window
        self.stream_windows = {}  # stream_id -> window size
        
        # Condition variable to allow waiting for window updates.
        self._condition = asyncio.Condition()

    def add_stream(self, stream_id, window_size=None):
        """
        Register a new stream with an initial window size.
        
        :param stream_id: The ID of the stream.
        :param window_size: Optional override of the default stream window size.
        """
        if window_size is None:
            window_size = DEFAULT_INITIAL_STREAM_WINDOW
        self.stream_windows[stream_id] = window_size

    def remove_stream(self, stream_id):
        """
        Remove a stream from flow control tracking.
        
        :param stream_id: The ID of the stream to remove.
        """
        if stream_id in self.stream_windows:
            del self.stream_windows[stream_id]

    async def wait_for_window(self, stream_id, data_length):
        """
        Wait until both the connection-level and stream-level windows are large enough
        to accommodate data_length bytes.
        
        :param stream_id: The stream ID to check.
        :param data_length: Number of bytes to be sent.
        """
        async with self._condition:
            while self.connection_window < data_length or self.stream_windows.get(stream_id, 0) < data_length:
                await self._condition.wait()

    def consume_window(self, stream_id, data_length):
        """
        Deduct data_length bytes from both the connection and stream windows.
        
        :param stream_id: The stream ID from which to consume window.
        :param data_length: Number of bytes to deduct.
        :raises ValueError: if there is insufficient window available.
        """
        if self.connection_window < data_length:
            raise ValueError("Insufficient connection window available")
        if self.stream_windows.get(stream_id, 0) < data_length:
            raise ValueError(f"Insufficient window available on stream {stream_id}")
        
        self.connection_window -= data_length
        self.stream_windows[stream_id] -= data_length

    def update_window(self, stream_id, increment):
        """
        Increase the available window size. If stream_id is 0, update the connection-level window;
        otherwise, update the specified stream's window.
        
        :param stream_id: 0 for connection-level, or a stream ID for stream-level update.
        :param increment: Number of bytes to add to the window.
        """
        if stream_id == 0:
            self.connection_window += increment
        else:
            if stream_id in self.stream_windows:
                self.stream_windows[stream_id] += increment
            else:
                # Optionally, register the stream if it wasn't added.
                self.stream_windows[stream_id] = increment

        # Notify any waiters that the window has been updated.
        asyncio.create_task(self._notify())

    async def _notify(self):
        async with self._condition:
            self._condition.notify_all()

# Example usage (for testing purposes only):
if __name__ == "__main__":
    async def test_flow_control():
        fc = FlowControlManager()
        fc.add_stream(1)
        print("Initial connection window:", fc.connection_window)
        print("Initial stream window (stream 1):", fc.stream_windows[1])
        
        # Simulate sending 1000 bytes.
        await fc.wait_for_window(1, 1000)
        fc.consume_window(1, 1000)
        print("After sending 1000 bytes:")
        print("Connection window:", fc.connection_window)
        print("Stream window (stream 1):", fc.stream_windows[1])
        
        # Update the windows with a WINDOW_UPDATE frame equivalent.
        fc.update_window(1, 5000)
        fc.update_window(0, 5000)
        await asyncio.sleep(0.1)  # Allow _notify to complete.
        print("After window update:")
        print("Connection window:", fc.connection_window)
        print("Stream window (stream 1):", fc.stream_windows[1])
    
    asyncio.run(test_flow_control())
