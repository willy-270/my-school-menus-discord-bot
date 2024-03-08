from discord.ext import tasks
from discord import app_commands
from datetime import datetime
import meals
import discord
import client
from consts import OWNER_ID, MEALS_CHANNEL_ID

def make_meal_embed(meal: meals.Meal):
        if meal is None:
            return None
        
        stlyized_desc = meal.desc

        italic_words = ["Or", "With", "Fruit", "Milk"]
        meal_desc_lines = meal.desc.split("\n")

        for line in meal_desc_lines:
            if line in italic_words:
                stlyized_desc = stlyized_desc.replace(line, f"*{line}*")
            else:
                stlyized_desc = stlyized_desc.replace(line, f"**{line}**")

        embed = discord.Embed()
        embed.title = f"{'Lunch' if meal.is_lunch else 'Breakfast'}, {meal.date.strftime('%m/%d/%Y')}"
        embed.color = discord.Color.green() if meal.is_lunch else discord.Color.blue()
        embed.description = meal.desc
    
        return embed

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
        date = datetime.fromisoformat(date).date()
    except Exception as e:
        await interaction.edit_original_response(content=f"you probably didn't use iso format, {e}")
        return

    lunch = meals.get_meal_by_date(date, True)
    breakfast = meals.get_meal_by_date(date, False)

    if lunch is None or breakfast is None:
        await interaction.edit_original_response(content="No meals found for that date!")
        return

    lunch_embed = discord.Embed()
    lunch_embed.title = f"Lunch, {lunch.date.strftime('%m/%d/%Y')}"
    lunch_embed.description = lunch.desc
    lunch_embed.color = discord.Color.blue()

    breakfast_embed = discord.Embed()
    breakfast_embed.title = f"Breakfast, {breakfast.date.strftime('%m/%d/%Y')}"
    breakfast_embed.description = breakfast.desc
    breakfast_embed.color = discord.Color.yellow()

    await interaction.edit_original_response(embeds=[lunch_embed, breakfast_embed], content="")

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
    today = datetime.datetime.now().date()
    tmr = today + datetime.timedelta(days=1)

    td_lunch_embed = make_meal_embed(meals.get_td_meal(True))
    td_breakfast_embed = make_meal_embed(meals.get_td_meal(False))
    td_embeds = [td_lunch_embed, td_breakfast_embed]
    
    tmr_lunch_embed = make_meal_embed(meals.get_meal_by_date(tmr, True))
    tmr_breakfast_embed = make_meal_embed(meals.get_meal_by_date(tmr, False))
    tmr_embeds = [tmr_lunch_embed, tmr_breakfast_embed]

    if td_embeds is [None, None] and tmr_embeds is [None, None]:
        return

    log_channel = client.bot.get_channel(MEALS_CHANNEL_ID)
    await log_channel.purge(limit=100)

    if td_embeds is not [None, None]:
        await log_channel.send(content= "# Today's Meals", embeds=[td_lunch_embed, td_breakfast_embed])

    if tmr_embeds is not [None, None]:
        await log_channel.send(content= "# Tommorow's Meals", embeds=[tmr_lunch_embed, tmr_breakfast_embed])