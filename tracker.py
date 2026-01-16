import json

from confluent_kafka import Consumer

# we are defining the Necessary configuration for the consumer here
# like where the kafka resides so that the consumer can connect to it.
# group id which is a unique string that identifies the consumer group this consumer belongs to
# automatically reset the offset to the earliest offset
consumer_config = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "order-tracker",
    "auto.offset.reset": "earliest"
}

# we then create a consumer instance with the above config
consumer = Consumer(consumer_config)

# We use the Subscribe method to make the consumer subscribe to the orders topic
consumer.subscribe(["orders"])

print("Consumer is running and subscribed to orders topic")

# Runs a continuous loop asking the broker for any new messages on the subscribed topics
# and returns them to the consumer for processing.
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Error:", msg.error())
            continue
        # We are decoding and then extract the value as string
        value = msg.value().decode("utf-8")
        # We then convert that string into a JSON object or Python Dictionary
        order = json.loads(value)

        print(f"Received order {order['quantity']} x {order['item']} from {order['user']}")
except KeyboardInterrupt:
   print("\n Stopping consumer")

finally:
    consumer.close()

