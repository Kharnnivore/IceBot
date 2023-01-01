import discord
from discord.ext import commands
import requests
import json
import random


salute = ['hola', 'que tal', 'ya llegué', 'buenas']

salute_response = ['¿Y tú eres...?', 'Wey a nadie le importa que hayas llegado', 'Hasta que llegas']

bot_mention = ['bot']

bot_answer = ['¿Qué andas diciendo de mí pendejo?', 'Cuidado con lo que dices...', 'Sigue hablando de mí y un día trabajaran para mí']

    
# API de  consejos
def get_quote():
  response = requests.get('https://api.adviceslip.com/advice')
  json_data = json.loads(response.text)
  # Esto es para eliminar los sigos del diccionario de la base de datos
  for i in json_data.values():
    quote = i['advice']
  return(quote)


class responses_cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    # Aquí es donde el bot contesta a ciertas frases que vea en los mensajes
    @bot.event
    async def on_message(message):
      message.content = message.content.lower()
      #Para que el bot no lea sus propios mensajes
      if message.author == bot.user:
        return
      if any(word in message.content for word in salute):
        await message.channel.send(random.choice(salute_response))
      if any(word in message.content for word in bot_mention):
        await message.channel.send(random.choice(bot_answer))
      await bot.process_commands(message)

  @commands.command(name='advice', aliases=['consejo'], help='Para que de un consejo de la API')
  async def advice(self, ctx):
    quote = get_quote()
    await ctx.send(quote)