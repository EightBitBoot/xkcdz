import zlib
import platform
import asyncio
import time

import websockets

from .types import GatewayPayload

__all__ = [
    "DiscordGatewayClient"
]

ZLIB_SUFFIX = b'\x00\x00\xff\xff'

#TODO(Adin): Identify Counting
#TODO(Adin): Rate limiting (120 messages / 60s)

class DiscordGatewayClient:
    def __init__(self, url):
        self._url = url

        self._websocket_client = None # Set in connect()
        self._decompressor = zlib.decompressobj()
        self._last_sequence = None
        self._is_closed = False
        self._heartbeat_interval = None

    async def connect_and_handshake(self, bot_token, bot_name, intents, identify_os=None):
        await self.connect()
        return await self.handshake(bot_token, bot_name, intents, identify_os)

    async def connect(self):
        self._websocket_client = await websockets.connect(self._url + "/?v=9&encoding=json&compress=zlib-stream")

    async def handshake(self, bot_token, bot_name, intents, os=None):
        hello_payload = await self.recv()
        if hello_payload.op != 10:
            print("First packet recieved in handshake wasn't a hello packet!\nWas this function run first after connecting?")
            return None

        print("Recieved hello payload from gateway")
        self._heartbeat_interval = hello_payload.d["heartbeat_interval"]

        identify_os = os if os is not None else platform.system().lower()

        identify_data = {
            "token": bot_token,
            "properties": {
                "$os": identify_os,
                "$browser": bot_name,
                "$device": bot_name
            },
            "compress": False, # Transmission compression is used instead
            "intents": intents
        }

        print("Sending identify payload")
        identify_payload = GatewayPayload(2, identify_data, None, None)
        await self.send(identify_payload)

        ready_payload = await self.recv()
        if ready_payload.t.lower() != "ready":
            print("Gateway didn't send ready as next packet after identify!")
            return None

        print("Ready recieved")

        return ready_payload

    async def recv(self, *args, **kwargs):
        incoming_raw = await self._websocket_client.recv(*args, **kwargs)
        if incoming_raw[-4:] != ZLIB_SUFFIX:
            print("Recieved message that doesn't end in zlib suffix!")
            return None

        incoming_str = self._decompressor.decompress(incoming_raw).decode("utf-8")
        payload = GatewayPayload.from_json_str(incoming_str) 

        if payload.s is not None:
            self._last_sequence = payload.s

        return payload

    async def send(self, payload, *args, **kwargs):
        payload_str = None

        if type(payload) == str:
            payload_str = payload
        elif type(payload) == GatewayPayload:
            payload_str = payload.to_json()
        else:
            raise TypeError("payload isn't a string or GatewayPayload")

        await self._websocket_client.send(payload_str, *args, **kwargs)

    async def send_heartbeat_task(self):
        now  = time.perf_counter()
        then = time.perf_counter()

        while not self._is_closed:
            await asyncio.sleep(self._heartbeat_interval / 1000)
            if self._is_closed:
                break

            now = time.perf_counter()
            print("Sending heartbeat payload after {:.0f}ms; heartbeat_interval={}ms".format((now - then) * 1000, self._heartbeat_interval))
            await self.send(GatewayPayload(1, self._last_sequence, None, None))
            then = time.perf_counter()

    async def close(self, op=1000):
        # TODO(Adin): Send disconnect message 
        await self._websocket_client.close()
        self._is_closed = True