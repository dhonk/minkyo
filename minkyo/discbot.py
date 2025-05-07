import dotenv
import os

import discord
from discord.ext import commands
import pickle

# discord API connection
dotenv.load_dotenv()
token = os.getenv('DISC_API')

bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} : {bot.user.id}')
    print('~~~~~')
    await bot.load_extension('minkyo.cogs.maincog')
    try:
        guilds = [discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028)]
        await bot.tree.sync(guild=guilds[0])
        await bot.tree.sync(guild=guilds[1])
    except Exception as e:
        print(f'Error during sync: {e}')

@bot.event
async def on_guild_available(guild):
    print('Verifying server data file')
    try:
        with open(f'./server_data/{guild.id}.pickle', 'xb') as _:
            print(f'{guild} ({guild.id}) : Created file')
        with open(f'./server_data/{guild.id}.pickle', 'wb') as f:
            pickle.dump({}, f)
    except FileExistsError:
        print(f'{guild} ({guild.id}) : ✅')
    except Exception as e:
        print(f'Error while verifying server data: {e}')

@bot.command()
async def reload(ctx):
    await bot.reload_extension('minkyo.cogs.maincog')
    bot.tree.remove_command('gen_mindy', guild = discord.Object(id=1356468638726492231))
    try:
        guilds = [discord.Object(id=1356468638726492231), discord.Object(1149416104922452028)]
        await bot.tree.sync(guild=guilds[0])
        await bot.tree.sync(guild=guilds[1])
    except Exception as e:
        print(f'Error during sync: {e}')

@bot.command()
async def clear_data(_):
    with open('./server_data/drivers.pickle', 'wb') as file:
        pickle.dump({}, file)
    with open('./server_data/riders.pickle', 'wb') as file:
        pickle.dump({}, file)

bot.run(token)