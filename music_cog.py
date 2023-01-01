import discord
import traceback
import json
import os
from ast import alias
from discord.ext import commands
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch

# self = el estado de la música, pausa, play, en cola, etc
# ctx = es como un message.content
# vc = virtual chat/channel

class music_cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    
    #Variables para especificar el estado de la música
    self.is_playing = False
    self.is_paused = False

    # Esta variable guarda las canciones en la cola
    self.music_queue = []
    # Para asegurar que YT usa la mejor calidad de música
    self.YDL_OPTIONS = {
      'format': 'bestaudio',
      'noplaylist':'True'
      }
    self.FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options': '-vn'
    }

    self.vc = None

  # Sirve para buscar la canción en YT
  def search_yt(self, item):
    with YoutubeDL(self.YDL_OPTIONS) as ydl:
      try:
        # Busca la canción en YT y arroja el primer resultado
        search = 'cancion'
        yt = YoutubeSearch(search, max_results=1).to_json()
        yt_id = str(json.loads(yt)['videos'][0]['id'])
        # De aquí se extrae la info y se cancela que la canción se descargue
        # Si se desea descargar la canción sólo cambiar download a True
        info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        song_name = info.get('title', None) + '-' + yt_id + '.mp3'
        if os.path.isfile(song_name):
          print('Canción descargada' + song_name)
        else:
          print('Error' + song_name)
      except:
        return False
    return {'source': info['formats'][0]['url'], 'title': info['title']}
    

  # Sirve para buscar la canción en YT a traves de la url
  '''
  def search_yt(self, item):
    with YoutubeDL(self.YDL_OPTIONS) as ydl:
      try: 
        # De aquí se extrae la canción y se anula el que se descargue
        info = ydl.extract_info('ytsearch:%s' % item, download=False)['entries'][0]
      except Exception: 
        return False

    return {'source': info['formats'][0]['url'], 'title': info['title']}
  '''    

  # Se encarga de reproducir la siguiente canción que esté en la cola
  def play_next(self):
    if len(self.music_queue) > 0:
      self.is_playing = True
      
      # Agarra la primer url en la lista
      m_url = self.music_queue[0][0]['source']

      # Elimina de la lista la canción que se estaba reproduciendo
      self.music_queue.pop(0)

      # Se pone la música y se vuelve a iterar play_next hasta que no haya canciones en la cola
      self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
    else:
      self.is_playing = False

  # Esta es la función que sirve para reproducir la música 
  async def play_music(self, ctx):
    if len(self.music_queue) > 0:
      self.is_playing = True

      m_url = self.music_queue[0][0]['source']
      
      # Si no hay nadie en un canal de voz... 
      if self.vc == None or not self.vc.is_connected():
        # ...Intenta meterse a algún canal de voz
        self.vc = await self.music_queue[0][1].connect()

        # Checa si logró meterse al canal de voz y si no da el mensaje
        if self.vc == None:
          await ctx.send("No logré entrar a ningún canal de voz")
          return
      else:
        # El bot busca en qué canal de voz estamos e intenta meterse ahí
        await self.vc.move_to(self.music_queue[0][1])
            
      # Quita la primer canción que se puso de la cola
      self.music_queue.pop(0)

      self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
    else:
      self.is_playing = False

  @commands.command(name="play", aliases=["p"], help="Comando para reproducir una canción de YT")
  async def play(self, ctx, *args):
    query = " ".join(args)
    
    # El bot busca en qué canal estamos y sino estamos conectados muestra el mensaje para saber a dónde conectarse
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
      await ctx.send("Entra a un canal de voz!")
    elif self.is_paused:
      self.vc.resume()
    else:
      song = self.search_yt(query)
      if type(song) == type(True):
        await ctx.send("No se puedo descargar la canción. Formato incorrecto, intenta con otra palabara, esto se puede deber a que está en una playlist o en directo.")
      else:
        await ctx.send("Canción agregada a la cola")
        self.music_queue.append([song, voice_channel])
        
        if self.is_playing == False:
          await self.play_music(ctx)

  @commands.command(name="pause", help="Comando para pausar la canción")
  async def pause(self, ctx, *args):
    if self.is_playing:
        self.is_playing = False
        self.is_paused = True
        self.vc.pause()
    
    elif self.is_paused:
        self.is_paused = False
        self.is_playing = True
        self.vc.resume()
        

  @commands.command(name = "resume", aliases=["r"], help="Comando para darle play a la música")
  async def resume(self, ctx, *args):
    if self.is_paused:
      self.is_paused = False
      self.is_playing = True
      self.vc.resume()

  @commands.command(name="skip", aliases=["s"], help="Salta la canción actualmente reproduciendose")
  async def skip(self, ctx):
    if self.vc != None and self.vc:
      #para la canción...
      self.vc.stop()
      # ... y see vuelve a llamamar a play-music para reproducir la siguiente canción en la cola, si es que hay
      await self.play_music(ctx)


  @commands.command(name="queue", aliases=["q"], help="Comando para mostrar las canciones en la cola")
  async def queue(self, ctx):
    retval = ""
    for i in range(0, len(self.music_queue)):
      # Se itera la lista y sólo se muestran las primeras 5 canciones
      if (i > 4): break
      retval += self.music_queue[i][0]['title'] + "\n"

    if retval != "":
      await ctx.send(retval)
    else:
      await ctx.send("No hay canciones en la cola.")

  @commands.command(name="clear", aliases=["c"], help="Comando para parar la música y borrar la cola de canciones")
  async def clear(self, ctx):
    if self.vc != None and self.is_playing:
      self.vc.stop()
      self.music_queue = []
      await ctx.send("Lista de canciones vacía")

  @commands.command(name="leave", aliases=["disconnect", "l"], help="Comando para sacar al bot del canal de voz")
  async def leave(self, ctx):
    self.is_playing = False
    self.is_paused = False
    await self.vc.disconnect()

