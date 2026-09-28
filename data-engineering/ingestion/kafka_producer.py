"""
Weather Data Kafka Producer
SIH 2026 - National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer

Fetches current weather data using the SAME Open-Meteo logic already
used by `fetch_openmeteo.py` (imported, not duplicated) and publishes
each reading as a JSON message to the Kafka topic `weather-data`.

Library choice: confluent-kafka
------------------------------------------------------------------
- It's a thin wrapper around librdkafka (the reference C client for
  Kafka), so it stays current with the Kafka wire protocol and is
  compatible with Kafka 4.x brokers (including KRaft mode — KRaft is a
  broker-side controller change and does not affect the client
  producer/consumer protocol).
- Actively maintained by Confluent (the company founded by Kafka's
  creators), unlike the original `kafka-python`, which stalled for a
  long time.
- Ships prebuilt binary wheels for Windows/macOS/Linux, so `pip install
  confluent-kafka` works out of the box — no separate C toolchain
  needed, which matters for a Windows hackathon laptop.
- `kafka-python-ng` (a community fork of kafka-python) is a reasonable
  pure-Python alternative if you specifically want to avoid a native
  dependency, but confluent-kafka is the more production-proven and
  better-supported choice for a real streaming layer.

This script does NOT touch the existing raw-JSON-to-disk flow in
fetch_openmeteo.py — it only reuses its fetch/extract functions.
"""

import json
import logging
import sys
import time
from pathlib import Path

from confluent_kafka import KafkaException, Producer

# Reuse the existing, already-working ingestion logic instead of
# duplicating API calls or field extraction.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_openmeteo import (  # noqa: E402
    LATITUDE,
    LONGITUDE,
    TIMEZONE,
    extract_current_weather,
    fetch_current_weather,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "weather-data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("kafka_producer")


def build_producer() -> Producer:
    """Create and return a configured Kafka Producer instance."""
    config = {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        # Wait for the leader to acknowledge the write before considering
        # it delivered — a sensible default for a data pipeline.
        "acks": "all",
        # Fail fast locally instead of hanging if the broker is unreachable.
        "socket.timeout.ms": 10000,
        "message.timeout.ms": 10000,
    }
    try:
        return Producer(config)
    except KafkaException as exc:
        logger.error("Failed to create Kafka producer: %s", exc)
        sys.exit(1)


def delivery_report(err, msg):
    """Callback invoked once per message to report delivery success/failure."""
    if err is not None:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.info(
            "Message delivered to topic='%s' partition=%s offset=%s key=%s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
            msg.key().decode("utf-8") if msg.key() else None,
        )


def build_message(latitude: float, longitude: float, tz: str) -> dict:
    """Fetch current weather and shape it into a Kafka-ready message."""
    logger.info("Fetching current weather from Open-Meteo (lat=%s, lon=%s)...", latitude, longitude)
    raw_payload = fetch_current_weather(latitude, longitude, tz)
    extracted = extract_current_weather(raw_payload, latitude, longitude, tz)

    # Add a producer-side timestamp so downstream consumers know when the
    # message was published, separate from the weather observation time.
    extracted["produced_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return extracted


def publish_weather_message(producer: Producer, message: dict) -> None:
    """Publish a single weather message to the weather-data topic."""
    # Location-based key so all readings for the same place land on the
    # same partition and stay in order for a given location.
    key = f"{message['latitude']}_{message['longitude']}"

    try:
        producer.produce(
            topic=TOPIC,
            key=key.encode("utf-8"),
            value=json.dumps(message).encode("utf-8"),
            callback=delivery_report,
        )
        # Serve delivery-report callbacks without blocking for long.
        producer.poll(0)
    except BufferError:
        logger.warning("Local producer queue is full, waiting for space...")
        producer.poll(1)
        producer.produce(
            topic=TOPIC,
            key=key.encode("utf-8"),
            value=json.dumps(message).encode("utf-8"),
            callback=delivery_report,
        )
    except KafkaException as exc:
        logger.error("Failed to publish message to Kafka: %s", exc)
        raise


def main():
    logger.info("Starting Kafka producer for topic '%s' at %s", TOPIC, BOOTSTRAP_SERVERS)
    producer = build_producer()

    try:
        message = build_message(LATITUDE, LONGITUDE, TIMEZONE)
        publish_weather_message(producer, message)
    except KafkaException as exc:
        logger.error("Kafka error, aborting: %s", exc)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 - surface any unexpected failure clearly
        logger.error("Unexpected error while producing message: %s", exc)
        sys.exit(1)
    finally:
        # Block until all outstanding messages are delivered (or timeout).
        remaining = producer.flush(timeout=10)
        if remaining > 0:
            logger.warning("%d message(s) were not delivered before flush timeout.", remaining)

    logger.info("Producer finished.")


if __name__ == "__main__":
    main()
