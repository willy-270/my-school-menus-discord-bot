from discord.ext import tasks
from discord import app_commands
import datetime
import meals
import discord
import client
from consts import OWNER_ID, MEALS_CHANNEL_ID
from google_images_download import google_images_download
import os

async def make_meal_embed(meal: meals.Meal):
    if meal is None:
        return None
        
    meal_desc_lines = meal.desc.split("\n")

    response = google_images_download.googleimagesdownload()
    arguments = {"keywords":meal_desc_lines[0], "limit":1, "aspect_ratio": "wide", "output_directory":os.getcwd(), "no_directory":True}
    r = response.download(arguments)
    path = list(r[0].values())[0][0]
    file = discord.File(path, filename="image.png")
    
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
    embed.set_image(url=f"attachment://image.png")
    embed.title = f"***{'Lunch' if meal.is_lunch else 'Breakfast'}, {meal.date.strftime('%m/%d/%Y')}***"
    embed.color = discord.Color.green() if meal.is_lunch else discord.Color.blue()
    embed.description = stlyized_desc
    
    return {"embed": embed, "file": file, "path": path}

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
        await interaction.edit_original_response(content=f"you probably didn't use iso format, {e}")
        return

    lunch = meals.get_meal_by_date(date, True)
    breakfast = meals.get_meal_by_date(date, False)

    if lunch is None or breakfast is None:
        await interaction.edit_original_response(content="No meals found for that date!")
        return

    await interaction.edit_original_response(content="Making embeds & getting images... (may take a while)")

    lunch_embed = await make_meal_embed(lunch)
    breakfast_embed = await make_meal_embed(breakfast)

    await interaction.channel.send(embed=lunch_embed["embed"], file=lunch_embed["file"])
    await interaction.channel.send(embed=breakfast_embed["embed"], file=breakfast_embed["file"])

    os.remove(lunch_embed["path"])
    os.remove(breakfast_embed["path"])

    await interaction.edit_original_response(content="Done!")
    

@client.bot.tree.command(
    name = "shutdown",
    description = "yep",
)
async def self(
    interaction: discord.Interaction,
):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You can't do that!", ephemeral=True)
        return
    await interaction.response.send_message("Shutting down...", ephemeral=True)
    await client.bot.close()

tz = datetime.datetime.now().astimezone().tzinfo     # local timezone
time = datetime.time(hour=6, minute=0, second=0, microsecond=0, tzinfo=tz)

@tasks.loop(time=time)
async def send_meals_loop():
    tmr = datetime.datetime.now().date() + datetime.timedelta(days=1)

    td_lunch_embed = await make_meal_embed(meals.get_todays_meal(True))
    td_breakfast_embed = await make_meal_embed(meals.get_todays_meal(False))
    td_embeds = [td_lunch_embed, td_breakfast_embed]
    
    tmr_lunch_embed = await make_meal_embed(meals.get_meal_by_date(tmr, True))
    tmr_breakfast_embed = await make_meal_embed(meals.get_meal_by_date(tmr, False))
    tmr_embeds = [tmr_lunch_embed, tmr_breakfast_embed]

    if td_embeds is [None, None] and tmr_embeds is [None, None]:
        return

    log_channel = client.bot.get_channel(MEALS_CHANNEL_ID)
    await log_channel.purge(limit=100)

    if td_embeds is not [None, None]:
        await log_channel.send(content="# Today's Meals:")
        await log_channel.send(embed=td_lunch_embed["embed"], file=td_lunch_embed["file"])
        await log_channel.send(embed=td_breakfast_embed["embed"], file=td_breakfast_embed["file"])

        os.remove(td_lunch_embed["path"])
        os.remove(td_breakfast_embed["path"])

    if tmr_embeds is not [None, None]:
        await log_channel.send(content="# Tomorrow's Meals:")
        await log_channel.send(embed=tmr_lunch_embed["embed"], file=tmr_lunch_embed["file"])
        await log_channel.send(embed=tmr_breakfast_embed["embed"], file=tmr_breakfast_embed["file"])

        os.remove(tmr_lunch_embed["path"])
        os.remove(tmr_breakfast_embed["path"])

async def test():
    await make_meal_embed(meals.get_meal_by_date(datetime.datetime.fromisoformat("2024-03-08").date(), True))
    await make_meal_embed(meals.get_meal_by_date(datetime.datetime.fromisoformat("2024-03-08").date(), False))



