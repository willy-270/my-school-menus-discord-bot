from datetime import datetime
from lunch import meals
from discord import app_commands
import discord
import client
from consts import OWNER_ID, MEALS_CHANNEL_ID

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


@client.bot.event 
async def on_message(message):
    if message.channel.id == MEALS_CHANNEL_ID:
        client.msgs_in_meal_logs.append(message)