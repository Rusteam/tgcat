
from telethon import functions, types
from src.train.download import tg_client



async def main():
    chan = await tg_client(functions.channels.GetFullChannelRequest('artintelligence'))
    messages = await tg_client.get_messages('artintelligence', 10)
    return chan,messages


with tg_client:
    chan,messages = tg_client.loop.run_until_complete(main())
    
