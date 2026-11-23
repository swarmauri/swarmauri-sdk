from swarmauri_publisher_redis import RedisPublisher

publisher = RedisPublisher(
    host="localhost",
    port=6379,
    db=0,
)

publisher.publish("my_channel", {"message": "Hello Redis!"})
