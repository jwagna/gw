import pymongo
from pymongo import MongoClient
from requests import get, Session
from scraper import *
from bs4 import BeautifulSoup as bs
from logger import log

def read_key():
  with open ("key.txt", 'r') as f:
    lines = f.readlines()
    return lines[0].strip()


cluster = MongoClient(read_key())

db = cluster['gw']

following = db['following']
listening = db['listening']
serving = db['serving']
watching = db['watching']

def id_iter(c):
  try:
    _id = c.find_one({},sort=[( '_id', pymongo.DESCENDING)])['_id'] + 1

  except:
    _id = 0

  finally:
    return _id


def follow(user_id, target, target_id, address, response):
  if user_id != address:
    method = 'channel'
    
  else:
    method = 'dm'

  if target_id >= 10000:
    if listen(response, address, method):
      return following.update_one({'user_id':user_id}, {'$addToSet': {'following.topics':{'topic':target, 'topic_id':target_id, 'address':address}}})

    else:
      return False # already in channel and dm (DUPES)

  else:
    if watch(response, address, method):
      return following.update_one({'user_id':user_id}, {'$addToSet': {'following.boards':{'board':target, 'board_id':target_id, 'address':address}}})


    else:
      return False # already in channel and dm (DUPES)


def follows(user_id):
  if following.find_one({'user_id':user_id}) is None:
    following.insert_one({'_id':id_iter(following), 'user_id':user_id, 'following':{'topics':[], 'boards':[]}})

  return following.find_one({'user_id':user_id})['following']


def unfollow(user_id, i):
  placeholder = '~~REDACTED~~'

  followlist = follows(user_id)

  topics = followlist['topics']
  boards = followlist['boards']

  if i == 'all':
    if len(topics) > 0 or len(boards) > 0:
      for topic in topics:
        unlisten(topic['topic_id'], user_id, topic['address'])

      for board in boards:
        unwatch(board['board_id'], user_id, board['address'])

      return following.update_one({'user_id':user_id}, {'$set':{'following':{'topics':[], 'boards':[]}}})
    # if len(topics) > 0:
    #   for i in range(len(topics) - 1, -1, -1):
    #     topic_id = topics[i]['topic_id']
    #     address = following.find_one({'user_id':user_id})['following'][i]['address']
        
    #     following.update_one({'user_id':user_id}, {'$set':{'following.topics' + str(i):placeholder}})

    #     unlisten(topic_id, user_id, address)

    #   return following.update_one({'user_id':user_id}, {'$pull':{'following.topics':placeholder}})
      
    else:
      return False

  else:
    try:
      i = int(i)

      if i >= 1 and i <= 20:
        i -= 1
        diff = following.find_one({'user_id':user_id})['following']['topics']
        if i >= len(diff):
          i -= len(diff)
          match = following.find_one({'user_id':user_id})['following']['boards'][i]
          board_id = match['board_id']
          board = match['board']
          address = match['address']

          following.update_one({'user_id':user_id}, {'$set':{'following.boards.' + str(i):placeholder}})

          unwatch(board_id, user_id, address)

          following.update_one({'user_id':user_id}, {'$pull':{'following.boards':placeholder}})

          return board, board_id

        else:
          match = following.find_one({'user_id':user_id})['following']['topics'][i]
          topic_id = match['topic_id']
          topic = match['topic']
          address = match['address']

          following.update_one({'user_id':user_id}, {'$set':{'following.topics.' + str(i):placeholder}})

          unlisten(topic_id, user_id, address)

          following.update_one({'user_id':user_id}, {'$pull':{'following.topics':placeholder}})

          return topic, topic_id


    except ValueError:
      pass


    return False


def listen(response, address, method):
  if method == 'channel':
    to = {'channel':[address], 'dm':[]}

  elif method == 'dm':
    to = {'channel':[], 'dm':[address]}

  # topic, topic_id, d, opn, opid, oph, opf, opi, opsc, i = scrape.pull(topic_id)
  topic = response[0]
  topic_id = response[1]
  
  if listening.find_one({'topic_id':topic_id}) is None:
    _id = id_iter(listening)

    # try: # SHITTY WAY OF KEEPING COUNT OF HOW MANY THREADS LISTENED IN TOTAL
    #   previous = listening.find_one({'_id':_id - 1})['to']

    #   if len(previous['channel']) == 0 and len(previous['dm']) == 0: # previous is placeholder
    #     listening.delete_one({'_id':_id - 1})

    # except TypeError: # there are 0 listens (edge case)
    #   pass

    # finally: # insert new listen
    #   return listening.insert_one({'_id':_id, 'topic':topic, 'topic_id':topic_id, 'post':0, 'to':to})
    log("Now listening in " + str(topic_id))
    return listening.insert_one({'_id':_id, 'topic':topic, 'topic_id':topic_id, 'last':0, 'to':to})


  else: # thread exists in listen
    try:
    # if address in listening.find_one({'topic_id':topic_id}['to'])
      l = listening.find_one({'topic_id':topic_id})['to']

      if method == 'channel':
        if address not in l['channel']:
          return listening.update_one({'topic_id':topic_id}, {'$addToSet':{'to.channel':address}})

        else:
          return False # exists

      else:
        if address not in l['dm']:
          return listening.update_one({'topic_id':topic_id}, {'$addToSet':{'to.dm':address}})

        else:
          return False # exists

    except KeyError: # edge case?
      return listening.update_one({'topic_id':topic_id}, {'$set': {'topic':topic, 'topic_id':topic_id, 'to':topic}})


