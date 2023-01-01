import discord
from discord.ext import commands
import os
import json
from help_cog import help_cog
from music_cog import music_cog
from responses import responses_cog

if os.path.exists(os.getcwd() + '/config.json'):
  with open('./config.json') as f:
    configData = json.load(f)
else:
  configTemplate = {'Token': '', 'Prefix': '/'}

  with open(os.getcwd() + '/config.json', 'w+') as f:
    json.dump(configTemplate, f)

token = configData["Token"]
prefix = configData["Prefix"]

# Comandos de discord para poder activar el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)


# Para que no lea el mensaje predeterminado de discord
bot.remove_command('help')
    
@bot.event
async def on_ready():
  await bot.add_cog(help_cog(bot))
  await bot.add_cog(music_cog(bot))
  await bot.add_cog(responses_cog(bot))
  print(f'{bot.user} está funcionando')


bot.run(token)