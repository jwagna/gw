import discord
from discord.ext import tasks, commands
import traceback
import sys
from requests import get
from bs4 import BeautifulSoup as bs

from mongo import serve, unserve, scans, scanned, clean, listens, listened, res

sys.path.insert(1, 'C:\\Users\\Administrator\\Desktop\\gw')


class Start(commands.Cog):
  
  def __init__(self, client):
    self.client = client
    
  @commands.Cog.listener()
  async def on_ready(self):
    self.scan.start()
    self.listen.start()
    print("Good")
    

  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    serve(str(guild), guild.id)
    
  @commands.Cog.listener()
  async def on_guild_remove(self, guild):
    unserve(str(guild), guild.id)


  @tasks.loop(minutes=1)
  async def scan(self):
    await self.client.wait_until_ready()

    for board in scans():
      front = []

      latest = board['topic_id']
      board_id = board['board_id']
      r = get('https://geekhack.org/index.php?board=' + str(board_id) + '.0;sort=last_post;desc')
      soup = bs(r.text, 'lxml')
      
      for i in soup.find_all('td', class_='subject windowbg2'):
        topic = i.find('a')['href']
        
        tid = topic[topic.find('topic') + 6:-2]
        front.append(int(tid))
        front.sort()
      
      for i in front:
        if i > latest:
          latest = i
          url = 'https://geekhack.org/index.php?topic=' + str(latest) + '.0'
          print(r.url, i)
          
          r = get(url)
          soup = bs(r.text, 'lxml')
    
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

          # if board['to']['channel'] != 0:
          #   for a in board['to']['channel']:
            
          #     self.channel = self.client.get_channel(a)

          #     await self.channel.send(embed=embed)



          # if board['to']['dm'] != 0:
          #   for a in board['to']['dm']:
            
          #     user = await self.client.fetch_user(a)
            
          #     await user.send(embed=embed)
              
 
          if board['to']['channel'] != 0:
            for a in board['to']['channel']:
              try:
                self.channel = self.client.get_channel(a)

                await self.channel.send(embed=embed)

              except AttributeError: # UNREACHABLE CHANNEL
                clean('channel', a)


          if board['to']['dm'] != 0:
            for a in board['to']['dm']:
              try:
                user = self.client.get_user(a)
              
                await user.send(embed=embed)
              
              except: # UNREACHABLE USER
                if 'error code: 10013' in traceback.format_exc():
                  clean('dm', a)


          scanned(board_id, latest)


  @tasks.loop(minutes=1)
  async def listen(self):
    await self.client.wait_until_ready()

    ls = [i for i in listens()]
    front = res('https://geekhack.org/index.php?action=recenttopics')

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
        

        if post != listed['post']:
          if poster_id != op_id:
            listened(topic_id, post)
            continue

          else: 
            
            
            inside = res('https://geekhack.org/index.php?topic=' + str(topic_id) + '.' + str(post))

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
              for a in channels:
                try:
                  channel = self.client.get_channel(a)
        
                  await channel.send(embed=embed)                 

                except AttributeError: # UNREACHABLE CHANNEL
                  clean('channel', a)
            
            if dms != 0:
              for a in dms:
                try:
                  
                  user = self.client.get_user(a)
                  
                  await user.send(embed=embed)
                  
                except: # UNREACHABLE USER
                  if 'error code: 10013' in traceback.format_exc():
                    clean('dm', a)

            listened(topic_id, post)
            
        # except:
      #   pass


def setup(client):
  client.add_cog(Start(client))