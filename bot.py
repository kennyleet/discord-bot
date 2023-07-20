import os
import urllib.request
import re
import ffmpeg
import discord
import youtube_dl
from random import randint
from random import choice
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get
from itertools import cycle

bot = commands.Bot(command_prefix="!")
status = cycle(['Под кайфом', 'Отдыхаю', 'Lands of Ilya bots', 'Niggerland',
                'Aye Simulator'])
players = {}
ban_msg = ['']
bot.remove_command('help')
ROLE = "Test Role"

@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")


@bot.event
async def on_message(message):
    channel = message.channel
    if message.author == bot.user:
        return

    if message.content == "/test":
        await channel.send("This is a test.")

    await bot.process_commands(message)


@tasks.loop(seconds = 60)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


@bot.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f"Привет, {author.mention}.")


@bot.command()
async def ping(ctx):
    await ctx.send(f"Пинг : {round(bot.latency * 1000)} мс.")


@bot.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


@bot.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason = reason)


@bot.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} забанен.')


@bot.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if(user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} разбанен.')
            return


@bot.command()
async def add(ctx, left: int, right: int):
    await ctx.send(left + right)


@bot.command()
async def subtract(ctx, left: int, right: int):
    await ctx.send(left - right)


@bot.command()
async def multiply(ctx, left: int, right: int):
    await ctx.send(left * right)


@bot.command()
async def divide(ctx, left: int, right: int):
    if right != 0:
        await ctx.send(left / right)
    else:
        await ctx.send("Если что на ноль делить нельзя.")


@bot.command()
async def random(ctx, left: int, right: int):
    await ctx.send(randint(left, right))

@bot.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == "general": 
            await channel.send_message(f"Добро пожаловать на сервер, {member.mention}")


@bot.command()
async def question(ctx, *, question_):
    responses = ['Возможно',
                 'Точно не могу сказать',
                 'Не уверен',
                 'Cпроси позже',
                 'Понятия не имею',
                 'Да',
                 'Определенно правда',
                 'Так и есть',
                 'Верно',
                 'Так точно',
                 'Нет',
                 'Неправда',
                 'Вроде нет',
                 'Ложь',
                 'Неа']
    await ctx.send(f'Вопрос : {question_}.\nОтвет :{choice(responses)}.')


@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Присоединился к {channel}.")


@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Покинул {channel}.")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Если что я не присоединен к каналу.")


@bot.command()
async def play(ctx, *, search):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Присоединился к {channel}.")

    query_srting = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_srting
    )
    search_results = re.findall('href=\"\\/watch\\?v=(.{11})', htm_content.read().decode())
    url = 'http://www.youtube.com/watch?v=' + search_results[0]

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ОШИБКА: Музыка уже играет.")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Готовлюсь к воспроизведению.")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([url])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -f " + '"' + c_path + '"' + " -s " + url)
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"Играет: {nname[0]}.")
    print("playing\n")


@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Воспроизведение приостановлено.")
    else:
        print("Music not playing failed pause")
        await ctx.send("Музыка не играет. Не удалось приостановить.")


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Воспроизведение возобновлено.")
    else:
        print("Music is not paused")
        await ctx.send("Воспроизведение не было приостановлено.")


@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Музыка остановлена.")
    else:
        print("No music playing failed to stop")
        await ctx.send("Музыка не играет. Не удалось остановить.")


queues = {}


@bot.command(pass_context=True, aliases=['n', 'nex'])
async def playnext(ctx, *, search):

    query_srting = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_srting
    )
    search_results = re.findall('href=\"\\/watch\\?v=(.{11})', htm_content.read().decode())
    url = 'http://www.youtube.com/watch?v=' + search_results[0]

    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([url])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + url)


    await ctx.send("Adding song " + str(q_num) + " to the queue")

    print("Song added to queue\n")


@bot.command(pass_context=True, aliases=['sk'])
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing Next Song")
        voice.stop()
        await ctx.send("Следующая песня.")
    else:
        print("No music playing")
        await ctx.send("Музыка не играет.")


