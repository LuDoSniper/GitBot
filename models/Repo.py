import discord
from tools.logger import log

class Repo:
    def __init__(self, name: str, url: str) -> None:
        if not isinstance(name, str) or not isinstance(url, str):
            raise TypeError(f"Arguments 'name' and 'url' must be strings. '{type(name).__name__}' and '{type(url).__name__}' given.")

        self.name = name
        self.url = url
        self.channels: list[dict[str, discord.TextChannel|str|int]] = []

    def add_channel(self, channel: discord.TextChannel, branch: str = "*", roles: list[int|str] = ["everyone"]) -> None:
        if not isinstance(channel, discord.TextChannel):
            raise TypeError(f"Argument 'channel' must be a discord.TextChannel. '{type(channel).__name__}' given.")

        self.channels.append({
            "channel": channel,
            "branch": branch,
            "roles": roles
        })
        log("info", f"Channel '{channel.name}' added to the list of channels to notify for the repo '{self.name}'.")
    
    def remove_channel(self, channel: discord.TextChannel) -> None:
        if not isinstance(channel, discord.TextChannel):
            raise TypeError(f"Argument 'channel' must be a discord.TextChannel. '{type(channel).__name__}' given.")

        for channel in self.channels:
            if channel['channel'] == channel:
                self.channels.remove(channel)
                log("info", f"Channel '{channel.name}' removed from the list of channels to notify for the repo '{self.name}'.")
                return
        self.channels.pop(self.channels.index(channel))
        log("info", f"Channel '{channel.name}' removed from the list of channels to notify for the repo '{self.name}'.")

    def encode(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "channels": self.encode_channels()
        }
    
    def encode_channels(self) -> dict[str, int|str]:
        channels = []
        for channel in self.channels:
            data = {
                "channel": channel['channel'].id,
                "branch": channel['branch'],
                "roles": channel['roles']
            }
            channels.append(data)
        return channels
