from confluent_kafka import Consumer, KafkaError, TopicPartition


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

        print(f'Received message: {msg.value().decode("utf-8")}')

    c.close()

if __name__ == "__main__":

    consume(0)