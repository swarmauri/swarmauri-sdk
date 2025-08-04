import pytest
from peagen.gateway.hooks.workers import _check_pool_policy
from peagen.transport.jsonrpc import RPCException


def test_policy_rejects_ip():
    policy = {"allowed_cidrs": ["10.0.0.0/24"], "max_instances": 5}
    with pytest.raises(RPCException):
        _check_pool_policy(policy, "192.168.0.1", 1)


def test_policy_rejects_capacity():
    policy = {"allowed_cidrs": ["0.0.0.0/0"], "max_instances": 1}
    with pytest.raises(RPCException):
        _check_pool_policy(policy, "10.0.0.1", 1)


def test_policy_accepts_valid_worker():
    policy = {"allowed_cidrs": ["10.0.0.0/24"], "max_instances": 2}
    _check_pool_policy(policy, "10.0.0.1", 1)
