import discord

def error(mt):
  if mt == "No permission":
    
    body = "You do not have permissions to call this command"

  elif mt == "Unrecognized command":
    body = "Send `.gw help` to view the available commands"

  elif mt == "Already followed within this server":
    body = "This topic is already being followed within this server"

  elif mt == "You are currently not following any topics":
    body = "Send `.gw follow url/topic` to follow a topic"

  elif mt == "You are currently not watching any boards":
    body = "Send `.gw watch url/board` to watch a board"

  elif mt == "You are no longer following any topics":
    body = "Send `.gw follow url/topic` to follow a topic"

  elif mt == "Bad index!":
    body = "Check the indices of your list with `.gw following`"

  elif mt == "Already being watched within this server":
    body = "This board is already being watched within this server"

  elif mt == "Connection error":
    body = "[geekhack servers may be down](https://geekhack.org/)"

  elif mt == "This command is limited to text channels within servers":
    body = ""

  elif mt == "This command is limited to admins only":
    body = ""

  elif mt == "The command you called requires another parameter":
    body = ""

  elif mt == "Could not locate topic or board":
    body = "Send `.gw follow ` along with a valid link or number"

  elif mt == "Please include a valid topic/board url or number after the command":
    body = ""
    
  embed = discord.Embed(
    title = mt,
    description = body,
    colour = discord.Color.red()
  )

  return embed



def watchlist(l, avatar):
  embed = discord.Embed(
    description = l,
    colour = discord.Colour.blurple()
  )
  embed.set_author(name="Currently watching", icon_url=avatar)
  return embed

def message(check, response, avatar):
  if "follow" in check:
    topic = response[0]
    topic_id = response[1]
    date = response[2]
    op_name = response[3]
    op_id = response[4]
    op_href = 'https://geekhack.org/index.php?action=profile;u=' + str(op_id)
    op_flair = response[5]
    op_icon = response[6]
    op_score = response[7]
    image = response[8]
    
    if check == "Now following":
      embed = discord.Embed(
        title = topic,
        description = "Responses from **" + op_name + "** will be sent to this channel",
        # description = "You will now receive post notifications whenever " + op_name + " replies within the topic",
        url = f'https://geekhack.org/index.php?topic={topic_id}.0',
        colour = discord.Colour.blurple()
      )

      embed.set_thumbnail(url=op_icon)
      embed.set_image(url=image)
      embed.set_author(name="Now following: " + f'{op_name} ({op_score})', url=op_href, icon_url=avatar
      )
      
      embed.set_footer(text="geekhack | " + date, icon_url ='https://i.imgur.com/JEDbZSQ.png')

    elif check == "Already being followed":
      embed = discord.Embed(
        title = topic,
        url = f'https://geekhack.org/index.php?topic={topic_id}.0',
        colour = discord.Colour.red()
      )
      embed.set_author(name="This topic is already being followed here")

  elif "watch" in check:
    board = response[0]
    board_id = response[1]

    if check == "Now watching":
      embed = discord.Embed(
        title = board,
        description = "New submissions to **" + board + "** will now be sent to this channel",
        url = f'https://geekhack.org/index.php?board={board_id}.0',
        colour = discord.Colour.blurple()
      )

      embed.set_author(name="Now following", icon_url=avatar)
      embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

    elif check == "Already being watched":
      embed = discord.Embed(
        title = board,
        url = f'https://geekhack.org/index.php?board={board_id}.0',
        colour = discord.Colour.red()
      )
      embed.set_author(name="This board is already being followed here")

  

  return embed


def max_error(call, l, avatar):
  if "follow" in call:
    embed = discord.Embed(
      description = l + '\n\n' +
      "Send `.gw unfollow #` to remove a topic from your list or `.gw unfollow all` to clear",
      colour = discord.Colour.red()
    )

    embed.set_author(name="You are already following the maximum number of 10 topics", icon_url=avatar)

  elif "watch" in call:
    embed = discord.Embed(
      description = l + '\n\n' +
      "Send `.gw unwatch #` to remove a board from your list or `.gw unwatch all` to clear",
      colour = discord.Colour.red()
    )

    embed.set_author(name="You are already watching the maximum number of 10 boards", icon_url=avatar)
  
  return embed

