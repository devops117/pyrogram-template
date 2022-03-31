#MIT License
#
#Copyright (c) 2022 DevOps117
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import asyncio
import logging
from operator import itemgetter
import os # os.path, os.environ
from pathlib import Path
from typing import TypedDict

from ruamel.yaml import YAML
import pyrogram # pyrogram.Client

logging.basicConfig(level=logging.INFO)

pyrogram_sessions_dir=Path("sessions")

config_file=Path("config.yaml")
yaml=YAML(typ="safe")
data=yaml.load(config_file) # look for ./base/config.yaml

CLIENTS=None

pyrogram_client_data = TypedDict(
    "pyrogram_client_data",
    {
        "session_name": str,
        "wheel_userids": list[int],
        "environment_variables": TypedDict(
            "environment_variables",
            {
                "TELEGRAM_API_ID": int,
                "TELEGRAM_API_HASH": str,
                "TELEGRAM_BOT_TOKEN": str | None,
            },
        ),
        "plugins": TypedDict(
            "plugins_data",
            {
                "include": list[str],
                "exclude": list[str] | None,
            },
        ),
    },
)


def client_init(clients_data: list[pyrogram_client_data] = data.get("clients")) -> list[pyrogram.Client] | None:
    global pyrogram_sessions_dir # sessions directory
    
    for session in clients_data:
        api_id, api_hash = itemgetter(
                *itemgetter(
                    "TELEGRAM_API_ID",
                    "TELEGRAM_API_HASH",
                )(session.get("environment_variables"))
            )(os.environ)
        if bot_token := session.get("TELEGRAM_BOT_TOKEN"):
            bot_token = os.environ.get(bot_token)

        client = pyrogram.Client(
            session["session_name"],
            api_id,
            api_hash,
            bot_token=bot_token,
            plugins=session["plugins"],
            workdir=pyrogram_sessions_dir,
        )
        client.wheel_userids = session["wheel_userids"] # A way to feed values, can be accessed using update handler's callback(client)

        yield client


async def async_main() -> None:
    global CLIENTS

    CLIENTS = [
        await client.start()
        for client in client_init()
    ]
    await pyrogram.idle()


if __name__ == "__main__":
    asyncio.run(async_main())
