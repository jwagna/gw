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


class Watcher(commands.Cog):
  
  def __init__(self, client):
    self.client = client
    
  @commands.Cog.listener()
  async def on_ready(self):
    self.watcher.start()
    log("Watcher is running")

  @tasks.loop(minutes=1)
  async def watcher(self):
    await self.client.wait_until_ready()

    tasks = []
    
    async def watch(session, board):
      front = []

      latest = board['last']
      board_id = board['board_id']
      topics = await aget(session, 'https://geekhack.org/index.php?board=' + str(board_id) + '.0;sort=last_post;desc')
      
      for i in topics.find_all('td', class_='subject windowbg2'):
        topic = i.find('a')['href']
        
        tid = topic[topic.find('topic') + 6:-2]
        front.append(int(tid))
        front.sort()
      
      for i in front:
        if i > latest:
          latest = i
          url = 'https://geekhack.org/index.php?topic=' + str(latest) + '.0'
          
          soup = await aget(session, url)
    
          op = soup.find_all('div', class_='poster')[0]
          op_name = op.find('a').text                
          op_href = 'https://geekhack.org/index.php?action=profile;' + op.find('a')['href'][op.find('a')['href'].find('u='):]

          try:
            op_flair = op.find('li', class_='membergroup').find('img')['src']

          except:
            op_flair = ''

          date = soup.find('div', class_='smalltext').text[7:-2]
          posts = soup.find('li', class_='postcount').text.replace('Posts: ','')
          title = soup.find('div', 'keyinfo').find('a').text

          try:
            image = soup.find_all('a', class_='highslide')[1]['href']
            
          except:
            try:
              image = soup.find_all('a', class_='highslide')[0]['href']
            
            except:
              image = 'https://geekhack.org/Themes/Nostalgia/images/banner.png'

          finally:
            if 'https://geekhack.org/index.php?' in image:
              image = 'https://geekhack.org/index.php?' + image[image.find('action'):]

          
          if "IC" in title:
            color = discord.Colour.dark_orange()

          elif "GB" in title:
            color = discord.Colour.dark_green()

          else:
            color = discord.Colour.dark_gold()

          embed = discord.Embed(
            title = title,
            url = url,
            colour = color
          )

          embed.set_author(name=op_name + ' (' + posts + ')', icon_url=op_flair, url=op_href)     
          embed.set_footer(text="geekhack | " + date, icon_url ='https://i.imgur.com/JEDbZSQ.png')
          embed.set_image(url=image)
    

          if board['to']['channel'] != 0:
            for address in board['to']['channel']:
              try:
                self.channel = self.client.get_channel(address)
                
                try:
                  await self.channel.send(embed=embed)

                except:
                  if 'error code: 50013' in traceback.format_exc():
                    print("A server is missing proper permissions")

              except AttributeError: # UNREACHABLE CHANNEL
                clean('channel', address)


          if board['to']['dm'] != 0:
            for address in board['to']['dm']:
              try:
                user = self.client.get_user(address)
              
                await user.send(embed=embed)
              
              except: # UNREACHABLE USER
                if 'error code: 10013' in traceback.format_exc():
                  clean('dm', address)

          watched(board_id, latest)     

    async with ClientSession() as session:
      for board in watches():
        tasks.append(watch(session, board))

      await asyncio.gather(*tasks)


def setup(client):
  client.add_cog(Watcher(client))