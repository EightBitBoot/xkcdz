import requests
import json
import hjson
from threading import Thread
import time
import websockets
import asyncio

class PrintThread(Thread):
    def run(self):
        then = time.perf_counter_ns()
        now = time.perf_counter_ns()
        while True:
            print("Time Slept: {}".format(now - then))
            then = time.perf_counter()
            time.sleep(1.0)
            now = time.perf_counter()


BASE_DISCORD_URL = "https://discord.com/api"
DISCORD_URL_V9 = BASE_DISCORD_URL + "/v9"

last_sequence = None

class DiscordWebsocketClient:
    def __init__(self, websocket_client):
        self._last_sequence = None
        self._is_closed = False
        self.websocket_client = websocket_client

    async def recv(self, *args, **kwargs):
        raw_result = await self.websocket_client.recv(*args, **kwargs)

        json_result = json.loads(raw_result)
        if "s" in json_result:
            self._last_sequence = json_result["s"]

        return raw_result

    async def send(self, *args, **kwargs):
        return await self.websocket_client.send(*args, **kwargs)

    async def close(self, *args, **kwargs):
        self._is_closed = True
        return await self.websocket_client.close()

    async def send_heartbeat_task(self, interval):
        while not self._is_closed:
            then = time.perf_counter()
            await asyncio.sleep(interval / 1000)
            if self._is_closed:
                break

            now = time.perf_counter()
            await self.send(json.dumps({"op": 1, "d": self._last_sequence}))
            print("Heartbeat sent after {}ms; interval={}ms".format((now - then) * 1000, interval))


async def heartbeat(websocket_client, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await websocket_client.send(json.dumps({"op": 1, "d": last_sequence}))
        print("Heartbeat")


async def main():
    json_data = None
    with open("xkcd.json", "r") as data_file:
        json_data = json.loads("".join(data_file.readlines()))

    bot_secrets = None
    with open("secrets.hjson", "r") as secrets_file:
        bot_secrets = hjson.loads("".join(secrets_file.readlines()))

    bot_token = bot_secrets["bot_token"]
    bot_name = bot_secrets["bot_name"]

    gateway_json = requests.get(DISCORD_URL_V9 + "/gateway/bot", headers={"Authorization": "Bot " + bot_token}).json()
    print(json.dumps(gateway_json, indent=4), end="\n\n")

    websocket_client = await websockets.connect(gateway_json["url"] + "/?v=9&encoding=json", ping_interval=None, ping_timeout=None, max_queue=None, max_size=None)
    discord_websocket_client = DiscordWebsocketClient(websocket_client)
    hello_json = json.loads(await discord_websocket_client.recv())
    print(json.dumps(hello_json, indent=4), end="\n\n")

    heartbeat_task = asyncio.create_task(discord_websocket_client.send_heartbeat_task(hello_json["d"]["heartbeat_interval"]))

    identify_payload = {
        "op": 2,
        "d": {
            "token": bot_token,
            "properties": {
                "$os": "linux",
                "$browser": bot_name,
                "$device": bot_name
            },
            "intents": 1
        }
    }
    await discord_websocket_client.send(json.dumps(identify_payload))

    try:
        while True:
            raw_event = await discord_websocket_client.recv()
            print(json.dumps(json.loads(raw_event), indent=4), end="\n\n")
    except KeyboardInterrupt as e:
        print("Interrupted")

    await discord_websocket_client.close()
    

if __name__ == "__main__":
    print_thread = PrintThread()
    # print_thread.start()
    asyncio.run(main())