from datetime import datetime

def log(message):
  time = datetime.now().strftime('%d/%m/%y %H:%M:%S')

  print(f'{time} — {message}')

