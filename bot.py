import discord
from discord.ext import commands, tasks
import asyncio

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def set_alarm(ctx, time: str):
    user_id = ctx.author.id
    alarms[user_id] = time
    await ctx.send(f'Alarm set for {time}')
    bot.loop.create_task(create_alarm_channel(ctx, user_id, time))

async def create_alarm_channel(ctx, user_id, alarm_time):
    guild = ctx.guild
    alarm_channel = await guild.create_voice_channel(f'{ctx.author.name}-alarm')
    
    # Calculate sleep time
    now = datetime.datetime.now()
    alarm_time_dt = datetime.datetime.strptime(alarm_time, '%H:%M')
    alarm_time_dt = now.replace(hour=alarm_time_dt.hour, minute=alarm_time_dt.minute, second=0, microsecond=0)
    sleep_time = (alarm_time_dt - now).total_seconds()
    
    if sleep_time < 0:
        sleep_time += 86400  # Add 24 hours if the time is past today
    
    await asyncio.sleep(sleep_time)
    
    member = guild.get_member(user_id)
    if member.voice:
        await member.move_to(alarm_channel)
        await play_alarm_sound(alarm_channel)

async def play_alarm_sound(channel):
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio('alarm.mp3'), after=lambda e: print('done', e))
    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()

bot.run('YOUR_BOT_TOKEN')