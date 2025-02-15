from confluent_kafka import Consumer, KafkaError, TopicPartition
import json
from dateutil import parser

def consume(partition):
    c = Consumer({
        'bootstrap.servers': 'localhost:9093',
        'group.id': 'mygroup',
        'auto.offset.reset': 'earliest'
    })

    # c.subscribe(['myFirstTopic'])
    c.assign([TopicPartition('test_topic', partition)])

    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        # print(f'Received message: {msg.value().decode("utf-8")}')
        
        # Parse the message value as JSON
        message = json.loads(msg.value().decode("utf-8"))

        # Extract the desired information
        timestamp_str = message["current_time_utc"]["0"]
        timestamp = parser.isoparse(timestamp_str)

        place = message["name"]["0"]
        event = message["event_name"]["0"]
        newsflash = message["event_newsflash"]["0"]

        # Format the output as an alert notification
        alert_notification = f'{timestamp.strftime("%Y-%m-%d %H:%M:%S")} - SURREAL EVENT ALERT: {event} | {place} | {newsflash}'
        alert_info = f'SURREAL EVENT ALERT: {place} | {event}:'
        alert_news = f'{timestamp.strftime("%Y-%m-%d %H:%M:%S")} - {newsflash}'
        print("\n" + alert_info + "\n" + alert_news)

    c.close()

if __name__ == "__main__":

    consume(0)