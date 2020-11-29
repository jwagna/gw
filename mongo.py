import pymongo
from pymongo import MongoClient
from requests import get, Session
import scrape
from bs4 import BeautifulSoup as bs


def read_key():
  with open ("key.txt", 'r') as f:
    lines = f.readlines()
    return lines[0].strip()
  

cluster = MongoClient(read_key())

db = cluster['gh']

following = db['following']
listening = db['listening']
serving = db['serving']
scanning = db['scanning']
watching = db['watching']

def id_iter(c):
  try:
    _id = c.find_one({},sort=[( '_id', pymongo.DESCENDING)])['_id'] + 1

  except:
    _id = 0

  finally:
    return _id


def follow(uid, t, tid, a):
  if uid != a:
    m = 'channel'
  else:
    m = 'dm'

  if listen(tid, a, m):
    # if following.find_one({'user_id':uid}) is not None:
    return following.update_one({'user_id':uid}, {'$push': {'following':{'topic':t, 'topic_id':tid, 'address':a}}})


    # else: # never followed before, create index
    #   return following.insert_one({'_id':id_iter(following), 'user_id':uid, 'following':[{'topic':t, 'topic_id':tid, 'address':a}]})

  else:
    return False # already in channel and dm (DUPES)


def follows(uid):
  if following.find_one({'user_id':uid}) is not None:
    return following.find_one({'user_id':uid})['following']

  else:
    following.insert_one({'_id':id_iter(following), 'user_id':uid, 'following':[]})

    return following.find_one({'user_id':uid})['following']

def unfollow(uid, i):
  r = '~~REDACTED~~'

  if i == 'all':
    count = len(follows(uid))

    if count > 0:
      for i in range(count - 1, -1, -1):
        tid = follows(uid)[i]['topic_id']
        a = following.find_one({'user_id':uid})['following'][i]['address']

        following.update_one({'user_id':uid}, {'$set':{'following.' + str(i):r}})

        unlisten(tid, uid, a)

      return following.update_one({'user_id':uid}, {'$pull':{'following':r}})

    else:
      return False

  else:
    i = int(i)

    if i >= 1 and i <= 10:
      i -= 1

      tid = follows(uid)[i]['topic_id']
      a = following.find_one({'user_id':uid})['following'][i]['address']

      following.update_one({'user_id':uid}, {'$set':{'following.' + str(i):r}})

      unlisten(tid, uid, a)

      return following.update_one({'user_id':uid}, {'$pull':{'following':r}})

    else:
      return False


def listen(tid, a, m):
  if m == 'channel':
    t = {'channel':[a], 'dm':[]}

  else:
    t = {'channel':[], 'dm':[a]}

  ti, tid, d, opn, opid, oph, opf, opi, opsc, i = scrape.pull(tid)


  if listening.find_one({'topic_id':tid}) is None:
    _id = id_iter(listening)

    try: # SHITTY WAY OF KEEPING COUNT OF HOW MANY THREADS LISTENED IN TOTAL
      previous = listening.find_one({'_id':_id - 1})['to']

      if len(previous['channel']) == 0 and len(previous['dm']) == 0: # previous is placeholder
        listening.delete_one({'_id':_id - 1})

    except TypeError: # there are 0 listens (edge case)
      pass

    finally: # insert new listen
      return listening.insert_one({'_id':_id, 'topic':ti, 'topic_id':tid, 'poster_id':opid, 'post':0, 'to':t})


  else: # thread exists in listen
    try:
    # if a in listening.find_one({'topic_id':tid}['to'])
      l = listening.find_one({'topic_id':tid})['to']

      if m == 'channel':
        if a not in l['channel']:
          return listening.update_one({'topic_id':tid}, {'$addToSet':{'to.channel':a}})

        else:
          return False # exists

      else:
        if a not in l['dm']:
          return listening.update_one({'topic_id':tid}, {'$addToSet':{'to.dm':a}})

        else:
          return False # exists

    except KeyError: # edge case?
      return listening.update_one({'topic_id':tid}, {'$set': {'topic':ti, 'topic_id':tid, 'poster_id':opid, 'to':t}})


def unlisten(tid, uid, a):
  # if len(list((following.find({'following.topic_id':{'$in':[tid]}})))) == 0: # no one is following
  if listening.find_one({'topic_id':tid})['_id'] != id_iter(listening) - 1:
    return listening.delete_one({'topic_id':tid})

  else:
    if uid != a:
      return listening.update_one({'topic_id':tid}, {'$pull': {'to.channel':a}})

    else:
      return listening.update_one({'topic_id':tid}, {'$pull': {'to.dm':a}})


def listens():
  return listening.find({})


def listened(tid, ps):
  return listening.update_one({'topic_id':tid}, {'$set': {'post':ps}})


def listen_dupe(tid):
  try:
    channels = listening.find_one({'topic_id':tid})['to']['channel']
    if len(channels) != 0:
      return channels

    else:
      return [0]

  except TypeError:
    return [0]


