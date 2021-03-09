import discord
from discord.ext import tasks, commands
import traceback
import sys
from bs4 import BeautifulSoup as bs
from recorder import *
from aiohttp import ClientSession
import asyncio 
from handler import aget
from logger import log

sys.path.insert(1, 'C:\\Users\\Administrator\\Desktop\\gw')


class Listener(commands.Cog):
  
  def __init__(self, client):
    self.client = client
    
  @commands.Cog.listener()
  async def on_ready(self):
    self.listener.start()
    log("Listener is running")

  @tasks.loop(minutes=1)
  async def listener(self):
    await self.client.wait_until_ready()
                      
    tasks = []

    ls = [i for i in listens()]
    async def listen(session, topic_id, post):
      inside = await aget(session, 'https://geekhack.org/index.php?topic=' + str(topic_id) + '.' + str(post))

      info = inside.find_all('div', class_='keyinfo')
      
      try:
        page = int(inside.find('div', class_='pagelinks floatleft').contents[-3].text)

      except ValueError:
        page = int(inside.find('div', class_='pagelinks floatleft').contents[-5].text)

      if page != 1:
        pi = (page * 50) - 50

      else:
        pi = 0

      #for i in info[post - pi]: # checks index of last reply on current page 
      for i in info[post - pi:]:  
        response = ""
        # smalltext = (i.find('div', 'smalltext').find('strong').text)
        timestamp = i.find('div', class_='smalltext').text.replace('« ','').replace(' »','')
        reply_num = timestamp[:timestamp.find(' on: ') + 5].replace(' on: ','').replace('Reply ', '')
        date = timestamp[timestamp.find(' on: ') + 5:]
        timestamp = date + ' | ' + reply_num
        # rn = int(smalltext[smalltext.find('#') + 1:smalltext.find('on')]) # SET THIS AS LAST REPLY AT THE END
      
        # op = i.find_parent('div', class_='post_wrapper').find('div', class_='poster').find('a').text

        msg = i.find('h5').find('a')['href']
        msgn = msg[msg.find('#') + 1:]
        msg_href = 'https://geekhack.org/index.php?topic=' + str(topic_id) + '.' + msgn + '#' + msgn
        if i.find_parent('div', class_='post_wrapper').find('div', class_='poster').find('li', class_='threadstarter') is not None: # check for op
          
          text = i.find_parent('div', class_='post_wrapper').find('div', class_='inner')
          temp_reply_list = []
          
          for q in text.find_all('blockquote'): # REMOVE QUOTES
            q.decompose()
            
          for x in text.find_all('div', class_='topslice_quote'): # FIND REPLIED TO
            c = x.extract()
            
            q = c.text

            temp_reply_list.append(q[12:q.find('on') - 1])
          
          if len(temp_reply_list) != 0:  
            quoted = ' & '.join(set(temp_reply_list))

          else:
            quoted = ''

          for m in text.strings:
            response += m + '\n\n'
          
          try:
            image = i.find_parent('div', class_='post_wrapper').find('a', class_='highslide')['href']

            if image is None:
              image = ''

          except:
            image = ''   

          try:
            op_icon = i.find_parent('div', class_='post_wrapper').find('li', class_='avatar').find('img', class_='avatar')['src']

            if op_icon is None:
              op_icon = ''

          except:
            op_icon = ''

          op_score = i.find_parent('div', class_='post_wrapper').find('li', class_='postcount').text.replace('Posts: ','')

          if len(temp_reply_list) != 0:
            kind = "Response to " + quoted 
          
          else:
            kind = "Direct Post"

          op_name = i.find_parent('div', class_='post_wrapper').find('div', class_='poster').find('a').text
      
      # embed = discord.Embed(
      #   title = topic,
      #   url = topic_href,
      #   description = f'[{kind}]({msg_href})' + '\n' + response,
      #   colour = discord.Colour.greyple()
      # )

      
      embed = discord.Embed(
        title = kind,
        url = msg_href,
        #description = response + '\n\n' + f'[{topic}]({topic_href})',
        description = response,
        colour = discord.Colour.greyple()
      )
    
      embed.set_author(name=topic + '\n' + op_name + ' (' + op_score + ')', icon_url=op_icon, url=topic_href)     
      embed.set_footer(text="geekhack | " + timestamp, icon_url ='https://i.imgur.com/JEDbZSQ.png')
      embed.set_image(url=image)

      channels = listed['to']['channel']
      dms = listed['to']['dm']

      if channels != 0:
        for address in channels:
          try:
            channel = self.client.get_channel(address)

            await channel.send(embed=embed)                 

          except AttributeError: # UNREACHABLE CHANNEL
            clean('channel', address)
      
      if dms != 0:
        for address in dms:
          try:
            
            user = self.client.get_user(address)
            
            await user.send(embed=embed)
            
          except: # UNREACHABLE USER
            if 'error code: 10013' in traceback.format_exc():
              clean('dm', address)

      listened(topic_id, post)
            
        # except:
      #   pass

    async with ClientSession() as session:
      front = await aget(session, 'https://geekhack.org/index.php?action=recenttopics')
      
      for l in front.select('tr[class*="windowbg"]')[::-1]:
        t = l.find_all('a')[2]['href']
        tin = t.find('topic') + 6
        op = l.find_all('a')[4]['href']
        lp = l.find_all('a')[1]['href']

        topic = l.find_all('a')[2].text
        topic_id = int(t[tin:][:t[tin:].find('.')])
        topic_href = 'https://geekhack.org/index.php?topic=' + str(topic_id)
        op_id = int(op[op.find('u=') + 2:])
        poster_id = int(lp[lp.find('u=') + 2:])
        op_href = 'https://geekhack.org/index.php?action=profile;u=' + str(poster_id)
        post = int(l.find_all('td', class_='smalltext')[1].text)

        if post == 0:
          continue

        if topic_id in [i['topic_id'] for i in ls]:
          listed = [i for i in ls if i['topic_id'] == topic_id][0]
          
          if post != listed['last']:
            listened(topic_id, post)

            if poster_id != op_id:
              continue

            else: 
              tasks.append(listen(session, topic_id, post))

      await asyncio.gather(*tasks)



def setup(client):
  client.add_cog(Listener(client))