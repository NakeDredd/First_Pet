import sys
import logging
import uuid
from datetime import datetime

import pytz

sys.path.insert(0, "/app")
from kafka_helper import KafkaConsumerWrapper, KafkaProducerWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONVERTER_REQUESTS_TOPIC = "converter-requests"
DATE_REQUESTS_TOPIC = "date-requests"
DATE_RESPONSES_TOPIC = "date-responses"
CONVERTER_RESPONSES_TOPIC = "converter-responses"


def convert_to_moscow(date_iso: str) -> str:
    tomsk_date = datetime.fromisoformat(date_iso).replace(
        tzinfo=pytz.timezone("Asia/Tomsk")
    )
    moscow_date = tomsk_date.astimezone(pytz.timezone("Europe/Moscow"))
    return moscow_date.isoformat()


def main():
    converter_consumer = KafkaConsumerWrapper(
        topics=[CONVERTER_REQUESTS_TOPIC],
        group_id="converter-consumer-group",
    )
    date_consumer = KafkaConsumerWrapper(
        topics=[DATE_RESPONSES_TOPIC],
        group_id="converter-date-consumer-group",
    )
    producer = KafkaProducerWrapper()

    job_id_mapping = {}

    logger.info("timezone-converter started")

    try:
        while True:
            msg = converter_consumer.poll(timeout=0.5)
            if msg:
                orig_job_id = msg.get("job_id")
                reply_to = msg.get("reply_to", CONVERTER_RESPONSES_TOPIC)

                internal_job_id = str(uuid.uuid4())
                job_id_mapping[internal_job_id] = {
                    "orig_job_id": orig_job_id,
                    "reply_to": reply_to,
                }

                request_msg = {
                    "job_id": internal_job_id,
                    "reply_to": DATE_RESPONSES_TOPIC,
                }
                producer.send(DATE_REQUESTS_TOPIC, request_msg)
                logger.info(f"Forwarded request {orig_job_id} -> {internal_job_id}")

            response_msg = date_consumer.poll(timeout=0.5)
            if response_msg:
                internal_job_id = response_msg.get("job_id")
                mapping = job_id_mapping.pop(internal_job_id, None)

                if mapping:
                    moscow_time = convert_to_moscow(response_msg.get("date", ""))
                    result = {
                        "job_id": mapping["orig_job_id"],
                        "moscow_time": moscow_time,
                        "status": "success",
                    }
                    producer.send(mapping["reply_to"], result)
                    logger.info(f"Sent response for {mapping['orig_job_id']}")

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        converter_consumer.close()
        date_consumer.close()
        producer.close()


if __name__ == "__main__":
    main()