def watch(uid, b, bid, a):
  if uid != a:
    m = 'channel'

  else:
    m = 'dm'

  if prescan(bid, a, m):
    # if watching.find_one({'user_id':uid}) is not None:
    return watching.update_one({'user_id':uid}, {'$push': {'watching':{'board':b, 'board_id':bid, 'address':a}}})

    # else: # never followed before, create index
    #   return watching.insert_one({'_id':id_iter(watching), 'user_id':uid, 'watching':[{'board':b, 'board_id':bid, 'address':a}]})

  else:
    return False # already in channel and dm (DUPES)


def watches(uid):
  if watching.find_one({'user_id':uid}) is not None:
    return watching.find_one({'user_id':uid})['watching']

  else:
    watching.insert_one({'_id':id_iter(watching), 'user_id':uid, 'watching':[]})

    return watching.find_one({'user_id':uid})['watching']


def unwatch(uid, i):
  r = '~~REDACTED~~'

  if i == 'all':
    count = len(watches(uid))

    if count > 0:
      for i in range(count - 1, -1, -1):
        bid = watches(uid)[i]['board_id']
        a = watching.find_one({'user_id':uid})['watching'][i]['address']

        watching.update_one({'user_id':uid}, {'$set':{'watching.' + str(i):r}})

        unscan(bid, uid, a)

      return watching.update_one({'user_id':uid}, {'$pull':{'watching':r}})

    else:
      return False

  else:
    i = int(i)

    if i >= 1 and i <= 10:
      i -= 1

      bid = watches(uid)[i]['board_id']
      a = watching.find_one({'user_id':uid})['watching'][i]['address']

      watching.update_one({'user_id':uid}, {'$set':{'watching.' + str(i):r}})

      unscan(bid, uid, a)


      return watching.update_one({'user_id':uid}, {'$pull':{'watching':r}})

    else:
      return False


def prescan(bid, a, m):
  if m == 'channel':
    t = {'channel':[a], 'dm':[]}

  else:
    t = {'channel':[], 'dm':[a]}

  b, bid = scrape.board_check(bid)

  if scanning.find_one({'board_id':bid}) is None:
    tid = scrape.topic_check(bid)

    return scanning.insert_one({'_id':id_iter(scanning), 'board':b, 'board_id':bid, 'topic_id':tid, 'to':t})

  else: # thread exists in scan
    try:
      l = scanning.find_one({'board_id':bid})['to']

      if m == 'channel':
        if a not in l['channel']:
          return scanning.update_one({'board_id':bid}, {'$addToSet':{'to.channel':a}})

        else:
          return False # exists

      else:
        if a not in l['dm']:
          return scanning.update_one({'board_id':bid}, {'$addToSet':{'to.dm':a}})

        else:
          return False # exists'

    except KeyError:
      return scanning.update_one({'board_id':bid}, {'$set': {'to':t}})


def scans():
  return scanning.find({})


def scanned(bid, tid):
  return scanning.update_one({'board_id':bid}, {'$set': {'topic_id':tid}})


def scan_dupe(bid):
  try:
    channels = scanning.find_one({'board_id':bid})['to']['channel']

    if len(channels) != 0:
      return channels

    else:
      return [0]

  except TypeError:
    return [0]


def unscan(bid, uid, a):
  # if len(list((watching.find({'watching.board_id':{'$in':[bid]}})))) == 0: # no one is watching
  #   scanning.update_one({'board_id':bid}, {'$set': {'to':{}}})

  # else: # someone still watching
  if uid != a:
    return scanning.update_one({'board_id':bid}, {'$pull': {'to.channel':a}})

  else:
    return scanning.update_one({'board_id':bid}, {'$pull': {'to.dm':a}})


def serve(s, sid):
  if serving.find_one({'server_id':sid}) is None:
    serving.insert_one({'_id':id_iter(serving), 'server':s, 'server_id':sid, 'unrestricting':False, 'serving':True})

  else:
    serving.update_one({'server_id':sid}, {'$set': {'server':s, 'serving':True}})


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
  try:
    serving.update_one({'server_id':sid}, {'$pull': {'unrestricting':cid}})

    if len(serving.find_one({'server_id':sid})['unrestricting']) == 0:
      return serving.update_one({'server_id':sid}, {'$set': {'unrestricting':False}})

  except:
    return False


def unrestricts(sid):
  return serving.find_one({'server_id':sid})['unrestricting']


def clean(m, a):
  following.update_many({}, {'$pull': {'following':{'address':a}}})
  listening.update_many({}, {'$pullAll': {'to.' + m:[a]}})
  watching.update_many({}, {'$pull': {'watching':{'address':a}}})
  scanning.update_many({}, {'$pullAll': {'to.' + m:[a]}})

  return


def res(url):
  r = get(url)
  soup = bs(r.text, 'lxml')

  return soup
