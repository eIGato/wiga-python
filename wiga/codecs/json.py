__all__ = ["JsonCodec"]

import json

from wiga.message import (
    Message,
    Topic,
)

from .base import Codec


class JsonCodec(Codec):
    def encode(self, message: Message) -> bytes:
        return json.dumps(
            {
                "topic": message.topic.name,
                "content": message.content,
            },
        ).encode()

    def decode(self, raw_message: bytes) -> Message:
        message_dict = json.loads(raw_message)
        topic_name = message_dict.get("topic", None)
        return Message(
            topic=Topic[topic_name] if topic_name else Topic.NO_TOPIC,
            content=message_dict.get("content", None),
        )
