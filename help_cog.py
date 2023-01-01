import discord
from discord.ext import commands

class help_cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.help_message = """
```
Bienvenido, estos son nuestros comandos generales:

/help - Para ver todos los comandos

COMANDOS DE MÚSICA
/p, /play - Buscará la canción en YT y la reproducirá en el canal en el que estés
/q, /queue - Muestra las siguientes 5 canciones por reproducir
/s, /skip - Salta la canción que se esté reproduciendo
/c, /clear - Para la música y borra las canciones en la cola
/l, /leave - Desconecta el bot del canal de voz
/pause - Pausa la canción que se esté reproduciendo
/r, /resume - Le da play a la canción si estaba en pausa

COMANDOS DE CHAT
Prueba a saludar a nuestro bot
/advice - Recibe un consejo

P.D: Ten cuidado cuando hables de Ice Bot
```
"""
    self.text_channel_list = []


  @commands.Cog.listener()
  async def on_ready(self):
    for guild in self.bot.guilds:
      for channel in guild.text_channels:
        self.text_channel_list.append(channel)

    await self.send_to_all(self.help_message)        

  @commands.command(name="help", help="Muestra todos los comandos")
  async def help(self, ctx):
    await ctx.send(self.help_message)

  async def send_to_all(self, msg):
    for text_channel in self.text_channel_list:
      await text_channel.send(msg)