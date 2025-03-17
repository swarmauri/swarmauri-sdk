"""
h2/multiplex.py

Provides a simple HTTP/2 multiplexer that manages concurrent streams over a single connection.
"""

import asyncio
from .frames import HTTP2Frame

class HTTP2Multiplexer:
    """
    Manages multiple HTTP/2 streams on a single connection.
    
    - Maintains a mapping of stream IDs to asyncio.Queue objects.
    - Provides methods to create new streams and send/receive frames.
    """
    def __init__(self, reader, writer):
        """
        Initialize the multiplexer with an existing asyncio StreamReader and StreamWriter.
        
        :param reader: asyncio.StreamReader for the connection.
        :param writer: asyncio.StreamWriter for the connection.
        """
        self.reader = reader
        self.writer = writer
        self.next_stream_id = 1  # Client-initiated streams use odd numbers.
        self.streams = {}  # Mapping of stream_id to asyncio.Queue for incoming frames.
        self._receive_task = None

    async def start_receiving(self):
        """
        Start the background task to continuously receive and dispatch frames.
        """
        self._receive_task = asyncio.create_task(self._receive_frames())

    async def stop_receiving(self):
        """
        Cancel the background task for receiving frames.
        """
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

    async def _receive_frames(self):
        """
        Continuously receive frames from the connection and dispatch them to the appropriate stream queues.
        """
        buffer = b""
        while not self.reader.at_eof():
            chunk = await self.reader.read(4096)
            if not chunk:
                break
            buffer += chunk
            # Process all complete frames in the buffer.
            while len(buffer) >= HTTP2Frame.HEADER_LENGTH:
                try:
                    frame, buffer = HTTP2Frame.unpack(buffer)
                except ValueError:
                    # Incomplete frame data; wait for more.
                    break
                # Dispatch the frame.
                if frame.stream_id in self.streams:
                    await self.streams[frame.stream_id].put(frame)
                else:
                    # Handle connection-level frames (e.g., SETTINGS, PING, etc.).
                    self.handle_connection_frame(frame)

    def handle_connection_frame(self, frame):
        """
        Handle frames that are not associated with a specific stream.
        
        :param frame: The HTTP2Frame instance.
        """
        # For now, we simply log the frame.
        print(f"Received connection-level frame: {frame}")

    def create_stream(self):
        """
        Create a new stream and return its stream ID.
        
        :return: The new stream ID.
        """
        stream_id = self.next_stream_id
        self.next_stream_id += 2  # Increment by 2 (client-initiated streams must be odd).
        self.streams[stream_id] = asyncio.Queue()
        return stream_id

    async def send_frame(self, frame):
        """
        Send a single HTTP/2 frame over the connection.
        
        :param frame: The HTTP2Frame instance to send.
        """
        self.writer.write(frame.pack())
        await self.writer.drain()

    async def send_request(self, headers, data=b''):
        """
        Send a simple HTTP/2 request:
          - Create a new stream.
          - Send a HEADERS frame (optionally followed by a DATA frame if data is provided).
        
        :param headers: Dictionary of header fields.
        :param data: Optional bytes payload.
        :return: The stream ID used for the request.
        """
        # Create a new stream.
        stream_id = self.create_stream()
        
        # Convert headers to a header block using HPACK (or a stub implementation).
        # Here you might call: header_block = hpack_encode(headers)
        # For simplicity, we'll assume headers are already a bytes object.
        header_block = b"".join(f"{k}:{v}\n".encode("utf-8") for k, v in headers.items())
        
        # Create and send a HEADERS frame.
        headers_frame = HTTP2Frame(frame_type=0x1, flags=0x4, stream_id=stream_id, payload=header_block)
        await self.send_frame(headers_frame)
        
        if data:
            # Create and send a DATA frame with the END_STREAM flag.
            data_frame = HTTP2Frame(frame_type=0x0, flags=0x1, stream_id=stream_id, payload=data)
            await self.send_frame(data_frame)
        
        return stream_id

    async def get_response(self, stream_id, timeout=None):
        """
        Wait for and return the next frame on the given stream.
        
        :param stream_id: The stream ID to receive frames from.
        :param timeout: Optional timeout in seconds.
        :return: An HTTP2Frame instance.
        """
        if stream_id not in self.streams:
            raise ValueError(f"Stream {stream_id} does not exist")
        return await asyncio.wait_for(self.streams[stream_id].get(), timeout=timeout)

