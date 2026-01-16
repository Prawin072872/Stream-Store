import json
import uuid

from confluent_kafka import Producer

# we are providing the address where kafka resides
producer_config = {
    'bootstrap.servers': 'localhost:9092'
}

# producer is then created considering the above config
producer = Producer(producer_config)

# A callback function to ensure that the data being sent is properly delivered
def delivery_report(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.value().decode('utf-8')}")
        print(f"Delivered to: {msg.topic()} : partition {msg.partition()} : at offset {msg.offset()}")

# Actual data that needs to be sent by the producer to the consumer
order = {
    "order_id": str(uuid.uuid4()),
    "user": "Laura",
    "item": "Frozen Yogurt",
    "quantity": 10
}

# we are converting that dictionary/object like structure to string and then encoding it
# so that it gets converted to bytes which kafka can understand
value = json.dumps(order).encode("utf-8")

# we then ask the producer to produce the event by specifying the topic
# and the value that needs to be added inside it.
producer.produce(
    topic="orders",
    value=value,
    callback=delivery_report
)


# we finally flush the events that are created. kafka process events in batches.
producer.flush()

