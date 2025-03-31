"""
h2/frames.py

Provides classes and functions for packing and unpacking HTTP/2 frames.
"""

# Constants for common HTTP/2 frame types.
DATA = 0x0
HEADERS = 0x1
PRIORITY = 0x2
RST_STREAM = 0x3
SETTINGS = 0x4
PUSH_PROMISE = 0x5
PING = 0x6
GOAWAY = 0x7
WINDOW_UPDATE = 0x8
CONTINUATION = 0x9

class HTTP2Frame:
    """
    Represents an HTTP/2 frame.

    An HTTP/2 frame consists of a 9-byte header followed by a variable-length payload.
    The header format is:
      - Length: 24 bits (3 bytes, big-endian) specifying the length of the payload.
      - Type: 8 bits (1 byte) indicating the frame type.
      - Flags: 8 bits (1 byte) for frame-specific flags.
      - R + Stream Identifier: 1 reserved bit and 31 bits (4 bytes, big-endian) for the stream ID.
    """
    HEADER_LENGTH = 9

    def __init__(self, frame_type, flags, stream_id, payload=b''):
        """
        Initialize a new HTTP/2 frame.

        :param frame_type: Integer (0-255) representing the frame type.
        :param flags: Integer (0-255) representing frame-specific flags.
        :param stream_id: Integer for the stream identifier (only the lower 31 bits are used).
        :param payload: Bytes payload of the frame.
        """
        self.frame_type = frame_type
        self.flags = flags
        self.stream_id = stream_id & 0x7fffffff  # Ensure only 31 bits are used.
        self.payload = payload

    def pack(self):
        """
        Pack the frame into its binary representation.

        :return: A bytes object containing the 9-byte header followed by the payload.
        """
        length = len(self.payload)
        header = (
            length.to_bytes(3, 'big') +
            self.frame_type.to_bytes(1, 'big') +
            self.flags.to_bytes(1, 'big') +
            (self.stream_id & 0x7fffffff).to_bytes(4, 'big')
        )
        return header + self.payload

    @classmethod
    def unpack(cls, data):
        """
        Unpack a single HTTP/2 frame from the given data.

        :param data: Bytes containing at least one complete frame.
        :return: A tuple (frame, remaining_bytes), where 'frame' is an HTTP2Frame instance
                 and 'remaining_bytes' contains any extra data after this frame.
        :raises ValueError: If there is insufficient data for a complete frame.
        """
        if len(data) < cls.HEADER_LENGTH:
            raise ValueError("Insufficient data for HTTP/2 frame header")
        
        # Parse the 9-byte header.
        length = int.from_bytes(data[0:3], 'big')
        frame_type = data[3]
        flags = data[4]
        stream_id = int.from_bytes(data[5:9], 'big') & 0x7fffffff

        total_length = cls.HEADER_LENGTH + length
        if len(data) < total_length:
            raise ValueError("Incomplete frame payload")
        
        payload = data[9:total_length]
        frame = cls(frame_type, flags, stream_id, payload)
        remaining = data[total_length:]
        return frame, remaining

    def __repr__(self):
        return (f"<HTTP2Frame type={self.frame_type} flags={self.flags} "
                f"stream_id={self.stream_id} payload_length={len(self.payload)}>")
