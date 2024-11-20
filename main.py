import discord
from discord.ext import tasks, commands
import random
import requests
import dotenv
import re
import os
import subprocess
import time
import asyncio

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
    await interaction.response.send_message("Updating bot...", ephemeral=False)
    if "testbot" in os.getcwd():
        os.chdir("..")
    os.system("git config --global --add safe.directory '*'") # just dont do this to your dev machine
    os.system("git pull")
    await interaction.followup.send("Bot updated. Restarting...", ephemeral=False)
    await bot.close()

@bot.tree.command(name="checkout")
@commands.has_permissions(administrator=True)
@discord.app_commands.describe(pr = "The PR number to checkout")
async def checkout(interaction: discord.Interaction, pr: str):
    await interaction.response.send_message("Checking out PR...", ephemeral=False)
    if not "testbot" in  os.getcwd():
        os.chdir("testbot")
    os.system("git config --global --add safe.directory '*'")
    os.system(f"git fetch origin pull/{pr}/head:pr-{pr}")
    os.system(f"git checkout pr-{pr}")
    await interaction.followup.send("PR checked out.", ephemeral=False)

@bot.tree.command(name="shutdown")
@commands.has_permissions(administrator=True)
async def shutdown(interaction: discord.Interaction):
    os.system("killall python3")
    await interaction.response.send_message("Shutting down bot...", ephemeral=False)

@bot.tree.command(name="start")
@commands.has_permissions(administrator=True)
async def start(interaction: discord.Interaction):
    if not "testbot" in os.getcwd():
        os.chdir("testbot")
    
    await interaction.response.send_message("Starting bot...", ephemeral=False)
    
    try:
        # Create subprocess asynchronously
        process = await asyncio.create_subprocess_exec(
            "python3", "main.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Function to handle output streaming
        async def send_logs():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                log_message = line.decode().strip()
                if log_message:
                    try:
                        await interaction.followup.send(f"```\n{log_message}\n```")
                    except discord.HTTPException:
                        continue
        
        async def send_errors():
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                log_message = line.decode().strip()
                if log_message:
                    try:
                        await interaction.followup.send(f"```\n{log_message}\n```")
                    except discord.HTTPException:
                        continue
        
        # Start log streaming task
        bot.loop.create_task(send_logs())
        bot.loop.create_task(send_errors())
        
        # Monitor process status
        await process.wait()
        
        if process.returncode != 0:
            await interaction.followup.send("Bot process terminated with an error!")
            
    except Exception as e:
        await interaction.followup.send(f"Error starting bot: {str(e)}")

bot.run(os.getenv("QA_DISCORD_TOKEN"))