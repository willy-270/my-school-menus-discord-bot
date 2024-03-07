import discord
from consts import BOT_TOKEN, MEALS_CHANNEL_ID
import datetime
from lunch import meals
from discord.ext import tasks
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot is ready')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    send_meals_loop.start()

def run():
    bot.run(BOT_TOKEN)


tz = datetime.datetime.now().astimezone().tzinfo     # local timezone
time = datetime.time(hour=6, minute=0, second=0, microsecond=0, tzinfo=tz)

@tasks.loop(time=time)
async def send_meals_loop():
    channel = bot.get_channel(MEALS_CHANNEL_ID)
    await channel.purge(limit=100)
    
    today = datetime.datetime.now().date()
    tommorow = today + datetime.timedelta(days=1)

    lunch = meals.get_todays_meal(True)
    breakfast = meals.get_todays_meal(False)

    tommorows_lunch = meals.get_meal_by_date(tommorow, True)
    tommorows_breakfast = meals.get_meal_by_date(tommorow, False)

    if lunch is None and breakfast is None and tommorows_lunch is None and tommorows_breakfast is None:
        return

    def make_meal_embed(meal, is_lunch: bool, is_tommorow: bool = False):
        embed = discord.Embed()
        embed.title = f"{'Tommorow' if is_tommorow else 'Today'}'s {'Lunch' if is_lunch else 'Breakfast'}, {tommorow.strftime('%m/%d/%Y') if is_tommorow else today.strftime('%m/%d/%Y')}"
        embed.color = discord.Color.green() if is_lunch else discord.Color.blue()
        
        if meal is None:
            embed.description = "No meal!"
        else:
            embed.description = meal.desc
        
        return embed
    
    lunch_embed = make_meal_embed(lunch, True)
    breakfast_embed = make_meal_embed(breakfast, False)

    tommorows_lunch_embed = make_meal_embed(tommorows_lunch, True, True)
    tommorows_breakfast_embed = make_meal_embed(tommorows_breakfast, False, True)

    await channel.send(content= "# Today's Meals", embeds=[lunch_embed, breakfast_embed])
    await channel.send(content= "# Tommorow's Meals", embeds=[tommorows_lunch_embed, tommorows_breakfast_embed])