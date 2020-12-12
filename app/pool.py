import asyncio
from typing import Dict
import json
from fastapi_mqtt.fastmqtt import FastMQTT
from fastapi import HTTPException, status
from starlette.status import HTTP_504_GATEWAY_TIMEOUT

class Pool:
    """Allows for waiting for mqtt responses."""

    def __init__(self, mqtt: FastMQTT):
        self.mqtt = mqtt
        self.pool = {}
        self.topics = {}

    def _get(self, topic):
        response = self.pool.get(topic)

        if response:
            del self.pool[topic]

        return response

    async def get(self, topic: str, payload: Dict, timeout: int = 10):
        """Get the response for the topic."""

        # Handle topic
        self.topics[topic] = 0

        # Subscribe to response topic
        self.mqtt.client.subscribe(f"{topic}/response")
        self.mqtt.client.subscribe(f"{topic}/keepalive")

        print(["Listening on:", f"{topic}/response", f"{topic}/keepalive"])

        # Publish data
        await self.mqtt.publish(topic, json.dumps(payload))

        # Wait for response (with timeout and keepalive)
        while True:
            response = self._get(topic)
            if response:
                # Unsubscribe
                await self.mqtt.unsubscribe(f"{topic}/response")
                await self.mqtt.unsubscribe(f"{topic}/keepalive")

                del self.topics[topic]

                # Return response
                return response

            if self.topics[topic] > timeout:
                raise HTTPException(
                    status_code=HTTP_504_GATEWAY_TIMEOUT,
                    detail="A connected server did not answer in time."
                )

            await asyncio.sleep(0.1)
            self.topics[topic] += 0.1

    def handle(self, topic: str, payload: Dict):
        """Handle an incoming mqtt message."""

        print(f"Pool handles topic {topic} now.")

        if topic.endswith("/response"):
            real_topic = topic[:-9]
            if real_topic in self.topics.keys():
                print("Topic is a response")
                self.pool[real_topic] = payload

        elif topic.endswith("/keepalive"):
            real_topic = topic[:-10]
            if real_topic in self.topics.keys():
                print("Topic is keepalive")
                self.topics[real_topic] = 0

        else:
            print("Topic skipped.")
            print(self.topics)