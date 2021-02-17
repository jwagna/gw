from json import loads
import asyncio
from handler import get, aget

bad = ["An Error Has Occurred!", "Login", "geekhack - Index"]


def verify(user_input):
  user_input = str(user_input)

  # if 'https://geekhack.org/index.php?topic=' in user_input:
  #   index = user_input.find('topic=') + 5
  #   target = "topic"

  # elif 'https://geekhack.org/index.php?board=' in user_input:
  #   index = user_input.find('board=') + 5
  #   target = "board"

  # else:
  #   index = 0
  #   target = None

  # if '.' in user_input:
  #   target_id = user_input[index:][:user_input[index:].find('.')]
    
  # else:
  #   target_id = user_input[index:]

  if 'topic=' in user_input:
    index = user_input.find('topic=') + 6
    target_id = user_input.split('=')[-1]
    target = "topic"

  elif 'board=' in user_input:
    index = user_input.find('board=') + 6
    target_id = user_input.split('=')[-1]
    target = "board"

  else:
    target_id = user_input
    target = None

  if '.' in target_id:
    target_id = target_id.split('.')[0]
  
  if target is not None:
    response = get('https://geekhack.org/index.php?' + target + '=' + target_id + '.0')

    if response is None:
      return 503

    title = response.title.text

    if title in bad:
      return 404

    if target == "board":
      return title, int(target_id)
    
  else:
    response = get('https://geekhack.org/index.php?topic=' + target_id + '.0')

    if response is None:
      return 503

    title = response.title.text
    
    if title in bad:
      response = get('https://geekhack.org/index.php?board=' + target_id + '.0')

      if response is None:
        return 503

      title = response.title.text

      if title in bad:
        return 404

      return title, int(target_id)

  topic_id = target_id
  topic = response.find('div', 'keyinfo').find('a').text
  date = response.find('div', class_='smalltext').text[7:-2]
  op = response.find_all('div', class_='poster')[0]
  op_name = op.find('a').text
  op_id = int(op.find('a')['href'][op.find('a')['href'].find('u=') + 2:])
  op_href = 'https://geekhack.org/index.php?action=profile;u=' + str(op_id)
  op_score = response.find('li', class_='postcount').text.replace('Posts: ','')

  try:
    op_flair = op.find('li', class_='membergroup').find('img')['src']

  except:
    op_flair = ''

  try:
    op_icon = 'https://geekhack.org/index.php?' + op.find('li', class_='avatar').find('img')['src'][op.find('li', class_='avatar').find('img')['src'].find('action'):]

  except:
    op_icon = ''

  try:
    image = response.find_all('a', class_='highslide')[1]['href']
    
  except:
    try:
      image = response.find_all('a', class_='highslide')[0]['href']
    
    except:
      image = 'https://geekhack.org/Themes/Nostalgia/images/banner.png'

  finally:
    if 'https://geekhack.org/index.php?' in image:
      image = 'https://geekhack.org/index.php?' + image[image.find('action'):]


  # try:
  #   keyinfo = soup.find_all('div', class_='keyinfo')[-1].find('div', 'smalltext').find('strong').text
    
  #   post = int(keyinfo[keyinfo.find('#') + 1:keyinfo.find('on')])

  # except ValueError: # op post 
  #   post = 0

  return topic, int(topic_id), date, op_name, op_id, op_flair, op_icon, op_score, image


def sort(board_id):
  front = []

  for p in range(0, 6):
    p *= 50
    
    soup = get('https://geekhack.org/index.php?board=' + str(board_id) + '.' + str(p) + ';sort=last_post;desc')

    for i in soup.find_all('td', class_='subject windowbg2'):
      topic = i.find('a')['href']
      
      tid = topic[topic.find('topic') + 6:-2]
      front.append(int(tid))
      front.sort()

  topic_id = front[-1]

  return int(topic_id)


# def verify(user_input):
#   user_input = str(user_input)

#   try:
#     if 'geekhack.org' in user_input:
#       raise

#     if '.' in user_input:
#       user_input = user_input.split('.')[0]

#     if int(user_input) >= 10000:
#       target = "topic"

#     else:
#       target = "board"

#     target_id = user_input

#   except ValueError:
#     if 'https://geekhack.org/index.php?topic=' in user_input:
#       index = user_input.find('topic=') + 6
#       target = "topic"

#     elif 'https://geekhack.org/index.php?board=' in user_input:
#       index = user_input.find('board=') + 6
#       target = "board"

#     else:
#       index = 0
#       target = None

#     if '.' in user_input:
#       # target_id = user_input[index:][:user_input[index:].find('.')]
#       target_id = user_input.split('.')[0]
      
#     else:
#       target_id = user_input[index:]
      
#   finally:
#     if target is not None:
#       response = get('https://geekhack.org/index.php?' + target + '=' + target_id + '.0')

#       if response is None:
#         return 503

#       title = response.title.text

#       if title in bad:
#         return 404

#     else:
#       response = get('https://geekhack.org/index.php?topic=' + target_id + '.0')

#       if response is None:
#         return 503

#       topic = response.title.text
      
#       if topic in bad:
#         response = get('https://geekhack.org/index.php?board=' + target_id + '.0')

#         if response is None:
#           return 503

#         board = response.title.text

#         if board in bad:
#           return 404

#         else:
#           board_id = target_id

#           return board, int(board_id)

#   topic_id = target_id
#   topic = response.find('div', 'keyinfo').find('a').text
#   date = response.find('div', class_='smalltext').text[7:-2]
#   op = response.find_all('div', class_='poster')[0]
#   op_name = op.find('a').text
#   op_id = int(op.find('a')['href'][op.find('a')['href'].find('u=') + 2:])
#   op_href = 'https://geekhack.org/index.php?action=profile;u=' + str(op_id)
#   op_score = response.find('li', class_='postcount').text.replace('Posts: ','')

#   try:
#     op_flair = op.find('li', class_='membergroup').find('img')['src']

#   except:
#     op_flair = ''

#   try:
#     op_icon = 'https://geekhack.org/index.php?' + op.find('li', class_='avatar').find('img')['src'][op.find('li', class_='avatar').find('img')['src'].find('action'):]

#   except:
#     op_icon = ''

#   try:
#     image = response.find_all('a', class_='highslide')[1]['href']
    
#   except:
#     try:
#       image = response.find_all('a', class_='highslide')[0]['href']
    
#     except:
#       image = 'https://geekhack.org/Themes/Nostalgia/images/banner.png'

#   finally:
#     if 'https://geekhack.org/index.php?' in image:
#       image = 'https://geekhack.org/index.php?' + image[image.find('action'):]


#   # try:
#   #   keyinfo = soup.find_all('div', class_='keyinfo')[-1].find('div', 'smalltext').find('strong').text
    
#   #   post = int(keyinfo[keyinfo.find('#') + 1:keyinfo.find('on')])

#   # except ValueError: # op post 
#   #   post = 0

#   return topic, int(topic_id), date, op_name, op_id, op_flair, op_icon, op_score, image