import sys
import logging
from datetime import datetime

import pytz

sys.path.insert(0, "/app")
from kafka_helper import KafkaConsumerWrapper, KafkaProducerWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATE_REQUESTS_TOPIC = "date-requests"


def get_current_date() -> str:
    tomsk_tz = pytz.timezone("Asia/Tomsk")
    current_time = datetime.now(tomsk_tz)
    return current_time.isoformat()


def main():
    consumer = KafkaConsumerWrapper(
        topics=[DATE_REQUESTS_TOPIC],
        group_id="date-server-group",
    )
    producer = KafkaProducerWrapper()

    logger.info(f"date-server started, consuming from {DATE_REQUESTS_TOPIC}")

    try:
        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue

            job_id = message.get("job_id")
            reply_to = message.get("reply_to")

            if not job_id or not reply_to:
                logger.warning(f"Invalid message: {message}")
                continue

            logger.info(f"Processing job_id={job_id}")

            date_iso = get_current_date()
            response = {
                "job_id": job_id,
                "date": date_iso,
                "status": "success",
            }

            if producer.send(reply_to, response):
                logger.info(f"Sent response for job_id={job_id}")
            else:
                logger.error(f"Failed to send response for job_id={job_id}")

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        consumer.close()
        producer.close()


if __name__ == "__main__":
    main()
