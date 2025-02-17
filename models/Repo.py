import discord
from tools.logger import log

class Repo:
    def __init__(self, name: str, url: str) -> None:
        if not isinstance(name, str) or not isinstance(url, str):
            raise TypeError(f"Arguments 'name' and 'url' must be strings. '{type(name).__name__}' and '{type(url).__name__}' given.")

        self.name = name
        self.url = url
        self.channels: list[discord.TextChannel] = []

    def add_channel(self, channel: discord.TextChannel) -> None:
        if not isinstance(channel, discord.TextChannel):
            raise TypeError(f"Argument 'channel' must be a discord.TextChannel. '{type(channel).__name__}' given.")

        self.channels.append(channel)
        log("info", f"Channel '{channel.name}' added to the list of channels to notify for the repo '{self.name}'.")
    
    def remove_channel(self, channel: discord.TextChannel) -> None:
        if not isinstance(channel, discord.TextChannel):
            raise TypeError(f"Argument 'channel' must be a discord.TextChannel. '{type(channel).__name__}' given.")

        self.channels.pop(self.channels.index(channel))
        log("info", f"Channel '{channel.name}' removed from the list of channels to notify for the repo '{self.name}'.")

    def encode(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "channels": [channel.id for channel in self.channels]
        }