@bot.command(pass_context=True, aliases=['ss'])
async def searchsong(ctx, *, search):
    query_srting = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_srting
    )
    search_results = re.findall('href=\"\\/watch\\?v=(.{11})', htm_content.read().decode())
    await ctx.send('http://www.youtube.com/watch?v=' + search_results[0])
    await ctx.send('http://www.youtube.com/watch?v=' + search_results[1])
    await ctx.send('http://www.youtube.com/watch?v=' + search_results[2])


@bot.command(pass_context=True, aliases=['v', 'vol'])
async def volume(ctx, volume: int):

    if ctx.voice_client is None:
        return await ctx.send("Не подключен к каналу.")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Громкость изменена на {volume}%")


@bot.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member):
    mute_role = discord.utils.get(ctx.message.guild.roles, name="mute")
    await member.add_roles(mute_role)


@bot.command()
async def embedt(ctx):

    embed = discord.Embed(
        colour=discord.Colour.blue(),
        title="Test Title",
        description="This is a test"
    )

    embed.set_author(name="Author", icon_url="https://cdn.discordapp.com/attachments/443208943213477889/601699371221909504/imagesfidosfhdis.jpg")
    embed.set_image(url="https://cdn.discordapp.com/attachments/443208943213477889/601699371221909504/imagesfidosfhdis.jpg")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/443208943213477889/601699371221909504/imagesfidosfhdis.jpg")
    embed.add_field(name="ping", value="This has the bot say pong", inline=False)
    embed.add_field(name="Test Field 2", value="this is test 2", inline=False)
    embed.add_field(name="test field 3", value="This is a test 3", inline=False)
    embed.set_footer(text="This is a footer")

    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    test_e = discord.Embed(
        colour=discord.Colour.orange()
    )
    test_e.set_author(name="Префикс бота = !")
    test_e.add_field(name="!hello", value="Данная функция отправляет приветствие юзеру.", inline=False)
    test_e.add_field(name="!ping", value="Данная функция отправляет пинг юзера.")
    test_e.add_field(name="!clear", value="Данная функция очищает терминал.")
    test_e.add_field(name="!kick", value="Данная функция исключает юзера из сервера.")
    test_e.add_field(name="!ban", value="Данная функция блокирует юзеру доступ к серверу.")
    test_e.add_field(name="!unban", value="Данная функция разблокирует юзеру доступ к серверу.")
    test_e.add_field(name="!mute", value="Данная функция заглушает юзера.")
    test_e.add_field(name="!question", value="Данная функция отправляет ответ на заданный вопрос.")
    test_e.add_field(name="!join", value="Данная функция присоединяет бота к каналу.")
    test_e.add_field(name="!leave", value="Данная функция отсоединяет бота от канала.")
    test_e.add_field(name="!play", value="Данная функция включает музыкального бота.")
    test_e.add_field(name="!pause", value="Данная функция ставит музыкального бота на паузу.")
    test_e.add_field(name="!resume", value="Данная функция возобновляет воспроизведение музыки.")
    test_e.add_field(name="!stop", value="Данная функция останавливает воспроизведение музыки.")
    test_e.add_field(name="!playnext", value="Данная функция заносит в плейлист следующую песню.")
    test_e.add_field(name="!skip", value="Данная функция пропускает песню.")
    test_e.add_field(name="!searchsong", value="Данная функция отправляет юзеру 3 песни по заданному ему запросу.")
    test_e.add_field(name="!volume", value="Данная функция позволяет изменять громкость музыкального бота.")
    await author.send(embed=test_e)


@bot.event
async def on_member_join(member):
    role = get(member.guild.roles, name=ROLE)
    await member.add_roles(role)
    print(f"{member} была выдана роль {role}")

bot.run("NjQxMzY4ODU1NDA2NDQ0NTY0.Xe_bjQ.sYcTjwKpC5E_Nmgx7tBu2r59xO8")