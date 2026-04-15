import pytest
import sys
import os
from unittest.mock import MagicMock, patch

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "../src/public-endpoint"))


@pytest.fixture
def mock_kafka():
    mock_producer = MagicMock()
    mock_producer.send.return_value = True

    mock_consumer_class = MagicMock()
    mock_consumer_instance = MagicMock()
    mock_consumer_class.return_value = mock_consumer_instance

    with patch.dict("sys.modules", {"kafka_helper": MagicMock()}):
        import kafka_helper
        kafka_helper.KafkaProducerWrapper.return_value = mock_producer
        kafka_helper.KafkaConsumerWrapper = mock_consumer_class

        yield {
            "producer": mock_producer,
            "consumer_class": mock_consumer_class,
            "consumer": mock_consumer_instance,
        }


@pytest.fixture
def app(mock_kafka):
    with patch.dict("sys.modules", {"kafka_helper": MagicMock()}):
        import kafka_helper
        kafka_helper.KafkaProducerWrapper.return_value = mock_kafka["producer"]
        kafka_helper.KafkaConsumerWrapper = mock_kafka["consumer_class"]

        from public_endpoint import app as flask_app
        flask_app.config["TESTING"] = True
        return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_consumer_thread(mock_kafka):
    mock_queue = MagicMock()
    mock_kafka["consumer"].poll.return_value = None
    return mock_queue
