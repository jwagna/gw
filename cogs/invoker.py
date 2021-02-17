import discord
from discord.ext import commands
import traceback
import sys
from embedder import *
from recorder import *
from scraper import *
from logger import log

sys.path.append('..')
sys.path.insert(1, '/home/jwagna/Documents/gw')


class Invoker(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    log("Invoker is running")

  @commands.command()
  async def gw(self, ctx, *kw):
    # if ctx.author.id != 15701257819376844:
    #   return
      
    kw = ' '.join(kw[:]).split(' ') # parse command
    call = kw[0].lower() # initial command

    user_id = ctx.author.id

    avatar = ctx.author.avatar_url

    def isDM():
      return isinstance(ctx.channel, discord.channel.DMChannel)

    def isAdmin():
      return ctx.author.guild_permissions.administrator
    
    def isUnrestricted():
      return unrestricts(ctx.guild.id, ctx.channel.id)

    def server(cid):
      try:
        return self.client.get_channel(cid).guild.id

      except AttributeError:
        pass

    def enumerator(following):
      topics = following['topics']
      boards = following['boards']

      index = 0

      def indexer():
        nonlocal index
        index += 1
        return index
      
      followed_topics = '\n'.join([f"[[ {indexer()} ]](https://discord.com/channels/{server(l['address'])}/{l['address']}) [{l['topic']}](https://geekhack.org/index.php?topic={l['topic_id']}.0)" if server(l['address']) is not None else f"[ {indexer()} ] [{l['topic']}](https://geekhack.org/index.php?topic={l['topic_id']}.0)" for l in topics])
        
      followed_boards = '\n'.join([f"[[ {indexer()} ]](https://discord.com/channels/{server(l['address'])}/{l['address']}) [{l['board']}](https://geekhack.org/index.php?board={l['board_id']}.0)" if server(l['address']) is not None else f"[ {indexer()} ] [{l['board']}](https://geekhack.org/index.php?board={l['board_id']}.0)" for l in boards])

      return followed_topics, followed_boards

    async def send(message):
      if isDM() is False:
        try:
          await ctx.message.delete()

        except:
          if 'error code: 50013' in traceback.format_exc(): # MANAGE MESSAGE PERM IS DISABLED (THIS IS FINE)
            pass

      if call in ["following", "watching", "help", "commands", "unfollow", "unwatch", "invite"]:
        await ctx.author.send(embed=message)

      else:
          
        try:
          await ctx.channel.send(embed=message)

        except:
          if 'error code: 50013' in traceback.format_exc():
            # user = self.client.get_user(user_id)
            
            # await user.send(embed=message)
           #  await ctx.author.send(error("Unable to reach"))
            print("A server is missing proper permissions [SEND MESSAGES]") # FIGURE OUT A WAY TO FAIL GRACEFULLY

    if isDM():
      address = user_id

    else:
      address = ctx.channel.id

    if isDM() is False:
      if isAdmin() is False:
        if isUnrestricted() is False:
          return await send(error("No permission"))


    if call not in ["follow", "following", "unfollow", "watch", "watching", "unwatch", "help", "commands", "unrestrict", "restrict", "detach", "invite"]:
      return await send(error("Unrecognized command"))

    try:
      if call == "follow" or call == "watch":
        response = verify(kw[1])

        if response == 404: # bad link
          return await send(error("Could not locate topic or board"))

        elif response == 503: # server dead
          return await send(error("Connection error"))

        else:
          if len(response) == 9:
            topic, topic_id, date, op_name, op_id, op_flair, op_icon, op_score, image = response

            if isDM() is False:
              if any(channel in listen_dupe(topic_id) for channel in [channel.id for channel in ctx.guild.text_channels]):
                return await send(error("Already followed within this server"))

            if len(follows(user_id)['topics']) < 10: 
              if follow(user_id, topic, topic_id, address, response):
                return await send(message("Now following", response, avatar))

              else:
                return await send(message("Already being followed", response, avatar))

            else:
              return await send(max_error(call, enumerator(call), avatar))

          elif len(response) == 2:
            board, board_id = response

            if isDM() is False:
              if any(channel in watch_dupe(board_id) for channel in [channel.id for channel in ctx.guild.text_channels]):
                return await send(error("Already being watched within this server"))

            if len(follows(user_id)['boards']) < 10:
              if follow(user_id, board, board_id, address, response):
                return await send(message("Now watching", response, avatar))

              else:
                return await send(message("Already being watched", response, avatar))

            else:
              return await send(max_error(call, enumerator(call), avatar))


      elif call == "unfollow" or call == "unwatch": # removing from follow list
        response = unfollow(user_id, kw[1])
        if response:
          if kw[1] == "all":
            #return await send(removed("You are no longer following any topics", response, avatar))
            return await send(followlist(enumerator(follows(user_id)), avatar))

          else:
            return await send(removed("No longer following", response, avatar))

        else:
          return await send(error("Bad index!"))

      elif call == "following" or call == "watching": # list all follows
        return await send(followlist(enumerator(follows(user_id)), avatar))

      elif call == "unrestrict":
        if isDM():
          return await send(error("This command is limited to text channels within servers"))

        if isAdmin() is False:
          return await send(error("This command is limited to admins only"))

        if isUnrestricted() is not False:
          return await send(gatekeep("Channel is already unresticted"))

        await send(gatekeep("WARNING"))

        def validate(message):
          return message.content.lower() == "unrestrict" and message.author == ctx.author
        
        await self.client.wait_for('message', check=validate)

        
        if unrestrict(ctx.guild.id, address):
          return await send(gatekeep("Channel has been unrestricted"))

        else:
          return await send(gatekeep("Channel is already unresticted"))

      elif call == "restrict":
        if isDM():
          return await send(error("This command is limited to text channels within servers"))

        if isAdmin() is False:
          return await send(error("This command is limited to admins only"))
          
        if restrict(ctx.guild.id, address) is False:
          return await send(gatekeep("Channel is already restricted"))
          
        else:
          return await send(gatekeep("Channel has been restricted"))

      elif call == "detach":
        if isDM() is False:
          if isAdmin() is False:
            return await send(error("This command is limited to admins only"))
          
          await send(gatekeep("channel"))

          def validate(message):
            return message.content.lower() == "detach" and message.author == ctx.author

          await self.client.wait_for('message', check=validate)

          clean('channel', address)

          return await send(gatekeep("Address has been detached"))

        else:
          await send(gatekeep("dm"))

          def validate(message):
            return message.content == "detach" and message.author == ctx.author

          await self.client.wait_for('message', check=validate)

          clean('dm', address)

          return await send(gatekeep("Address has been detached"))

        
      elif call == "help" or call == "commands":
        return await send(commandlist())


      elif call == "invite":
        return await send(invite())

    except IndexError:
      return await send(error("Please include a valid topic/board url or number after the command"))


def setup(client):
  client.add_cog(Invoker(client))
