#!/usr/bin/env python3

import requests
import json
import hjson
from threading import Thread
import time
import asyncio

from discord_api import DiscordGatewayClient

class PrintThread(Thread):
    def run(self):
        then = time.perf_counter_ns()
        now = time.perf_counter_ns()
        while True:
            print("Time Slept: {}".format(now - then))
            then = time.perf_counter()
            time.sleep(1.0)
            now = time.perf_counter()


BASE_DISCORD_URL = "https://discord.com/api/"
DISCORD_URL_V9 = BASE_DISCORD_URL + "/v9/"

async def main(loop: asyncio.AbstractEventLoop):
    # json_data = None
    # with open("../xkcd.json", "r") as data_file:
    #     json_data = json.loads("".join(data_file.readlines()))

    bot_secrets = None
    with open("secrets.hjson", "r") as secrets_file:
        bot_secrets = hjson.loads("".join(secrets_file.readlines()))

    bot_token = bot_secrets["bot_token"]
    bot_name = bot_secrets["bot_name"]

    gateway_json = requests.get(DISCORD_URL_V9 + "/gateway/bot", headers={"Authorization": "Bot " + bot_token}).json()
    # print(json.dumps(gateway_json, indent=4), end="\n\n")

    gateway_client = DiscordGatewayClient(gateway_json["url"])
    
    ready_payload = await gateway_client.connect_and_handshake(bot_token, bot_name, 1)
    print()
    print(ready_payload, end="\n\n")

    heartbeat_task = loop.create_task(gateway_client.send_heartbeat_task())

    while True:
        event_payload = await gateway_client.recv()
        print("Recieved:")
        print(event_payload, end="\n\n")

    await gateway_client.close()
    

if __name__ == "__main__":
    print_thread = PrintThread()
    # print_thread.start()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))
    except KeyboardInterrupt as inter:
        print("Interrupted __main__")