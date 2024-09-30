from discord.ext import tasks
from discord import app_commands
import datetime
import pytz
import meals
import discord
import client
import db

def make_meal_embed(meal: meals.Meal) -> dict["embed": discord.Embed, "meal_found": bool]:
    if meal is None:
        embed = discord.Embed()
        embed.title = "No meal found"
        embed.color = discord.Color.red()
        return embed, False
        
    meal_desc_lines = meal.desc.split("\n")
    
    italic_lines = ["Or", "With", "Fruit", "Milk"]
    for i, line in enumerate(meal_desc_lines):
        if line == "":
            pass
        elif line in italic_lines:
            meal_desc_lines[i] = f"*{line}*"
        else:
            meal_desc_lines[i] = f"**{line}**"

    stlyized_desc = "\n".join(meal_desc_lines)

    embed = discord.Embed()
    embed.title = f"***{'Lunch' if meal.is_lunch else 'Breakfast'}, {meal.date.strftime('%m/%d/%Y')}***"
    embed.color = discord.Color.green() if meal.is_lunch else discord.Color.blue()
    embed.description = stlyized_desc
    
    return embed, True

@client.bot.tree.command(
    name = "get_meals_by_date",
    description = "yep",
)
@app_commands.describe(date="in iso format, YYYY-MM-DD")
async def self(
    interaction: discord.Interaction,
    date: str,
):
    await interaction.response.send_message("Getting...", ephemeral=False)

    try:
        date = datetime.datetime.fromisoformat(date).date()
    except Exception as e:
        await interaction.edit_original_response(content=f"you probably didn't use valid iso format")
        return

    lunch = meals.get_meal_by_date(date, True)
    breakfast = meals.get_meal_by_date(date, False)

    if lunch == None and breakfast == None:
        await interaction.edit_original_response(content="No meals found for that date!")
        return

    await interaction.edit_original_response(content="Making embeds... (may take a while)")

    lunch_embed = make_meal_embed(lunch)
    breakfast_embed = make_meal_embed(breakfast)

    if lunch_embed:
        await interaction.channel.send(embed=lunch_embed["embed"])
    if breakfast_embed:
        await interaction.channel.send(embed=breakfast_embed["embed"])

    await interaction.edit_original_response(content="Done!")
    
@client.bot.tree.command(
    name = "config",
    description = "congigure the bot"
)
@app_commands.describe(
    timezone="use this format please: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List, Ex: America/New_York",
)
async def self(
    interaction: discord.Interaction,
    channel_to_send_meals: discord.TextChannel,
    timezone: str
):
    await interaction.response.send_message("Saving changes...", ephemeral=False)

    database = db.Database()
    conn = await database.connect()
    await database.insert_config_values(conn, [interaction.guild_id, channel_to_send_meals.id, timezone])
    await conn.close()

    await interaction.edit_original_response(content="Done!")

async def get_server_config(guild_id):
    database = db.Database()
    conn = await database.connect()
    values = await database.get_config_values(conn, guild_id)
    await conn.close()
    return values

async def get_and_send_meals(log_channel_id: discord.TextChannel):
    log_channel = client.bot.get_channel(log_channel_id)
    await log_channel.purge(limit=100)

    tmr = datetime.datetime.now().date() + datetime.timedelta(days=1)

    td_lunch_embed = make_meal_embed(meals.get_todays_meal(True))
    td_breakfast_embed = make_meal_embed(meals.get_todays_meal(False))
    
    tmr_lunch_embed = make_meal_embed(meals.get_meal_by_date(tmr, True))
    tmr_breakfast_embed = make_meal_embed(meals.get_meal_by_date(tmr, False))

    if td_lunch_embed["meal_found"] or td_breakfast_embed["meal_found"]:
        await log_channel.send(content="# Today's Meals:")
        if td_lunch_embed["meal_found"]:
            await log_channel.send(embed=td_lunch_embed["embed"])
        if td_breakfast_embed["meal_found"]:
            await log_channel.send(embed=td_breakfast_embed["embed"]) 

    if tmr_lunch_embed["meal_found"] or tmr_breakfast_embed["meal_found"]:
        await log_channel.send(content="# Tomorrow's Meals:")
        if tmr_lunch_embed["meal_found"]:
            await log_channel.send(embed=tmr_lunch_embed["embed"])
        if tmr_breakfast_embed["meal_found"]:
            await log_channel.send(embed=tmr_breakfast_embed["embed"])

@tasks.loop(seconds=60)
async def send_meals_loop():
    conn = await db.Database().connect()
    cursor = await conn.cursor()
    await cursor.execute("SELECT server_id FROM servers")
    guilds = await cursor.fetchall()
    await conn.close()

    for guild_id in guilds:
        server_settings = await get_server_config(guild_id[0])
        if server_settings:
            channel_id, timezone = server_settings
            tz = pytz.timezone(timezone) if timezone else pytz.utc

            now = datetime.datetime.now(tz)
            desired_time = datetime.time(hour=7, minute=0, tzinfo=tz)

            if now.hour == desired_time.hour and now.minute == desired_time.minute:
                print(f"sending meals to {guild_id[0]}...")

                await get_and_send_meals(channel_id)


   