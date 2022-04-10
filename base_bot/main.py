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
import os # os.environ
from pathlib import Path
from typing import NamedTuple, TypedDict

from ruamel.yaml import YAML
import pyrogram # pyrogram.Client

logging.basicConfig(level=logging.INFO)

pyrogram_sessions_dir=Path("sessions")

yaml=YAML(typ="safe")
CONFIG_DATA = yaml.load(Path("config.yaml")) # look for ./config.yaml


class ClientStore(NamedTuple):
    session_name: str
    client: pyrogram.Client


class PluginsData(TypedDict):
    root: str
    include: list[str] | None
    exclude: list[str] | None


class ClientConfigData(TypedDict):
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_BOT_TOKEN: str | None
    wheel_userids: list[int]
    plugins: PluginsData


def client_create(session_name: str, client_data: ClientConfigData) -> ClientStore:
    global pyrogram_sessions_dir # sessions directory

    api_id, api_hash = itemgetter(
            *(itemgetter("TELEGRAM_API_ID", "TELEGRAM_API_HASH")(client_data))
        )(os.environ)
    if bot_token := client_data.get("TELEGRAM_BOT_TOKEN"):
        bot_token = os.environ.get(bot_token)

    client = pyrogram.Client(
        session_name,
        api_id,
        api_hash,
        bot_token=bot_token,
        plugins=client_data["plugins"],
        workdir=pyrogram_sessions_dir,
    )
    return ClientStore(session_name, client)


def client_init(clients_data: list[dict[str, ClientConfigData]]) -> ClientStore:
    """
    You can use dict.pop() on client_data;
    in case a particular session should be dealt with in a special manner
    """

    for session_name, client_data in clients_data.items():
        client_created = client_create(session_name, client_data)

        # A way to feed values, can be accessed using update handler's callback(client)
        client_created.client.wheel_userids = client_data["wheel_userids"]
        yield client_created


async def async_main() -> None:
    global CONFIG_DATA

    for session_name, client in client_init(CONFIG_DATA.get("clients")):
        await client.start()
    await pyrogram.idle()


if __name__ == "__main__":
    asyncio.run(async_main())
