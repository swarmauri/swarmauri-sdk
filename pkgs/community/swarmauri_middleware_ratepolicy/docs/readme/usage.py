from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

retry = RetryPolicyMiddleware(max_retries=3, initial_wait=0.5)


class RequestEnvelope:
    def __init__(self, payload: str):
        self.payload = payload


request = RequestEnvelope("work-item-123")


def call_next(req):
    raise RuntimeError("Simulated upstream failure")


retry.dispatch(request, call_next)
