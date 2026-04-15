import json
import logging
import time
from typing import Optional

from confluent_kafka import Producer, Consumer, KafkaError, KafkaException

logger = logging.getLogger(__name__)

BOOTSTRAP_SERVERS = "my-cluster-kafka-bootstrap:9092"
REQUEST_TIMEOUT_SEC = 5
MAX_RETRIES = 3


class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers: str = BOOTSTRAP_SERVERS):
        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "acks": "all",
        })

    def _delivery_callback(self, err, msg):
        if err:
            logger.error(f"Delivery failed: {err}")
        else:
            logger.debug(f"Delivered to {msg.topic()} [{msg.partition()}]")

    def send(self, topic: str, message: dict, retries: int = MAX_RETRIES) -> bool:
        for attempt in range(retries):
            try:
                self.producer.produce(
                    topic,
                    key=message.get("job_id", "").encode("utf-8"),
                    value=json.dumps(message).encode("utf-8"),
                    callback=self._delivery_callback,
                )
                self.producer.flush(timeout=REQUEST_TIMEOUT_SEC)
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(1)
        return False

    def close(self):
        self.producer.flush()


class KafkaConsumerWrapper:
    def __init__(
        self,
        topics: list[str],
        group_id: str,
        bootstrap_servers: str = BOOTSTRAP_SERVERS,
    ):
        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        })
        self.consumer.subscribe(topics)
        self.running = True

    def poll(self, timeout: float = 1.0) -> Optional[dict]:
        try:
            msg = self.consumer.poll(timeout)
            if msg is None:
                return None
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    return None
                raise KafkaException(msg.error())
            return json.loads(msg.value().decode("utf-8"))
        except Exception as e:
            logger.error(f"Poll error: {e}")
            return None

    def wait_for_message(
        self,
        target_job_id: str,
        timeout_sec: float = REQUEST_TIMEOUT_SEC,
    ) -> Optional[dict]:
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            if not self.running:
                break
            msg = self.poll(timeout=0.5)
            if msg and msg.get("job_id") == target_job_id:
                return msg
        return None

    def close(self):
        self.running = False
        self.consumer.close()