def unlisten(topic_id, user_id, address):
  # if len(list((following.find({'following.topic_id':{'$in':[topic_id]}})))) == 0: # no one is following
  # if listening.find_one({'topic_id':topic_id})['_id'] != id_iter(listening) - 1:
  #   return listening.delete_one({'topic_id':topic_id})

  # else:
  
  if user_id != address:
    return listening.update_one({'topic_id':topic_id}, {'$pull': {'to.channel':address}})

  else:
    return listening.update_one({'topic_id':topic_id}, {'$pull': {'to.dm':address}})


def listens():
  return listening.find({})


def listened(topic_id, ps):
  return listening.update_one({'topic_id':topic_id}, {'$set': {'last':ps}})


def listen_dupe(topic_id):
  try:
    channels = listening.find_one({'topic_id':topic_id})['to']['channel']
    if len(channels) != 0:
      return channels

    else:
      return [0]

  except TypeError:
    return [0]


def watches():
  return watching.find({})


def watch(response, address, method):
  if method == 'channel':
    to = {'channel':[address], 'dm':[]}

  elif method == 'dm':
    to = {'channel':[], 'dm':[address]}
  board = response[0]
  board_id = response[1]
  

  if watching.find_one({'board_id':board_id}) is None:
    topic_id = sort(board_id)
    log("Now watching " + str(board_id))
    return watching.insert_one({'_id':id_iter(watching), 'board':board, 'board_id':board_id, 'last':topic_id, 'to':to})

  else: # thread exists in scan
    try:
      l = watching.find_one({'board_id':board_id})['to']

      if method == 'channel':
        if address not in l['channel']:
          return watching.update_one({'board_id':board_id}, {'$addToSet':{'to.channel':address}})

        else:
          return False # exists

      else:
        if address not in l['dm']:
          return watching.update_one({'board_id':board_id}, {'$addToSet':{'to.dm':address}})

        else:
          return False # exist

    except KeyError:
      return watching.update_one({'board_id':board_id}, {'$set': {'to':to}})


def watched(board_id, topic_id):
  return watching.update_one({'board_id':board_id}, {'$set': {'topic_id':topic_id}})


def watch_dupe(board_id):
  try:
    channels = watching.find_one({'board_id':board_id})['to']['channel']

    if len(channels) != 0:
      return channels

    else:
      return [0]

  except TypeError:
    return [0]


def unwatch(board_id, user_id, address):
  # if len(list((watching.find({'watching.board_id':{'$in':[board_id]}})))) == 0: # no one is watching
  #   watching.update_one({'board_id':board_id}, {'$set': {'to':{}}})

  # else: # someone still watching
  if user_id != address:
    return watching.update_one({'board_id':board_id}, {'$pull': {'to.channel':address}})

  else:
    return watching.update_one({'board_id':board_id}, {'$pull': {'to.dm':address}})


def serve(s, sid):
  if serving.find_one({'server_id':sid}) is None:
    serving.insert_one({'_id':id_iter(serving), 'server':s, 'server_id':sid, 'unrestricting':False, 'serving':True})

  else:
    serving.update_one({'server_id':sid}, {'$set': {'server':s, 'serving':True}})

def serves():
  return serving.find({})

def unserve(s, sid):
  if serving.find_one({'server_id':sid}) is None:
    serving.insert_one({'_id':id_iter(serving), 'server':s, 'server_id':sid, 'unrestricting':False, 'serving':False})

  else:
    serving.update_one({'server_id':sid}, {'$set': {'serving':False}})


def unrestrict(sid, cid):
  u = serving.find_one({'server_id':sid})['unrestricting']
  if u == False:
    return serving.update_one({'server_id':sid}, {'$set': {'unrestricting':[cid]}})

  else:
    if cid not in u:
      return serving.update_one({'server_id':sid}, {'$addToSet':{'unrestricting':cid}})

    else:
      return False # exists


def restrict(sid, cid):
  if unrestricts(sid, cid) is False:
    return False

  else:
    serving.update_one({'server_id':sid}, {'$pull': {'unrestricting':cid}})

    if len(serving.find_one({'server_id':sid})['unrestricting']) == 0:
      serving.update_one({'server_id':sid}, {'$set': {'unrestricting':False}})
 

def unrestricts(sid, cid):
  try:
    if cid not in serving.find_one({'server_id':sid})['unrestricting']:
      return False
    
  except TypeError:
    return False
    

def clean(method, address):
  following.update_many({}, {'$pull': {'topics':{'address':address}}})
  following.update_many({}, {'$pull': {'boards':{'address':address}}})
  listening.update_many({}, {'$pullAll': {'to.' + method:[address]}})
  watching.update_many({}, {'$pullAll': {'to.' + method:[address]}})
  # watching.update_many({}, {'$pullAll': {'watching':{'address':address}}})
  # watching.update_many({}, {'$pullAll': {'to.' + method:[address]}})
