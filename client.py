from discord.ext import commands
from consts import BOT_TOKEN
import discord


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot is ready')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    from commands import send_meals_loop
    send_meals_loop.start()

def run():
    bot.run(BOT_TOKEN)

