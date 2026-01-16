# StreamStore – Local Kafka with Docker Compose

This project provides a lightweight local Apache Kafka instance using Docker Compose, along with a simple Python producer and consumer to demonstrate streaming order data.

## Overview

The stack currently includes:

- **Kafka** (Confluent image, KRaft mode, no ZooKeeper)
  - Image: `confluentinc/cp-kafka:7.7.7`
  - Exposed port: `9092`
  - Advertised listener: `PLAINTEXT://localhost:9092`
  - Data persisted in a Docker volume `kafka_kraft`
- **Python apps**
  - `producer.py`: sends order events to the `orders` topic
  - `tracker.py`: consumes and prints order events from the `orders` topic

`docker-compose.yaml`:

```yaml
version: '3.8'

services:
  kafka:
    image: confluentinc/cp-kafka:7.7.7
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_KRAFT_MODE: 'true'
      CLUSTER_ID: '1L6g7nGhU-eAKfL--X25wo'
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
    volumes:
      - kafka_kraft:/var/lib/kafka/data

volumes:
  kafka_kraft:
```

## Prerequisites

- Docker (Desktop or Engine)
- Docker Compose (built-in `docker compose` or legacy `docker-compose`)
- Python 3.x
- `pip` (Python package manager)

Verify installation:

```bash
docker version
docker compose version  # or: docker-compose version
python --version
pip --version
```

## Running Kafka

From the project root (where `docker-compose.yaml` is located):

### Start in foreground (see logs)

```bash
docker compose up
```

This will:

- Pull the Kafka image if not already present
- Start the `kafka` container
- Stream Kafka logs to your terminal

Stop with `Ctrl + C`.

### Start in background (detached)

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

View logs:

```bash
docker logs kafka
# or follow logs
docker compose logs -f
```

### Stop and remove containers

Stop containers:

```bash
docker compose down
```

Stop and **remove volumes** (clears Kafka data):

```bash
docker compose down -v
```

## Connecting to Kafka

Your applications can connect using:

- **Bootstrap server:** `localhost:9092`
- **Protocol:** PLAINTEXT (no TLS, no auth, dev only)

Example (using a typical Kafka client configuration):

```bash
bootstrap.servers=localhost:9092
```

Any producer/consumer library (Java, Python, Node, etc.) can use `localhost:9092` as the broker address.

## StreamStore Python Applications

This project includes two simple Python scripts that work with the Kafka broker:

- `producer.py` – sends a single order event to Kafka
- `tracker.py` – continuously consumes order events and prints them

Both use the `confluent-kafka` Python client and communicate via the `orders` topic.

### Install Python dependencies

From the project root:

```bash
pip install confluent-kafka
```

(Optionally set up and activate a virtual environment first.)

### Producer – `producer.py`

`producer.py`:

- Connects to Kafka at `localhost:9092`
- Builds a sample order payload:
  - Random `order_id` (`uuid4`)
  - `user`: `"Laura"`
  - `item`: `"Frozen Yogurt"`
  - `quantity`: `10`
- Serializes the order as JSON
- Produces the message to the `orders` topic
- Uses a delivery callback to print whether the message was successfully delivered
- Flushes the producer to ensure the message is sent

Run the producer:

```bash
python producer.py
```

Expected behavior:

- The script exits after sending one message
- Terminal output shows whether delivery succeeded and the topic/partition/offset

### Consumer – `tracker.py`

`tracker.py`:

- Connects to Kafka at `localhost:9092`
- Uses consumer group `order-tracker`
- Subscribes to the `orders` topic
- Continuously polls for new messages
- For each message:
  - Decodes the JSON payload
  - Prints:  
    `Received order <quantity> x <item> from <user>`

Run the consumer:

```bash
python tracker.py
```

Expected behavior:

- The script prints:  
  `Consumer is running and subscribed to orders topic`
- Whenever a new message arrives on `orders`, you see output like:  
  `Received order 10 x Frozen Yogurt from Laura`
- Stop it with `Ctrl + C` (it will print a “Stopping consumer” message and close cleanly)

### Typical workflow

1. **Start Kafka** (in one terminal):

   ```bash
   docker compose up
   ```

2. **Start the consumer** (second terminal):

   ```bash
   python tracker.py
   ```

3. **Send an order** (third terminal):

   ```bash
   python producer.py
   ```

4. Watch the consumer terminal; you should see the order printed.

You can run `producer.py` multiple times; each execution will create a new order event that the consumer will process.

## Verifying Kafka and StreamStore Together

To confirm everything works end-to-end:

1. Ensure Kafka is running and listening on `localhost:9092`.
2. Start `tracker.py` and verify it shows it is subscribed to `orders`.
3. Run `producer.py`; confirm:
   - The producer prints successful delivery.
   - The consumer prints the corresponding order line.

If either side fails, check:

- Kafka container logs (`docker logs kafka`)
- Python script output / stack traces
- That `confluent-kafka` is installed and Python can import it

## Common Issues / Troubleshooting

- **Nothing seems to happen when I run Kafka commands**
  - Make sure you are in the directory with `docker-compose.yaml`.
  - Run without `-d` to see logs:  
    ```bash
    docker compose up
    ```
- **Port already in use**
  - If something else uses `9092`, either stop it or change the `ports` section in `docker-compose.yaml`, e.g.:
    ```yaml
    ports:
      - "9093:9092"
    ```
    Then connect to `localhost:9093` in the Python configs.
- **Python scripts can’t connect to Kafka**
  - Confirm Kafka is running (`docker ps`).
  - Confirm the port mapping (`0.0.0.0:9092->9092/tcp`).
  - Ensure `bootstrap.servers` in both scripts matches the mapped port.
- **No `docker compose` command**
  - Use the legacy command:
    ```bash
    docker-compose up
    ```

## Extending the Setup

You can extend this stack by:

- Adding more Python services (e.g., multiple producers/consumers for different topics)
- Adding Schema Registry and using Avro/Protobuf instead of raw JSON
- Adding a Kafka UI (e.g., Kafdrop, Kafka UI, AKHQ) for inspecting topics and messages
- Integrating StreamStore into a larger microservices architecture
