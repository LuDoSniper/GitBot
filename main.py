# Discord
import discord
import discord.context_managers
from discord.ext import commands, tasks

import requests

# Custom imports
from models.Repo import Repo
from tools.env_link import get
from tools.logger import log
from tools.saver import update, load

class GitBot:

    TOKEN = get("TOKEN")
    DEFAULT_CHANNEL_IDS = get("DEFAULT_CHANNEL_IDS")
    API_URL = "http://gitbot.donnarieix.fr/getlastlog"
    VERBOSE = get("VERBOSE")

    def __init__(self):
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)
        
        self.repos: list[Repo] = []

        @self.bot.event
        async def on_ready():
            log("info", f"Bot connecté en tant que {self.bot.user}")
            self.default_channels = [self.bot.get_channel(int(channel_id)) for channel_id in self.DEFAULT_CHANNEL_IDS]

            for channel in self.default_channels:
                if channel:
                    await channel.send("Bot connecté !")
                else:
                    log("warning", f"Channel '{channel}' non trouvé")
            
            self.repos = self.load_repos()
            self.fetch_log.start()

        @self.bot.command()
        async def ping(ctx) -> None:
            log('info', "Commande !ping reçue")
            await ctx.send("pong")
            log('info', "Réponse \"pong\" envoyée")

        @self.bot.command()
        async def add_channel(ctx, arg: str) -> None:
            name = arg.split('/')[-1]
            url = arg
            repo = self.search_repo(url)
            if not repo:
                repo = Repo(name, url)
                self.repos.append(repo)
            repo.add_channel(ctx.channel)
            
            log("success", f"Channel '{ctx.channel.name}' added to the list of channels to notify for the repo '{repo.name}'.")
            await ctx.send(f"Channel {ctx.channel.name} ajouté à la liste des channels à notifier pour le repo {repo.name}.\nL'url donné n'est pas vérifié, assurez-vous qu'il soit correct.")

            self.save()

        @self.bot.command()
        async def remove_channel(ctx, arg: str) -> None:
            repo = self.search_repo(arg)
            if repo:
                if ctx.channel not in repo.channels:
                    log("warning", f"Channel '{ctx.channel.name}' not found in the list of channels to notify for the repo '{repo.name}'.")
                    await ctx.send(f"Channel {ctx.channel.name} non trouvé dans la liste des channels à notifier pour le repo {repo.name}")
                else:
                    repo.remove_channel(ctx.channel)
                    log("info", f"Channel '{ctx.channel.name}' removed from the list of channels to notify for the repo '{repo.name}'.")
                    await ctx.send(f"Channel {ctx.channel.name} retiré de la liste des channels à notifier")
            else:
                log("warning", f"No repo found with the url '{arg}'")
                await ctx.send("Aucun repo trouvé avec l'url donnée")

            self.save()

        @self.bot.command()
        async def list_channels(ctx, arg: str) -> None:
            name = arg
            if 'http' in arg:
                name = arg.split('/')[-1]
            
            repo = self.search_repo(name, name=True)
            if repo:
                channels = ', '.join([channel.name for channel in repo.channels])
                await ctx.send(f"Channels à notifier pour le repo {repo.name} : {channels}")
                return
            log("warning", f"No repo found with the name '{name}'")
            await ctx.send(f"Aucun repo trouvé avec le nom donné '{name}'")

        @self.bot.command()
        async def verbose(ctx, arg: str) -> None:
            arg = arg.lower()
            if arg == "true":
                if self.VERBOSE:
                    log("info", "Verbose déjà activé")
                    await ctx.send("Verbose déjà activé")
                else:
                    self.VERBOSE = True
                    log("info", "Verbose activé")
                    await ctx.send("Verbose activé")
            elif arg == "false":
                if not self.VERBOSE:
                    log("info", "Verbose déjà désactivé")
                    await ctx.send("Verbose déjà désactivé")
                else:
                    self.VERBOSE = False
                    log("info", "Verbose désactivé")
                    await ctx.send("Verbose désactivé")
            else:
                log("warning", f"Argument invalide: '{arg}'")
                await ctx.send("Argument invalide")

    def load_repos(self):
        datas = load()
        repos = []
        for data in datas['repos']:
            repo = Repo(data['name'], data['url'])
            for channel_id in data['channels']:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    repo.add_channel(channel)
                else:
                    log("warning", f"Channel '{channel_id}' non trouvé")
            repos.append(repo)
        return repos

    def save(self):
        data = {
            "repos": [repo.encode() for repo in self.repos]
        }
        update(data)

    def search_repo(self, string: str, name: bool = False) -> Repo|None:
        for repo in self.repos:
            if name:
                if repo.name == string:
                    return repo
            else:
                if 'api' in string:
                    tmp = repo.url.split('//')
                    new_url = tmp[0] + '//api.' + tmp[1]
                    tmp = new_url.split('.com')
                    new_url = tmp[0] + '.com/repos' + tmp[1]
                else:
                    new_url = repo.url
                if new_url == string:
                    return repo
        return None

    @tasks.loop(seconds=1)  # La tâche sera exécutée toutes les secondes
    async def fetch_log(self) -> None:
        try:
            response = requests.get(self.API_URL)
            data = response.json()

            if 'error' in data:
                match data['error']:
                    case "No logs found":
                        if self.VERBOSE:
                            log("info", "No logs found")
                    case _:
                        log("error", data['error'])
            else:
                message = f"@everyone\nNouveau push sur `{data['repository']}` par `{data['pusher']}`:\n> Commit : [{data['payload']['commits'][-1]['message']}](<{data['payload']['commits'][-1]['url']}>)\n> Branche : `{data['payload']['ref'].split('/')[-1]}`"
                log('info', f"Will send : {message}")

                repo = self.search_repo(data['payload']['repository']['url'])
                for channel in repo.channels:
                    if channel:
                        await channel.send(message)
                        log('success', f"Message sent to {channel.name}")

        except Exception as e:
            log("error", e.__str__())

    def run(self):
        self.bot.run(self.TOKEN)
    
    async def close(self):
        await self.bot.close()
    
if __name__ == "__main__":
    bot = GitBot()
    bot.run()
