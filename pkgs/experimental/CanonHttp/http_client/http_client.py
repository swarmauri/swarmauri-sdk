import http.client
import urllib.parse
import json
import asyncio
import ssl

from .exceptions import TimeoutError, HTTP2Error, HttpClientError
from .utils import merge_headers, to_bytes, to_str

# Import HTTP/2 components from our subpackage.
from .h2 import frames, hpack, multiplex, flow_control

# A helper to send the HTTP/2 connection preface.
async def send_connection_preface(writer):
    """
    Sends the HTTP/2 connection preface as specified:
    "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
    """
    preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
    writer.write(preface)
    await writer.drain()

class HttpClient:
    def __init__(self, base_url=None, timeout=None, version="1.1"):
        """
        :param base_url: Optional base URL for all requests.
        :param timeout: Timeout (in seconds) for connections and operations.
        :param version: HTTP version to use. Accepts "1.1" (default) or "2".
                        For "2", the client configures ALPN negotiation for HTTP/2.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.version = version

    def _prepare_url(self, url, params):
        """
        Combine the base URL (if provided) with the endpoint and attach query parameters.
        """
        if self.base_url:
            url = urllib.parse.urljoin(self.base_url, url)
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path or "/"
        if params:
            query = urllib.parse.urlencode(params)
            path = f"{path}?{query}"
        return parsed_url, path

    def sync_request(self, method, url, headers=None, params=None, data=None, json_data=None):
        """
        Synchronous HTTP request.
        :returns: A tuple (status, headers, body)
        """
        parsed_url, path = self._prepare_url(url, params)
        method = method.upper()
        headers = headers or {}

        # Process JSON payload.
        if json_data is not None:
            data = json.dumps(json_data)
            headers['Content-Type'] = 'application/json'

        if self.version == "1.1":
            # Use built-in http.client for HTTP/1.1.
            if parsed_url.scheme == "https":
                conn = http.client.HTTPSConnection(parsed_url.netloc, timeout=self.timeout)
            else:
                conn = http.client.HTTPConnection(parsed_url.netloc, timeout=self.timeout)
            conn.request(method, path, body=data, headers=headers)
            response = conn.getresponse()
            body_response = response.read()
            headers_response = response.getheaders()
            conn.close()
            return response.status, headers_response, body_response

        elif self.version == "2":
            # For HTTP/2, run the async version in a blocking manner.
            return asyncio.run(self._handle_http2_async_request(method, parsed_url, path, headers, data))
        else:
            raise HttpClientError(f"Unsupported HTTP version: {self.version}")

    async def async_request(self, method, url, headers=None, params=None, data=None, json_data=None):
        """
        Asynchronous HTTP request.
        :returns: Raw response data as a string.
        """
        parsed_url, path = self._prepare_url(url, params)
        method = method.upper()
        headers = headers or {}

        # Process JSON payload.
        if json_data is not None:
            data = json.dumps(json_data)
            headers['Content-Type'] = 'application/json'

        if self.version == "1.1":
            # Build a raw HTTP/1.1 request.
            host = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
            ssl_context = None
            if parsed_url.scheme == "https":
                ssl_context = ssl.create_default_context()

            request_lines = [f"{method} {path} HTTP/1.1", f"Host: {host}"]
            for key, value in headers.items():
                request_lines.append(f"{key}: {value}")
            request_lines.append("Connection: close")
            request_lines.append("")  # End of headers.
            request_lines.append(data if data else "")
            request_str = "\r\n".join(request_lines)

            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port, ssl=ssl_context),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                raise TimeoutError("Connection timed out")

            writer.write(request_str.encode("utf-8"))
            try:
                await asyncio.wait_for(writer.drain(), timeout=self.timeout)
            except asyncio.TimeoutError:
                writer.close()
                await writer.wait_closed()
                raise TimeoutError("Writing data timed out")

            try:
                response_data = await asyncio.wait_for(reader.read(), timeout=self.timeout)
            except asyncio.TimeoutError:
                writer.close()
                await writer.wait_closed()
                raise TimeoutError("Reading response timed out")

            writer.close()
            await writer.wait_closed()
            return response_data.decode("utf-8")

        elif self.version == "2":
            return await self._handle_http2_async_request(method, parsed_url, path, headers, data)
        else:
            raise HttpClientError(f"Unsupported HTTP version: {self.version}")

    async def _handle_http2_async_request(self, method, parsed_url, path, headers, data):
        """
        Handle HTTP/2 asynchronous requests using our h2 submodule.
        This method:
          1. Establishes a connection with ALPN configured for HTTP/2.
          2. Verifies that HTTP/2 was negotiated.
          3. Sends the connection preface.
          4. Instantiates an HTTP2Multiplexer to manage streams.
          5. Uses HPACK to encode headers and sends a HEADERS frame (and optionally a DATA frame).
          6. Waits for a response frame and returns its payload.
        """
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
        ssl_context = None
        if parsed_url.scheme == "https":
            ssl_context = ssl.create_default_context()
            ssl_context.set_alpn_protocols(["h2", "http/1.1"])
        else:
            raise HttpClientError("HTTP/2 requires an HTTPS connection.")

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port, ssl=ssl_context),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError("HTTP/2 Connection timed out")

        # Verify ALPN negotiation.
        negotiated = writer.get_extra_info("ssl_object").selected_alpn_protocol()
        if negotiated != "h2":
            writer.close()
            await writer.wait_closed()
            raise HTTP2Error("Failed to negotiate HTTP/2 protocol.")

        # Send the HTTP/2 connection preface.
        await send_connection_preface(writer)

        # Instantiate the HTTP/2 multiplexer.
        multiplexer = multiplex.HTTP2Multiplexer(reader, writer)
        await multiplexer.start_receiving()

        # Encode headers using our HPACK stub.
        header_block = hpack.hpack_encode(headers)

        # Create a new stream and send a HEADERS frame.
        stream_id = multiplexer.create_stream()
        headers_frame = frames.HTTP2Frame(
            frame_type=frames.HEADERS,
            flags=0x4,  # END_HEADERS flag.
            stream_id=stream_id,
            payload=header_block
        )
        await multiplexer.send_frame(headers_frame)

        if data:
            # Send a DATA frame with END_STREAM flag.
            data_frame = frames.HTTP2Frame(
                frame_type=frames.DATA,
                flags=0x1,  # END_STREAM flag.
                stream_id=stream_id,
                payload=to_bytes(data)
            )
            await multiplexer.send_frame(data_frame)

        # Wait for a response frame on the stream.
        response_frame = await multiplexer.get_response(stream_id, timeout=self.timeout)
        response_payload = response_frame.payload

        # Clean up.
        await multiplexer.stop_receiving()
        writer.close()
        await writer.wait_closed()

        return response_payload.decode("utf-8")

    def _handle_http2_sync_request(self, method, parsed_url, path, headers, data):
        """
        Handle synchronous HTTP/2 requests by running the asynchronous implementation
        in an event loop.
        """
        return asyncio.run(self._handle_http2_async_request(method, parsed_url, path, headers, data))

    # --- Convenience methods for synchronous requests ---
    def get(self, url, headers=None, params=None):
        return self.sync_request("GET", url, headers=headers, params=params)

    def post(self, url, headers=None, data=None, json_data=None):
        return self.sync_request("POST", url, headers=headers, data=data, json_data=json_data)

    def put(self, url, headers=None, data=None, json_data=None):
        return self.sync_request("PUT", url, headers=headers, data=data, json_data=json_data)

    def patch(self, url, headers=None, data=None, json_data=None):
        return self.sync_request("PATCH", url, headers=headers, data=data, json_data=json_data)

    def delete(self, url, headers=None, data=None, json_data=None):
        return self.sync_request("DELETE", url, headers=headers, data=data, json_data=json_data)

    def head(self, url, headers=None, params=None):
        return self.sync_request("HEAD", url, headers=headers, params=params)

    def options(self, url, headers=None, params=None):
        return self.sync_request("OPTIONS", url, headers=headers, params=params)

    # --- Convenience methods for asynchronous requests ---
    async def aget(self, url, headers=None, params=None):
        return await self.async_request("GET", url, headers=headers, params=params)

    async def apost(self, url, headers=None, data=None, json_data=None):
        return await self.async_request("POST", url, headers=headers, data=data, json_data=json_data)

    async def aput(self, url, headers=None, data=None, json_data=None):
        return await self.async_request("PUT", url, headers=headers, data=data, json_data=json_data)

    async def apatch(self, url, headers=None, data=None, json_data=None):
        return await self.async_request("PATCH", url, headers=headers, data=data, json_data=json_data)

    async def adelete(self, url, headers=None, data=None, json_data=None):
        return await self.async_request("DELETE", url, headers=headers, data=data, json_data=json_data)

    async def ahead(self, url, headers=None, params=None):
        return await self.async_request("HEAD", url, headers=headers, params=params)

    async def aoptions(self, url, headers=None, params=None):
        return await self.async_request("OPTIONS", url, headers=headers, params=params)
