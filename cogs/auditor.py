import discord
from discord.ext import tasks, commands
from recorder import serve, unserve, serves
from logger import log
# import sys

# sys.path.insert(1, 'C:\\Users\\Administrator\\Desktop\\gw')


class Auditor(commands.Cog):
  
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    log("Auditor is running")
    # guilds = self.client.guilds
    # serving = [server['server_id'] for server in serves()]

    # for guild in guilds:
    #   server = str(guild)
    #   server_id = guild.id
    #   if server_id not in serving:
    #     serve(server, server_id)
    #     log("Now serving " + str(server_id))
    
    # for guild in [server for server in guilds]:
    #   server = str(guild)
    #   server_id = guild.id
    #   if guild.id not in serving:
    #     unserve(serve, server_id)
    #     log("No longer serving " + str(server_id))
      
  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    server = str(guild)
    server_id = guild.id

    serve(server, server_id)
    log("Now serving " + str(server_id))
    
  @commands.Cog.listener()
  async def on_guild_remove(self, guild):
    server = str(guild)
    server_id = guild.id

    unserve(server, server_id)
    log("No longer serving " + str(server_id))



      
def setup(client):
  client.add_cog(Auditor(client))