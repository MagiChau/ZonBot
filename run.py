import bot
import os
import sys

if __name__ == '__main__':
	filepath = os.path.join(sys.path[0] + "/config.ini")
	zonbot = bot.Bot(filepath, '!')
	zonbot.run()
