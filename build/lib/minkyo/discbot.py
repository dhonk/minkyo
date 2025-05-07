import discord
import dotenv
import os
import minkyo
import pickle
from discord import app_commands
from discord.ext import commands

''' 
top down implementation:

setup processes
    - when connected to a guild, check the corresponding data file
    
    > one function for on_ready logging
    > one function for joining a new guild
    > one function for checking available guilds

rides command
    - 
    
address setup command
    - 
'''

# discord API connection
dotenv.load_dotenv()
token = os.getenv('DISC_API')

# for debug only
print(f'Discord api key: {token}')

# discord bot setup
desc = '''A helper tool in order to make rides easier. '''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description=desc, intents=intents)

# ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('~~~~~~')
    await bot.load_extension('cogs.maincog')

# guild joined TODO
@bot.event
async def on_guild_join(guild):
    print(f'Joined a guild')

# guild becomes available
@bot.event
async def on_guild_available(guild):
    out = ''
    out += f'{guild} : {guild.id}'
    # check for the data file
    path = f'./server_data/{guild.id}.pickle'
    try:
        # case: data file for server doesn't exist yet
        with open(path, 'xb') as f:
            out += ' - Created file\n'
        with open(path, 'wb') as f:
            pickle.dump({}, f) # initialize with empty data
    except FileExistsError:
        out += ' - ✅\n'
    except Exception as e:
        out += f'Error: {e}\n'
    print(out)

@bot.command()
async def reload(ctx: commands.Context, extension: str):
    await bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'reloaded {extension}')
    
bot.run(token)