def removed(l, res, avatar):
  if l == "No longer following":
    topic = res[0]
    topic_id = res[1]

    embed = discord.Embed(
      title = topic,
      url = f'https://geekhack.org/index.php?topic={topic_id}.0',
      # description = 
      colour = discord.Colour.red()
    )

    embed.set_author(name="No longer following", icon_url=avatar)

  elif l == "No longer watching":
    board = res[0]
    board_id = res[1]
    embed = discord.Embed(
      title = board,
      url = f'https://geekhack.org/index.php?board={board_id}.0',
      # description = 
      colour = discord.Colour.red()
    )

    embed.set_author(name="No longer watching", icon_url=avatar)
  
  elif l == "No longer following2":
    removed = res[0]
    removed_id = res[1]
    if removed_id >= 10000:
      url = 'https://geekhack.org/index.php?topic='

    else:
      url = 'https://geekhack.org/index.php?board='

    embed = discord.Embed(
      title = removed,
      url = f'{url}{removed_id}.0',
      # description = 
      colour = discord.Colour.red()
    )

    embed.set_author(name="No longer following2", icon_url=avatar)

  elif l == "You are no longer watching any boards":
    embed = discord.Embed(
      description = "Send `.gw watch url/board` to watch a board",
      colour = discord.Colour.red()
    )

    embed.set_author(name="You are no longer watching any boards", icon_url=avatar)

  elif l == "You are no longer following any topics":
    embed = discord.Embed(
      description = "Send `.gw follow url/topic` to follow a topic",
      colour = discord.Colour.red()
    )

    embed.set_author(name="You are no longer following any topics", icon_url=avatar)
  return embed


def gatekeep(msg):
  if msg == "WARNING":
    embed = discord.Embed(
      title = "WARNING",
      description = "You are attempting to unrestrict this channel which will allow anyone with send permissions to call any non-admin command. \n\n **THIS FEATURE IS INTENDED FOR SMALLER PERSONAL SERVERS.** \n\n If you would like to proceed, respond with `unrestrict`",
      colour = discord.Colour.red()
    )

  elif msg == "Channel has been unrestricted":
    embed = discord.Embed(
      title = "Channel has been unrestricted",
      description = "You can revoke this at any time with `.gw restrict`",
      colour = discord.Colour.dark_green()
    )

  elif msg == "Channel is already unresticted":
    embed = discord.Embed(
      title = "Channel is already unresticted",
      description = "You can revoke this at any time with `.gw restrict`",
      colour = discord.Colour.light_grey()
    )

  elif msg == "Channel has been restricted":
    embed = discord.Embed(
      title = "Channel has been restricted",
      colour = discord.Colour.dark_red()
    )

  elif msg == "Channel is already restricted":
    embed = discord.Embed(
      title = "Channel is already restricted",
      colour = discord.Colour.dark_red()
    )
  elif msg == "channel":
    embed = discord.Embed(
      title = "WARNING",
      description = "You are attempting to detach this address which will remove any follow or watch (including other users') associated to this channel.\n\nIf you would like to proceed, respond with `detach`",
      colour = discord.Colour.red()
    )

  elif msg == "Address has been detached":
    embed = discord.Embed(
      title = "Address has been detached",
      colour = discord.Colour.dark_red()
    )
    
  elif msg == "dm":
    embed = discord.Embed(
      title = "WARNING",
      description = "You are attempting to detach this address which will remove any follow or watch associated to your direct messages.\n\nIf you would like to proceed, respond with `detach`",
      colour = discord.Colour.red()
    )
  return embed


def commandlist():
  embed = discord.Embed(
    title = "All Commands",
    description = "\n\n```.gw follow url/topic/board```\n" + "Follow a topic for post notifications or a board for newly posted topics" +
    "\n\n```.gw following```\n" + "Returns your current follow list" +
    "\n\n```.gw unfollow #```\n" + "Unfollow a topic or board using an index provided by .gw following" +
    "\n\n```.gw unfollow all```\n" + "Unfollow all topics and boards" +
    "\n\n```.gw help```\n" + "Returns the commands list" +
    "\n\n```.gw invite```\n" + "Returns an invite link for the bot" + 
    '\n\n' + "__**ADMIN ONLY**__" +
    "\n\n```.gw unrestrict```\n" + "Lifts restrictions within a channel, allowing any user to call non-admin commands" +
    "\n\n```.gw restrict```\n" + "Restricts channel, disallowing non-admins to call any command (all channels are restricted by default)" +
    "\n\n```.gw detach```\n" + "Removes all instances of channel from every list, including from other users (this can also be called via DM)", 
    colour = discord.Colour.gold()
  )

  return embed



def followlist(l, avatar):
  topics = l[0]
  boards = l[1]

  if len(topics) == 0:
    topics = "None"

  if len(boards) == 0:
    boards = "None"

  embed = discord.Embed(
    colour = discord.Colour.blurple()
  )

  embed.set_author(name="Currently following", icon_url=avatar)
  embed.add_field(name="__Topics__", value=topics, inline= True)
  embed.add_field(name="__Boards__", value=boards, inline= True)

  if topics =="None" and boards == "None":
    embed.add_field(name="Want to get started?", value="Send `.gw follow ` along with a valid topic/board number or url", inline= False)

    embed.add_field(name="Need help?", value="Send `.gw help` for a full list of commands", inline= False)

  embed.set_footer(text="geekhack", icon_url ='https://i.imgur.com/JEDbZSQ.png')

  return embed


def invite():
  embed = discord.Embed(
    title = "Click to invite me into one of your servers!",
    url= "https://discord.com/oauth2/authorize?client_id=772690211792224256&permissions=10240&scope=bot",
    colour = discord.Colour.green()
  )
  return embed