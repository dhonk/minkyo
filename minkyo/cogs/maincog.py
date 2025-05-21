# discord.py library
import discord
from discord.ext import commands
from discord import app_commands

# distance and google maps libraries
from minkyo import distance
from minkyo import gmaps

# data file management
import pickle

# concurrency
import asyncio

# updated database
import sqlite3

# the main cog
class maincog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # store message ID & channel in order to know where to track reactions
        # this currently won't work for applications where makeride is called twice, for instance
        # TODO eventually add concurrency for multiple ride instances
        self.recent_msg_id = None
        self.recent_chn = None

        # use this to store who reacted which to check for dual reaction, and their corresponding locks
        self.drivers = []
        self.riders = []
        self.dr_lists_lock = asyncio.Lock() # lock both self.drivers and self.riders

        # driver data storage
        # TODO: currently holds all the driver information as an object in memory, change to write/read from database ONLY
        # {user.id : {'name' : user.nick, 'address' : address, 'pId' : pId, 'cap' : capacity}}
        self.driver_data = {}
        # use this in order to store the data ykwim
        with open('./server_data/drivers.pickle', 'rb') as f:
            self.driver_data = pickle.load(f)
        self.driver_data_lock = asyncio.Lock() # lock for self.driver_data

        # {user.id : {'name' : user.nick, 'address' : address, 'pId' : pId}}
        self.rider_data = {}
        with open('./server_data/riders.pickle', 'rb') as f:
            self.rider_data = pickle.load(f)
        self.rider_data_lock = asyncio.Lock() # lock for self.rider_data

        # TODO: for concurrency between multiple ride instances
        # integer UID for each instance
        self.uid = 0
        
        # lookup table for solution objects
        self.solns = {}

        # initialize database
        self.conn = sqlite3.connect('minkyo.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, name TEXT, address TEXT, pId TEXT, capacity INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS riders (id INTEGER PRIMARY KEY, name TEXT, address TEXT, pId TEXT)''')
        self.conn.commit()

    # setup command tree & listeners 
    async def cog_load(self):
        # Register event listeners
        self.bot.add_listener(self.on_reaction_add)
        self.bot.add_listener(self.on_reaction_remove)

    # command to diagnostic, simple hello world type echo
    @app_commands.command(name='hello', description='say hello')
    @app_commands.guilds(discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028))
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message('hi wsp!')

    # command to initialize a rides query
    @app_commands.command(name='makeride', description='make a new ride')
    @app_commands.guilds(discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028))
    @app_commands.describe(
        dest='Where everyone is coming from/going to',
        ping='The role/member that you want to ping',
    )
    async def makeride(self, interaction: discord.Interaction, ping: discord.Member | discord.Role = None, dest: str = None):
        # defer to prevent 404 error
        await interaction.response.defer()

        # embed actually send the message content
        embed = discord.Embed(
            title=f'React here for rides to **{dest or "?"}**!!!!!',
            description=(
                "**INSTRUCTIONS**\n"
                "If you will be **driving**, react with :red_car:\n\n"
            
                "If you need a **ride**, react with :person_standing:\n\n"
            
                "If this is your first time using me, please **type in**:\n"
                "**/setup_driver <your address> <how many people you can drive>**\n"
                "OR\n" 
                "**/setup_rider <your address>**\n\n"
            
                "*For example*, if I need to get dropped off at C9, I'll type **/setup_rider college 9!**\n\n"
                "After you do this once, you won't have to do this again!!"
            ),
            colour=int('0xFFDE00', 16),
        )

        # default msg in case of no ping
        msg = '‼️'
        if ping != None:
            msg = f'{ping.mention}' 

        # utilize followup webhook, sent is type WebhookMessage
        sent_msg = await interaction.followup.send(msg, embed=embed, allowed_mentions=discord.AllowedMentions(roles=True), wait=True)
        
        # initial reactions for other users to add onto
        await sent_msg.add_reaction('🚗')
        await sent_msg.add_reaction('🧍')
        
        # fetch the mesage from the sent webhook
        # update the ids of the most recent makeride
        message = await sent_msg.fetch()
        self.recent_msg_id = message.id
        self.recent_chn = message.channel
    
    async def on_reaction_add(self, reaction, user):
        # someone reacted to the ride prompt
        if reaction.message.id != self.recent_msg_id:
            return
        
        async with self.dr_lists_lock:
            if reaction.emoji == '🧍': # rider instance:
                # double reaction check
                if user.id in self.drivers:
                    await self.recent_chn.send(f'<@{user.id}> 야 임마 pick only one')
                    await reaction.remove(user)
                    return
                # run check to see if user's data is stored"
                async with self.rider_data_lock:
                    if user.id not in self.rider_data: # user info not found in data store
                        # case: data not found:
                        await self.recent_chn.send(f"<@{user.id}> looks like we don't have your info yet, use /setup_rider to get started!")
                        await reaction.remove(user)
                self.riders.append(user.id)             
                    
            if reaction.emoji == '🚗': # driver instance:
                # double reaction check
                if user.id in self.riders:
                    await self.recent_chn.send(f'<@{user.id}> 야 임마 pick only one')
                    await reaction.remove(user)
                    return
                # run check to see if driver's data is stored
                async with self.driver_data_lock:
                    if user.id not in self.driver_data:
                        # case: data not found
                        await self.recent_chn.send(f"<@{user.id}> looks like we don't have your info yet, use /setup_driver to get started!")
                        await reaction.remove(user)
                self.drivers.append(user.id)
    
    async def on_reaction_remove(self, reaction, user):
        async with self.dr_lists_lock:
            # someone removed reaction:
            if reaction.emoji == '🧍': # rider instance:
                try:
                    self.riders.remove(user.id)
                except:
                    pass
            if reaction.emoji == '🚗': # driver instance:
                try:
                    self.drivers.remove(user.id)
                except:
                    pass

    # setup a rider
    @app_commands.command(description='Set yourself up as a rider! Enter your address here!')
    @app_commands.guilds(discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028))
    async def setup_rider(self, interaction : discord.Interaction, address : str, user : discord.User = None):
        # get the addresses, and the pIds
        pIds, adds = gmaps.extract_from_place(gmaps.get_place(address))

        # TODO add suggestion match functionality
        # add_menu = '\n'.join([f'{i+1}: {a}' for i, a in enumerate(adds)])
        opt = f' for {user.name}' if user != None else ''
        await interaction.response.send_message(f"Entering address: {adds[0]}{opt}. If this doesn't look right, please run setup again!", ephemeral=True)

        # this is the discord.Member object for which to set up the info for
        rider_obj = interaction.user
        if user != None:
            rider_obj = user

        async with self.rider_data_lock:
            try:
                guild = interaction.guild
                member = await guild.fetch_member(rider_obj.id)
                name = member.display_name
                self.rider_data[rider_obj.id] = {'name' : name, 'address' : adds[0], 'pId' : pIds[0]}
            except Exception as e:
                print('sum ting wong: ', e)
                self.rider_data[rider_obj.id] = {'name' : rider_obj.name, 'address' : adds[0], 'pId' : pIds[0]}

            # serialize update, update data files
            print('added: ', rider_obj.id, ': ', self.rider_data[rider_obj.id])
            with open('./server_data/riders.pickle', 'wb') as f:
                pickle.dump(self.rider_data, f)

    # setup a driver
    @app_commands.command(description='Set yourself up as a driver! Enter the your address number of people you can take here!')
    @app_commands.guilds(discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028))
    async def setup_driver(self, interaction: discord.Interaction, address : str, capacity : int, user : discord.Member = None):
        # get the addresses, and the pIds
        pIds, adds = gmaps.extract_from_place(gmaps.get_place(address))
        
        # TODO add suggestion match functionality
        # add_menu = '\n'.join([f'{i+1}: {a}' for i, a in enumerate(adds)])

        opt = f' for {user.name}' if user != None else ''
        await interaction.response.send_message(f"Entering address: {adds[0]}{opt}. If this doesn't look right, please run setup again!", ephemeral=True)

        # this is the discord.Member object for which to set up the info for
        rider_obj = interaction.user
        if user != None:
            rider_obj = user

        async with self.driver_data_lock:
            try:
                guild = interaction.guild
                member = await guild.fetch_member(rider_obj.id)
                name = member.display_name
                self.driver_data[rider_obj.id] = {'name' : name, 'address' : adds[0], 'pId' : pIds[0], 'cap' : capacity}
            except Exception as e:
                print('sum ting wong: ', e)
                self.driver_data[rider_obj.id] = {'name' : rider_obj.name, 'address' : adds[0], 'pId' : pIds[0], 'cap' : capacity}
                
            # serialize update, update data files
            print('added: ', rider_obj.id, ': ', self.driver_data[rider_obj.id])
            with open('./server_data/drivers.pickle', 'wb') as f:
                pickle.dump(self.driver_data, f)

    # generate a rides list given the most recent rides query
    @app_commands.command(description='generate a rides list')
    @app_commands.guilds(discord.Object(id=1356468638726492231), discord.Object(1149416104922452028))
    async def genride(self, interaction: discord.Interaction):
        if self.recent_msg_id == None or self.recent_chn == None:
            await interaction.response.send_message('Use /makeride to first create a ride query!', ephemeral=True)
            return

        async with self.dr_lists_lock:
            # check for driver initialization fye
            for u in self.drivers:
                async with self.driver_data_lock:
                    if u not in self.driver_data:
                        # TODO: have bot dm, and use reactions + minkyo.gmaps to get the place id
                        await interaction.response.send_message('Missing info!', ephemeral=True)
                        return

            # check for rider initialization yuh 
            for u in self.riders:
                async with self.rider_data_lock:
                    if u not in self.rider_data:
                        # TODO: have bot dm, and use reactions + minkyo.gmaps to get the place id
                        await interaction.response.send_message('Missing info!', ephemeral=True)
                        return

        # create the distance.driver or distance.rider objects type beat frl frl yuh
        t1 = []
        t2 = []

        # for drivers
        async with self.dr_lists_lock:
            async with self.driver_data_lock:
                for d in self.drivers:
                    entry = self.driver_data[d]
                    new = distance.driver(entry['name'], entry['address'], entry['pId'], entry['cap'])
                    t1.append(new)

            # for riders
            async with self.rider_data_lock:    
                for r in self.riders:
                    entry = self.rider_data[r]
                    new = distance.rider(entry['name'], entry['address'], entry['pId'])
                    t2.append(new)
            
        # update uid #TODO USE THIS TO SUPPORT MULITPLE INSTANCES IN FUTURE
        self.solns[self.uid] = distance.solve(t1, t2)
        solution = self.solns[self.uid]
        self.uid = self.uid + 1
            
        print(solution)
        # check to see if enough drivers are present
        if solution.solveable():
            solution.find_routes_greedy()
            solution.print_dist()
            routes = solution.route_to_str()
            embed=discord.Embed(
                title='**Rides: 🌞**',
                description=routes,
                colour=int('0xFFDE00', 16),
            )
            await interaction.response.send_message(embed=embed)
            # self.recent_msg_id = None
            # self.recent_chn = None
        else:
            # case: not enough seats
            await interaction.response.send_message('Number of riders exceeds number of seats.', ephemeral=True)

# setup cog
async def setup(bot):
    await bot.add_cog(maincog(bot))