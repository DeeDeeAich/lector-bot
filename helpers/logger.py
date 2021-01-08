import datetime

def log(message):
    with open('bot.log', 'a') as f:
        f.write(f'[{datetime.datetime.now().strftime("%c")}] {message}\n')