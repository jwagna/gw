from bs4 import BeautifulSoup as bs
from requests import get, Session
from json import loads


def board_check(b):
  b = str(b)
  if 'https://geekhack.org/index.php?board=' in b:
    soup = r(b) 

    bi = b.find('board') + 6

  else:
    soup = r('https://geekhack.org/index.php?board=' + b)  
  
    bi = 0

  board = soup.title.text
  
  if board != "An Error Has Occurred!" and board != "Login":
    if '.' in b[bi:]:
      board_id = b[bi:][:b[bi:].find('.')]
      
    else:
      board_id = b[bi:]
      
    return board, int(board_id)

  else:
    board = board_id = False

    return board, board_id


def topic_check(board_id):
  front = []

  for p in range(0, 6):
    p *= 50
    
    soup = r('https://geekhack.org/index.php?board=' + str(board_id) + '.' + str(p) + ';sort=last_post;desc')

    for i in soup.find_all('td', class_='subject windowbg2'):
      topic = i.find('a')['href']
      
      tid = topic[topic.find('topic') + 6:-2]
      front.append(int(tid))
      front.sort()

  topic_id = front[-1]

  return int(topic_id)


def pull(t):
  t = str(t)
  if 'https://geekhack.org/index.php?topic=' in t:
    tin = t.find('topic') + 6
    
  else:
    tin = 0
  
  if '.' in t:
    topic_id = t[tin:][:t[tin:].find('.')]
    
  else:
    topic_id = t[tin:]
  
  soup = r('https://geekhack.org/index.php?topic=' + topic_id + '.0')
  title = soup.title.text
  
  if title != "An Error Has Occurred!" and title != "Login":
    topic = soup.find('div', 'keyinfo').find('a').text
    date = soup.find('div', class_='smalltext').text[7:-2]
    op = soup.find_all('div', class_='poster')[0]
    op_name = op.find('a').text
    op_id = int(op.find('a')['href'][op.find('a')['href'].find('u=') + 2:])
    op_href = 'https://geekhack.org/index.php?action=profile;u=' + str(op_id)
    op_score = soup.find('li', class_='postcount').text.replace('Posts: ','')

    try:
      op_flair = op.find('li', class_='membergroup').find('img')['src']

    except:
      op_flair = ''

    try:
      op_icon = 'https://geekhack.org/index.php?' + op.find('li', class_='avatar').find('img')['src'][op.find('li', class_='avatar').find('img')['src'].find('action'):]

    except:
      op_icon = ''

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


    # try:
    #   keyinfo = soup.find_all('div', class_='keyinfo')[-1].find('div', 'smalltext').find('strong').text
      
    #   post = int(keyinfo[keyinfo.find('#') + 1:keyinfo.find('on')])

    # except ValueError: # op post 
    #   post = 0

    return topic, int(topic_id), date, op_name, op_id, op_href, op_flair, op_icon, op_score, image

  else:
    topic = topic_id = date = op_name = op_id = op_href = op_flair = op_icon = op_score = image = False #bad link
    
    return topic, topic_id, date, op_name, op_id, op_href, op_flair, op_icon, op_score, image 
    

def r(t):
  r = get(t)
  soup = bs(r.text, 'lxml')

  return soup
