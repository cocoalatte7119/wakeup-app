import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

alarms = {}  # {user_id: (time, voice_channel, alert_task)}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='setalarm')
async def set_alarm(ctx, time: str):
    """Sets an alarm for the user at the specified time (HH:MM)"""
    user_id = ctx.author.id
    hour, minute = map(int, time.split(':'))

    alarm_time = datetime.time(hour, minute)
    now = datetime.datetime.now().time()

    delta = datetime.datetime.combine(datetime.date.today(), alarm_time) - datetime.datetime.combine(datetime.date.today(), now)
    if delta.total_seconds() < 0:
        delta += datetime.timedelta(days=1)

    voice_channel = await ctx.guild.create_voice_channel(name=f'Alarm for {ctx.author.name}')
    await ctx.send(f'Alarm set for {time}. You will be moved to {voice_channel.name} at the set time.')

    async def alarm_task():
        await asyncio.sleep(delta.total_seconds())
        if ctx.author.voice:
            await ctx.author.move_to(voice_channel)
        await play_alarm_sound(voice_channel)

    task = bot.loop.create_task(alarm_task())
    alarms[user_id] = (alarm_time, voice_channel, task)

async def play_alarm_sound(voice_channel):
    """Plays the alarm sound in the specified voice channel"""
    vc = await voice_channel.connect()
    vc.play(discord.FFmpegPCMAudio('alarm_sound.mp3'), after=lambda e: print('done', e))
    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id in alarms:
        alarm_time, voice_channel, task = alarms[member.id]
        if after.channel != voice_channel:
            await asyncio.sleep(60)  # Wait 60 seconds to check if user left the alarm channel
            if member.voice and member.voice.channel == voice_channel:
                return
            await voice_channel.delete()
            del alarms[member.id]

bot.run(TOKEN)
