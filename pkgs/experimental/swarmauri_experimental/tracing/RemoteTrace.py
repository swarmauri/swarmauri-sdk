from __future__ import ITraceContext

import requests
import json
import uuid
from datetime import datetime

from swarmauri.core.tracing.ITracer import ITracer
from swarmauri.core.tracing.ITraceContext import ITraceContext

# Implementing the RemoteTraceContext class
class RemoteTraceContext(ITraceContext):
    def __init__(self, trace_id: str, name: str):
        self.trace_id = trace_id
        self.name = name
        self.start_time = datetime.now()
        self.attributes = {}
        self.annotations = {}

    def get_trace_id(self) -> str:
        return self.trace_id

    def add_attribute(self, key: str, value):
        self.attributes[key] = value
        
    def add_annotation(self, key: str, value):
        self.annotations[key] = value

# Implementing the RemoteAPITracer class
class RemoteAPITracer(ITracer):
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint

    def start_trace(self, name: str, initial_attributes=None) -> 'RemoteTraceContext':
        trace_id = str(uuid.uuid4())
        context = RemoteTraceContext(trace_id, name)
        if initial_attributes:
            for key, value in initial_attributes.items():
                context.add_attribute(key, value)
        return context

    def end_trace(self, trace_context: 'RemoteTraceContext'):
        trace_context.end_time = datetime.now()
        # Pretending to serialize the context information to JSON
        trace_data = {
            "trace_id": trace_context.get_trace_id(),
            "name": trace_context.name,
            "start_time": str(trace_context.start_time),
            "end_time": str(trace_context.end_time),
            "attributes": trace_context.attributes,
            "annotations": trace_context.annotations
        }
        json_data = json.dumps(trace_data)
        # POST the serialized data to the remote REST API
        response = requests.post(self.api_endpoint, json=json_data)
        if not response.ok:
            raise Exception(f"Failed to send trace data to {self.api_endpoint}. Status code: {response.status_code}")

    def annotate_trace(self, trace_context: 'RemoteTraceContext', key: str, value):
        trace_context.add_annotation(key, value)