"""
Shared test configuration and fixtures used across all tests.
This prevents code duplication and ensures consistent test setup.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from trancepoint import Config
from trancepoint import Event, EventType, ExecutionStatus

@pytest.fixture
def valid_config():
    """Valid config for testing"""
    return Config(
        api_key="sk_test_abc123",
        api_endpoint="https://api.test.com",
        batch_size=10,
        flush_interval_seconds=5,
        enabled=True,
        debug=False,
    )

@pytest.fixture
def disabled_config():
    """Config with observability disabled (for testing skip behavior)"""
    return Config(
        api_key="sk_test_abc123",
        enabled=False,  # Disabled
    )


@pytest.fixture
def invalid_configs():
    """Dictionary of invalid configs for testing validation"""
    return {
        "no_api_key": {"api_key": ""},
        "invalid_api_key": {"api_key": "invalid_not_sk"},
        "invalid_batch_size_too_high": {"api_key": "sk_...", "batch_size": 1001},
        "invalid_batch_size_zero": {"api_key": "sk_...", "batch_size": 0},
        "invalid_endpoint_no_protocol": {"api_key": "sk_...", "api_endpoint": "api.com"},
        "negative_timeout": {"api_key": "sk_...", "timeout_seconds": -1},
    }

@pytest.fixture
def start_event():
    """Valid START event"""
    return Event(
        event_id="evt_001",
        trace_id="tr_abc123",
        event_type=EventType.START,
        status=ExecutionStatus.RUNNING,
        agent_name="test_agent",
        timestamp_ms=1703352000000,
        input_text="args: ('test',), kwargs: {}",
    )


@pytest.fixture
def end_event():
    """Valid END event"""
    return Event(
        event_id="evt_002",
        trace_id="tr_abc123",
        event_type=EventType.END,
        status=ExecutionStatus.SUCCESS,
        agent_name="test_agent",
        timestamp_ms=1703352002500,
        output_text='{"result": "success"}',
        duration_ms=2500,
    )


@pytest.fixture
def error_event():
    """Valid ERROR event"""
    return Event(
        event_id="evt_003",
        trace_id="tr_abc123",
        event_type=EventType.ERROR,
        status=ExecutionStatus.ERROR,
        agent_name="test_agent",
        timestamp_ms=1703352000500,
        error="ValueError: invalid input",
        error_type="ValueError",
        duration_ms=500,
    )


@pytest.fixture
def event_sequence(start_event, end_event):
    """Sequence of events representing complete execution"""
    return [start_event, end_event]

@pytest.fixture
def mock_requests(mocker):
    """Mock requests library"""
    return mocker.patch("requests.Session.post")


@pytest.fixture
def mock_env(mocker):
    """Mock environment variables"""
    return mocker.patch.dict(os.environ, {
        "AGENT_OBS_API_KEY": "sk_test_env",
        "AGENT_OBS_BATCH_SIZE": "15",
        "AGENT_OBS_DEBUG": "false",
    })


@pytest.fixture
def mock_config_from_file(mocker):
    """Mock config file loading"""
    config = Config(
        api_key="sk_test_file",
        batch_size=20,
    )
    return mocker.patch(
        "agent_observability.config.ObservabilityConfig.from_file",
        return_value=config
    )

@pytest.fixture
def http_client(valid_config, mock_requests):
    """HTTP client instance with mocked requests"""
    from trancepoint import SyncEventClient
    client = SyncEventClient(valid_config)
    return client

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "slow: slow tests")