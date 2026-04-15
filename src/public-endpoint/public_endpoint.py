import sys
import logging
import uuid
import threading
from queue import Queue, Empty

import pytz
from flask import Flask, jsonify

sys.path.insert(0, "/app")
from kafka_helper import KafkaConsumerWrapper, KafkaProducerWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CONVERTER_REQUESTS_TOPIC = "converter-requests"
CONVERTER_RESPONSES_TOPIC = "converter-responses"

response_queues = {}
queues_lock = threading.Lock()


def kafka_consumer_thread():
    consumer = KafkaConsumerWrapper(
        topics=[CONVERTER_RESPONSES_TOPIC],
        group_id="public-endpoint-consumer-group",
    )
    logger.info("Kafka consumer thread started")

    try:
        while True:
            msg = consumer.poll(timeout=0.5)
            if msg is None:
                continue

            job_id = msg.get("job_id")
            with queues_lock:
                if job_id in response_queues:
                    response_queues[job_id].put(msg)
                    logger.info(f"Routed response for job_id={job_id}")
    except Exception as e:
        logger.error(f"Consumer thread error: {e}")
    finally:
        consumer.close()


@app.route("/public-date", methods=["GET"])
def get_public_date():
    job_id = str(uuid.uuid4())
    reply_to = CONVERTER_RESPONSES_TOPIC

    producer = KafkaProducerWrapper()
    message = {
        "job_id": job_id,
        "reply_to": reply_to,
    }

    if not producer.send(CONVERTER_REQUESTS_TOPIC, message):
        producer.close()
        return jsonify({"error": "Failed to send request"}), 503
    producer.close()

    response_queue = Queue()
    with queues_lock:
        response_queues[job_id] = response_queue

    try:
        try:
            response = response_queue.get(timeout=5.0)
        except Empty:
            with queues_lock:
                response_queues.pop(job_id, None)
            return jsonify({"error": "Gateway Timeout"}), 504

        with queues_lock:
            response_queues.pop(job_id, None)

        return jsonify({"converted_date": response.get("moscow_time")})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    consumer_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    consumer_thread.start()

    app.run(host="0.0.0.0", port=5002)
