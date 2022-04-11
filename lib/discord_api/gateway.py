import zlib
import platform
import asyncio
import time
import json
from threading import Lock
import os
from datetime import datetime

import websockets

from .types import GatewayPayload
from .exception import GatewayException

__all__ = [
    "DiscordGatewayClient"
]

ZLIB_SUFFIX = b'\x00\x00\xff\xff'

#TODO(Adin): Rate limiting (120 messages / 60s)
#TODO(Adin): Config System

_identify_file_mutex = Lock()
#TODO(Adin): Move these to config system
IDENTIFY_FILE_NAME = "identifies.json"
IDENTIFY_MAX = 1000

# Number of seconds in 24 hours
TF_HOUR_SECONDS = 86400

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

    def _load_identifies_from_file(self):
        _identify_file_mutex.acquire()

        identifies = 0
        identify_time_period = time.time()

        if os.path.exists(IDENTIFY_FILE_NAME):
            identify_file_contents = None

            with open(IDENTIFY_FILE_NAME, "rt") as identify_file:
                identify_file_contents = "".join(identify_file.readlines())

            identifies_parsed_json = json.loads(identify_file_contents)

            identifies = identifies_parsed_json["identifies"]
            identify_time_period = identifies_parsed_json["identify_time_period"]

        _identify_file_mutex.release()

        return (identifies, identify_time_period)

    def _update_identifies_file(self, identifies, old_identify_time_period):
        _identify_file_mutex.acquire()

        with open(IDENTIFY_FILE_NAME, "w+t") as identify_file:
            # Number of identifies in the 24 hour period
            res_identifies = 1
            # Unix timestamp of the beginning of the 24 hour period
            res_identify_time_period = int(time.time())

            if int(time.time()) < old_identify_time_period + TF_HOUR_SECONDS:
                # 24 hour period hasn't elapsed
                res_identifies = identifies
                res_identify_time_period = old_identify_time_period

            identify_file.truncate(0)
            identify_file.write(json.dumps({"identifies": res_identifies, "identify_time_period": res_identify_time_period}, indent=4))

        _identify_file_mutex.release()

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

        identifies, old_identify_time_period = self._load_identifies_from_file()

        if identifies >= IDENTIFY_MAX:
            raise GatewayException("Max identifies already sent in 24 hour period [{}, {}]".format(
                datetime.fromtimestamp(old_identify_time_period),
                datetime.fromtimestamp(old_identify_time_period + TF_HOUR_SECONDS - 1)))

        print("Sending identify payload")
        identify_payload = GatewayPayload(2, identify_data, None, None)
        await self.send(identify_payload)

        identifies += 1

        print("Identifies:", identifies)

        # handshake() is only run once per instance so a function
        # this meaty in the middle of handshaking should be ok
        self._update_identifies_file(identifies, old_identify_time_period)

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