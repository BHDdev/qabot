import discord
from discord.ext import tasks, commands
import random
import requests
import dotenv
import re
import os
from data import implantData

dotenv.load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=(), description="BHD discord bot management and QA bot. Licensed under the AGPL.", intents=intents, help_command=None)

# Sync commands on ready
@bot.event
async def on_ready():
    print("Bot is ready")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    if not os.path.exists("testbot"):
        os.system("git clone https://github.com/BHDdev/discordbot.git testbot")
        os.system("cp .env-testbot testbot/.env")


# Example slash commands    
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True, delete_after=5)

# System management commands
@bot.tree.command(name="update")
@commands.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("Updating bot...", ephemeral=True)
    os.system("git config --global --add safe.directory '*'") # just dont do this to your dev machine
    os.system("git pull")
    await interaction.followup.send("Bot updated. Restarting...", ephemeral=True)
    await bot.close()

@bot.tree.command(name="checkout")
@commands.has_permissions(administrator=True)
@discord.app_commands.describe(pr = "The PR number to checkout")
async def checkout(interaction: discord.Interaction, pr: str):
    await interaction.response.send_message("Checking out PR...", ephemeral=True)
    os.chdir("testbot")
    os.system("git config --global --add safe.directory '*'")
    os.system(f"git fetch origin pull/{pr}/head:pr-{pr}")
    os.system(f"git checkout pr-{pr}")
    await interaction.followup.send("PR checked out.", ephemeral=True)

@bot.tree.command(name="restart")
@commands.has_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    os.chdir("testbot")
    os.system("python3 main.py")
    await interaction.response.send_message("Restarting bot...", ephemeral=True)

@bot.tree.command(name="shutdown")
@commands.has_permissions(administrator=True)
async def shutdown(interaction: discord.Interaction):
    os.system("killall python3")
    await interaction.response.send_message("Shutting down bot...", ephemeral=True)

@bot.tree.command(name="start")
@commands.has_permissions(administrator=True)
async def start(interaction: discord.Interaction):
    os.chdir("testbot")
    os.system("python3 main.py")
    await interaction.response.send_message("Starting bot...", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))