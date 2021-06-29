from queue import Queue, Empty
import base64
import asyncio
from typing import Dict, Tuple
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

    async def get(self, topic: str, payload: Dict, timeout: int = 10):
        """Get the response for the topic."""

        # Handle topic
        self.topics[topic] = 0
        self.pool[topic] = Queue()

        # Subscribe to response topic
        self.mqtt.client.subscribe(f"{topic}/response")
        self.mqtt.client.subscribe(f"{topic}/keepalive")

        # Publish data
        await self.mqtt.publish(topic, json.dumps(payload))

        # Wait for response (with timeout and keepalive)
        while True:
            try:
                response = self.pool.get(topic).get_nowait()

                # Unsubscribe
                await self.mqtt.unsubscribe(f"{topic}/response")
                await self.mqtt.unsubscribe(f"{topic}/keepalive")

                del self.topics[topic]

                # Return response
                return response

            except Empty:
                pass

            if self.topics[topic] > timeout:
                raise HTTPException(
                    status_code=HTTP_504_GATEWAY_TIMEOUT,
                    detail="A connected server did not answer in time.",
                )

            await asyncio.sleep(0.1)
            self.topics[topic] += 0.1

    async def get_bytes(
        self, topic: str, payload: Dict, timeout: int = 30
    ) -> Tuple[str, str, bytes]:
        """Get filename, mime type and bytes for the topic."""

        # Handle topic
        self.topics[topic] = 0
        self.pool[topic] = Queue()

        # Subscribe to response topic
        self.mqtt.client.subscribe(f"{topic}/response")
        self.mqtt.client.subscribe(f"{topic}/keepalive")

        # Publish data
        await self.mqtt.publish(topic, json.dumps(payload))

        # Wait for response (with timeout and keepalive)

        data = b""

        while True:
            try:
                response = self.pool.get(topic).get_nowait()

                if not response.get("data"):

                    # Unsubscribe
                    await self.mqtt.unsubscribe(f"{topic}/response")
                    await self.mqtt.unsubscribe(f"{topic}/keepalive")

                    del self.topics[topic]

                    # Return response
                    return response.get("filename"), response.get("mime"), data

                else:
                    data = data + base64.b64decode(response.get("data").encode())
                    self.topics[topic] = 0

            except Empty:
                pass

            if self.topics[topic] > timeout:
                raise HTTPException(
                    status_code=HTTP_504_GATEWAY_TIMEOUT,
                    detail="A connected server did not answer in time.",
                )

            await asyncio.sleep(0.1)
            self.topics[topic] += 0.1

    def handle(self, topic: str, payload: Dict):
        """Handle an incoming mqtt message."""

        if topic.endswith("/response"):
            real_topic = topic[:-9]
            if real_topic in self.topics.keys():
                self.pool[real_topic].put(payload)

        elif topic.endswith("/keepalive"):
            real_topic = topic[:-10]
            if real_topic in self.topics.keys():
                self.topics[real_topic] = 0
