from bs4 import BeautifulSoup as bs
import requests
from aiohttp import ClientSession
import asyncio

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.87 Safari/537.36'}

def get(url):
  try:
    response = requests.get(url, headers=headers, timeout=5)

    return bs(response.text, 'lxml')

  except:

    return None



async def aget(session, url):
  while True:
    async with session.get(url, headers=headers) as response:
      text = await response.text()     

      # if text:
      return bs(text, 'lxml')

      # else:
      #   print("Bad response")
      #   await asyncio.sleep(5)