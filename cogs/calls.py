import discord
from discord.ext import commands
import traceback
import sys

from mongo import id_iter, follow, follows, unfollow, watch, watches, unwatch, restrict, unrestrict, unrestricts, clean, scan_dupe, listen_dupe
from scrape import board_check, pull

sys.path.append('..')
sys.path.insert(1, 'C:\\Users\\Administrator\\Desktop\\gw')


class Calls(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def gw(self, ctx, *kw):

    kw = ' '.join(kw[:]).split(' ') # parse command
    call = kw[0].lower() # initial command

    user_id = ctx.message.author.id

    if isinstance(ctx.channel, discord.channel.DMChannel) is False: # check for restrictions
      if unrestricts(ctx.message.guild.id) is False:
        if ctx.message.author.guild_permissions.administrator:
          pass

        else:
          embed = discord.Embed(
            title = "You do not have permissions to call this command",
            colour = discord.Colour.red()
          )

          #await ctx.message.delete()
          await ctx.channel.send(embed=embed)

          return

      else:
        if ctx.message.channel.id in unrestricts(ctx.message.guild.id):
          pass

        # else:
        #   embed = discord.Embed(
        #     title = "You do not have permissions to call this command",
        #     colour = discord.Colour.red()
        #   )

        #   await ctx.message.delete()

        #   await ctx.channel.send(embed=embed)

        #   return


    if isinstance(ctx.channel, discord.channel.DMChannel): # calld via dm
      address = int(user_id)

    else: # calld via channel
      address = int(ctx.message.channel.id)

    if call not in ["follow", "following", "unfollow", "watch", "watching", "unwatch", "help", "unrestrict", "restrict", "detach"]:
      embed = discord.Embed(
        title = "Unrecognized command",
        description = "Send `.gw help` to view the available commands",
        colour = discord.Colour.red()
      )
      await ctx.channel.send(embed=embed)

      return

    try:
      if call == "follow": # adding a follow
        topic, topic_id, date, op_name, op_id, op_href, op_flair, op_icon, op_score, image = pull(kw[1])

        if topic_id:
          for c in listen_dupe(topic_id):
            if isinstance(ctx.channel, discord.channel.DMChannel) is False:
              if c not in [c.id for c in ctx.guild.text_channels]:
                pass

              else:
                embed = discord.Embed(
                  description = "This topic is already being followed within this server",
                  colour = discord.Colour.red()
                )
                # embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

            else:
              pass

            if len(follows(user_id)) < 10:
              if follow(user_id, topic, topic_id, address):
                embed = discord.Embed(
                  title = topic,
                  url = f'https://geekhack.org/index.php?topic={topic_id}.0',
                  # description = "**Published:** " + date,
                  colour = discord.Colour.blurple()
                )
                embed.set_thumbnail(url=op_icon)
                embed.set_image(url=image)
                embed.set_footer(text="geekhack | " + date, icon_url ='https://i.imgur.com/JEDbZSQ.png')
                embed.set_author(name="Now following: " + f'{op_name} ({op_score})', url=op_href, icon_url=ctx.message.author.avatar_url)

              else:
                embed = discord.Embed(
                  title = topic,
                  url = f'https://geekhack.org/index.php?topic={topic_id}.0',
                  # description = "**Published:** " + date,
                  colour = discord.Colour.red()
                )
                embed.set_author(name="This thread is already being followed here", icon_url=ctx.message.author.avatar_url)

            else:
              embed = discord.Embed(
                description = ('\n'.join(['**(' + str(c + 1) + ')** [' + p['topic'] + '](https://geekhack.org/index.php?topic=' + str(p['topic_id']) + '.0)' for c, p in enumerate(follows(user_id))])) + '\n\n' +
                "Send `.gw unfollow #` to remove a thread from your list or `.gw unfollow all` to clear",
                colour = discord.Colour.red()
              )

              embed.set_author(name="You are already following the maximum number of 10 threads", icon_url=ctx.message.author.avatar_url)



              # embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

          # else:
          #   embed = discord.Embed(
          #     description = "This topic is already being followed within this server",
          #     colour = discord.Colour.red()
          #   )
          #   embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')



        # except TypeError: # bad link
        else: # bad link
          embed = discord.Embed(
            description = "Send `.gw follow` along with a valid link or topic number",
            colour = discord.Colour.red()
          )

          embed.set_author(name="Could not locate thread", icon_url=ctx.message.author.avatar_url)
          # embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')


      elif call == "following": # list all follows
        try:
          if len(follows(user_id)) != 0:
            embed = discord.Embed(
              description = ('\n'.join(['**(' + str(c + 1) + ')** [' + p['topic'] + '](https://geekhack.org/index.php?topic=' + str(p['topic_id']) + '.0)' for c, p in enumerate(follows(user_id))])),
              colour = discord.Colour.blurple()
            )
            embed.set_author(name="Currently following", icon_url=ctx.message.author.avatar_url)

          else:
            raise TypeError

        except TypeError:
          embed = discord.Embed(
            description = "Send `.gw follow url/topic` to follow a thread",
            colour = discord.Colour.blurple()
          )
          embed.set_author(name="You are currently not following any threads", icon_url=ctx.message.author.avatar_url)
        #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

        #await ctx.channel.send(embed=embed)


      elif call == "unfollow": # removing from follow list

        if unfollow(user_id, kw[1]):
          if len(follows(user_id)) != 0:
            embed = discord.Embed(
              description = ('\n'.join(['**(' + str(c + 1) + ')** [' + p['topic'] + '](https://geekhack.org/index.php?topic=' + str(p['topic_id']) + '.0)' for c, p in enumerate(follows(user_id))])),
              colour = discord.Colour.blurple()
            )
            embed.set_author(name="Now following", icon_url=ctx.message.author.avatar_url)

          else:
            embed = discord.Embed(
              description = "Send `.gw follow url/topic` to follow a thread",
              colour = discord.Colour.blurple()
            )
            embed.set_author(name="You are no longer following any threads", icon_url=ctx.message.author.avatar_url)
          #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

          #await ctx.channel.send(embed=embed)

        else:
          embed = discord.Embed(
            title = "Bad index!",
            description = "Check the indices of your list with `.gw following`",
            colour = discord.Colour.red()
          )


      elif call == "watch":
        board, board_id = board_check(kw[1])

        if board_id:
          for c in scan_dupe(board_id):
            if isinstance(ctx.channel, discord.channel.DMChannel) is False:
              if c not in [c.id for c in ctx.guild.text_channels]:
                pass

              else:
                embed = discord.Embed(
                  description = "This board is already being watched within this server",
                  colour = discord.Colour.red()
                )
                #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

            else:
              pass

            if len(watches(user_id)) < 10:
              if watch(user_id, board, board_id, address):
                embed = discord.Embed(
                  title = board,
                  url = f'https://geekhack.org/index.php?board={board_id}.0',
                  # description = "**Published:** " + date,
                  colour = discord.Colour.blurple()
                )
                embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')
                embed.set_author(name="Now watching")


              else:
                embed = discord.Embed(
                  title = board,
                  url = f'https://geekhack.org/index.php?board={board_id}.0',
                  # description = "**Published:** " + date,
                  colour = discord.Colour.red()
                )
                embed.set_author(name="This board is already being watched here", icon_url=ctx.message.author.avatar_url)

            else:
              embed = discord.Embed(
                description = ('\n'.join(['**(' + str(c + 1) + ')** [' + p['board'] + '](https://geekhack.org/index.php?board=' + str(p['board_id']) + '.0)' for c, p in enumerate(watches(user_id))])) + '\n\n' +
                "Send `.gw unwatch #` to remove a thread from your list or `.gw unwatch all` to clear",
                colour = discord.Colour.red()
              )

              embed.set_author(name="You are already watching the maximum number of 10 boards", icon_url=ctx.message.author.avatar_url)
                #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')
              #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

            # else:
            #   embed = discord.Embed(
            #     description = "This board is already being watched within this server",
            #     colour = discord.Colour.red()
            #   )
            #   embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')




        else:
        # except TypeError: # bad link
          embed = discord.Embed(
            description = "Send `.gw watch` along with a valid link or board number",
            colour = discord.Colour.red()
          )

          embed.set_author(name="Could not locate board", icon_url=ctx.message.author.avatar_url)
          #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

      elif call == "watching": # list all follows
        try:
          if len(watches(user_id)) != 0:
            embed = discord.Embed(
              description = ('\n'.join(['**(' + str(c + 1) + ')** [' + p['board'] + '](https://geekhack.org/index.php?board=' + str(p['board_id']) + '.0)' for c, p in enumerate(watches(user_id))])),
              colour = discord.Colour.blurple()
            )
            embed.set_author(name="Currently watching", icon_url=ctx.message.author.avatar_url)
          else:
            raise TypeError

        except TypeError:
          embed = discord.Embed(
            description = "Send `.gw watch url/board` to follow a thread",
            colour = discord.Colour.red()
          )
          embed.set_author(name="You are currently not watching any boards", icon_url=ctx.message.author.avatar_url)
        #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')


      elif call == "unwatch":
        if unwatch(user_id, kw[1]):
          if len(watches(user_id)) != 0:
            embed = discord.Embed(
              description = ('\n'.join(['**(' + str(c + 1) + ')** [' + p['board'] + '](https://geekhack.org/index.php?board=' + str(p['board_id']) + '.0)' for c, p in enumerate(watches(user_id))])),
              colour = discord.Colour.blurple()
            )
            embed.set_author(name="Now watching", icon_url=ctx.message.author.avatar_url)

          else:
            embed = discord.Embed(
              description = "Send `.gw watch url/topic` to watch a board",
              colour = discord.Colour.blurple()
            )
            embed.set_author(name="You are no longer watching any boards", icon_url=ctx.message.author.avatar_url)
          #embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

          #await ctx.channel.send(embed=embed)

        else:
          embed = discord.Embed(
            title = "Bad index!",
            description = "Check the indices of your list with `.gw watching`",
            colour = discord.Colour.red()
          )


      elif call == "unrestrict":
        if isinstance(ctx.channel, discord.channel.DMChannel) is False:
          if ctx.message.author.guild_permissions.administrator:
            await ctx.message.delete()
            embed = discord.Embed(
              title = "WARNING",
              description = "You are attempting to unrestrict this channel which will allow anyone with send permissions to call any non-admin command. \n\n **THIS FEATURE IS INTENDED FOR SMALLER PERSONAL SERVERS.** \n\n If you would like to proceed, respond with `open gate`",
              colour = discord.Colour.red()
            )

            await ctx.channel.send(embed=embed)

            def check(m):
              return m.content.lower() == "open gate" and m.author == ctx.message.author

            await self.client.wait_for('message', check=check)

            if unrestrict(ctx.message.guild.id, ctx.message.channel.id):

              embed = discord.Embed(
                title = "Channel has been unrestricted",
                description = "You can revoke this at any time with `.gw restrict`",
                colour = discord.Colour.dark_green()
              )

            else:
              embed = discord.Embed(
                title = "Channel is already unresticted",
                description = "You can revoke this at any time with `.gw restrict`",
                colour = discord.Colour.light_grey()
              )

            await ctx.channel.send(embed=embed)

            return

          else:
            embed = discord.Embed(
              title = "This command is limited to admins only",
              colour = discord.Colour.red()
            )

        else:
            embed = discord.Embed(
              title = "This command is limited to text channels within servers",
              colour = discord.Colour.red()
            )

      elif call == "restrict":
        if isinstance(ctx.channel, discord.channel.DMChannel) is False:
          if ctx.message.author.guild_permissions.administrator:
            if restrict(ctx.message.guild.id, ctx.message.channel.id):
              embed = discord.Embed(
                title = "Channel has been restricted",
                colour = discord.Colour.dark_red()
              )

            else:
              embed = discord.Embed(
                title = "Channel is already restricted",
                colour = discord.Colour.dark_red()
              )

          else:
            embed = discord.Embed(
              title = "This command is limited to admins only",
              colour = discord.Colour.red()
            )

        else:
            embed = discord.Embed(
              title = "This command is limited to text channels within servers",
              colour = discord.Colour.red()
            )

      elif call == "detach":

        if isinstance(ctx.channel, discord.channel.DMChannel) is False:
          if ctx.message.author.guild_permissions.administrator:
            await ctx.message.delete()
            embed = discord.Embed(
              title = "WARNING",
              description = "You are attempting to detach this address which will remove any follow or watch (including other users') associated to this channel.\n\nIf you would like to proceed, respond with `detach`",
              colour = discord.Colour.red()
            )

            await ctx.channel.send(embed=embed)

            def check(m):
              return m.content.lower() == "detach" and m.author == ctx.message.author

            await self.client.wait_for('message', check=check)

            clean('channel', address)

            embed = discord.Embed(
              title = "Address has been detached",
              colour = discord.Colour.dark_red()
            )

            await ctx.channel.send(embed=embed)

            return

          else:
            embed = discord.Embed(
              title = "This command is limited to admins only",
              colour = discord.Colour.red()
            )

        else:

          embed = discord.Embed(
            title = "WARNING",
            description = "You are attempting to detach this address which will remove any follow or watch associated to your direct messages.\n\nIf you would like to proceed, respond with `Yes`",
            colour = discord.Colour.red()
          )

          await ctx.channel.send(embed=embed)

          def check(m):
            return m.content == "Yes" and m.author == ctx.message.author

          await self.client.wait_for('message', check=check)

          clean('dm', address)

          embed = discord.Embed(
            title = "Address has been detached",
            colour = discord.Colour.dark_red()
          )

          await ctx.channel.send(embed=embed)

          return


      elif call == "help":
        embed = discord.Embed(
          title = "All Commands",
          description = "\n\n```.gw follow url/topic```\n" + "Follow a thread to receive notifications for new posts made by the thread starter" +
          "\n\n```.gw following```\n" + "Returns your followed threads with indices" +
          "\n\n```.gw unfollow #```\n" + "Unfollow a thread using an index provided by .gw following" +
          "\n\n```.gw unfollow all```\n" + "Unfollow all threads" +
          "\n\n```.gw watch url/board```\n" + "Watch a board to receive notifications for newly posted threads" +
          "\n\n```.gw watching```\n" + "Returns your watched boards with indices" +
          "\n\n```.gw unwatch #```\n" + "Unwatch a board using an index provided by .gw watching" +
          "\n\n```.gw unwatch all```\n" + "Unwatch all boards" +
          "\n\n```.gw help```\n" + "Returns the commands list" +
          '\n\n' + "__**ADMIN ONLY**__" +
          "\n\n```.gw unrestrict```\n" + "Lifts restrictions within a channel, allowing any user to call non-admin commands" +
          "\n\n```.gw restrict```\n" + "Restricts channel, disallowing non-admins to call any command (all channels are restricted by default)" +
          "\n\n```.gw detach```\n" + "Removes all instances of channel from every list, including from other users (this can also be called via DM)",
          colour = discord.Colour.gold()
        )

      try:
        if isinstance(ctx.channel, discord.channel.DMChannel) is False:
          await ctx.message.delete()

      except:
        pass

      await ctx.channel.send(embed=embed)

    except IndexError:
      embed = discord.Embed(
        title = "The command you called requires another parameter",
        colour = discord.Colour.red()
      )

      await ctx.channel.send(embed=embed)


def setup(client):
  client.add_cog(Calls(client))
