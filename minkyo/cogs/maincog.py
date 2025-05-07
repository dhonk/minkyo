import discord
from discord.ext import commands
from discord import app_commands

from minkyo import distance
from minkyo import gmaps

import pickle

# TODO at some point I really need to reformat this, idk why I shoved this into init LMAO but if it works it works ykwim (no)

class maincog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # store message ID & channel in order to know where to track reactions
        # this currently won't work for applications where makeride is called twice, for instance
        self.recent_msg_id = None
        self.recent_chn = None

        # use this to store who reacted which to check for dual reaction
        self.drivers = []
        self.riders = []

        # {user.id : {'name' : user.nick, 'address' : address, 'pId' : pId, 'cap' : capacity}}
        self.driver_data = {}
        # use this in order to store the data ykwim
        with open('./server_data/drivers.pickle', 'rb') as f:
            self.driver_data = pickle.load(f)

        # {user.id : {'name' : user.nick, 'address' : address, 'pId' : pId}}
        self.rider_data = {}
        with open('./server_data/riders.pickle', 'rb') as f:
            self.rider_data = pickle.load(f)

        # integer UID for each instance
        self.uid = 0
        
        # lookup table for solution objects
        self.solns = {}

        @bot.tree.command(name='hello', description='say hello', guilds=[discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028)])
        async def hello(interaction: discord.Interaction):
            await interaction.response.send_message('hi wsp!')

        @bot.tree.command(name='makeride', description='make a new ride', guilds=[discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028)])
        @app_commands.describe(
            dest='Where everyone is coming from/going to',
            ping='The role/member that you want to ping',
        )
        async def makeride(interaction: discord.Interaction, ping: discord.Member | discord.Role = None, dest: str = None):
            embed = discord.Embed(
                title=f'React here for rides to **{dest or "?"}**!!!!!',
                description=f"""
                **INSTRUCTIONS**
                If you will be **driving**, react with :red_car:
                
                If you need a **ride**, react with :person_standing:
                
                If this is your first time using me, please type in:
                **/setup_driver <your address> <how many people you can drive>**
                OR 
                **/setup_rider <your address>**
                
                *For example*, if I need to get dropped off at C9, I'll type /setup_rider college 9!\n\nAfter you do this once, you won't have to do this again!!""",
                colour=int('0xFFDE00', 16),

            )
            channel = interaction.channel
            msg = '‼️'
            if ping != None:
                msg = f'{ping.mention}'   
            sent = await interaction.response.send_message(msg, embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))
            
            # initial reactions
            sent_id = sent.message_id
            message = await channel.fetch_message(sent_id)
            await message.add_reaction('🚗')
            await message.add_reaction('🧍')
            
            # update the ids of the most recent makeride
            self.recent_msg_id = message.id
            self.recent_chn = channel
            
            # clear the lists of the people who reacted for a previous instance of makeride
            self.riders = []
            self.drivers = []
        
        @bot.event
        async def on_reaction_add(reaction, user):
            # someone reacted to the ride prompt
            if reaction.message.id != self.recent_msg_id:
                return
            
            if reaction.emoji == '🧍': # rider instance:
                # double reaction check
                if user.id in self.drivers:
                    await self.recent_chn.send(f'<@{user.id}> 야 임마 pick only one')
                    await reaction.remove(user)
                    return
                self.riders.append(user.id)
                # run check to see if user's data is stored"
                if user.id not in self.rider_data: # user info not found in data store
                    # case: data not found:
                    await self.recent_chn.send(f"<@{user.id}> looks like we don't have your info yet, use /setup_rider to get started!")
                    await reaction.remove(user)
                # else: # user info found, add to the soln
                #    entry = self.rider_data[user.id]
                #    new = distance.rider(entry['name'], entry['address'], entry['pId'])
                #    self.soln.add_rider(new)
                #    print(f'Added: {new}')                    
                    
            if reaction.emoji == '🚗': # driver instance:
                # double reaction check
                if user.id in self.riders:
                    await self.recent_chn.send(f'<@{user.id}> 야 임마 pick only one')
                    await reaction.remove(user)
                    return
                self.drivers.append(user.id)
                # run check to see if driver's data is stored
                if user.id not in self.driver_data:
                    # case: data not found
                    await self.recent_chn.send(f"<@{user.id}> looks like we don't have your info yet, use /setup_driver to get started!")
                    await reaction.remove(user)
                #else:
                #    entry = self.driver_data[user.id]
                #    new = distance.driver(entry['name'], entry['address'], entry['pId'], entry['cap'])
                    
                #    print(f'Added: {new}')
        
        @bot.event
        async def on_reaction_remove(reaction, user):
            # someone removed reaction:
            if reaction.emoji == '🧍': # rider instance:
                try:
                    self.riders.remove(user.id)
                except:
                    print('on_reaction: rider already removed')
            if reaction.emoji == '🚗': # driver instance:
                try:
                    self.drivers.remove(user.id)
                except:
                    print('on_reaction: driver already removed')

        # setup a rider
        @bot.tree.command(description='Set yourself up as a rider! Enter your address here!', guilds=[discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028)])
        async def setup_rider(interaction : discord.Interaction, address : str, user : discord.User = None):
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

            try:
                guild = interaction.guild
                member = await guild.fetch_member(rider_obj.id)
                name = member.display_name
                self.rider_data[rider_obj.id] = {'name' : name, 'address' : adds[0], 'pId' : pIds[0]}
            except Exception as e:
                print('sum ting wong: ', e)
                self.rider_data[rider_obj.id] = {'name' : rider_obj.name, 'address' : adds[0], 'pId' : pIds[0]}

            print('added: ', rider_obj.id, ': ', self.rider_data[rider_obj.id])
            with open('./server_data/riders.pickle', 'wb') as f:
                pickle.dump(self.rider_data, f)

        # setup a driver
        @bot.tree.command(description='Set yourself up as a driver! Enter the your address number of people you can take here!', guilds=[discord.Object(id=1356468638726492231), discord.Object(id=1149416104922452028)])
        async def setup_driver(interaction: discord.Interaction, address : str, capacity : int, user : discord.Member = None):
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

            try:
                guild = interaction.guild
                member = await guild.fetch_member(rider_obj.id)
                name = member.display_name
                self.driver_data[rider_obj.id] = {'name' : name, 'address' : adds[0], 'pId' : pIds[0], 'cap' : capacity}
            except Exception as e:
                print('sum ting wong: ', e)
                self.driver_data[rider_obj.id] = {'name' : rider_obj.name, 'address' : adds[0], 'pId' : pIds[0], 'cap' : capacity}
                
            print('added: ', rider_obj.id, ': ', self.driver_data[rider_obj.id])
            with open('./server_data/drivers.pickle', 'wb') as f:
                pickle.dump(self.driver_data, f)

        @bot.tree.command(description='generate a rides list', guilds=[discord.Object(id=1356468638726492231), discord.Object(1149416104922452028)])
        async def genride(interaction: discord.Interaction):
            if self.recent_msg_id == None or self.recent_chn == None:
                await interaction.response.send_message('Use /makeride to first create a ride query!', ephemeral=True)
                return
        
            # got the drivers and riders lists
            print(self.drivers)
            print(self.riders)

            for u in self.drivers:
                if u not in self.driver_data:
                    # TODO: have bot dm, and use reactions + minkyo.gmaps to get the place id
                    await interaction.response.send_message('Missing info!', ephemeral=True)
                    return

            for u in self.riders:
                if u not in self.rider_data:
                    # TODO: have bot dm, and use reactions + minkyo.gmaps to get the place id
                    await interaction.response.send_message('Missing info!', ephemeral=True)
                    return

            t1 = []
            t2 = []
            for d in self.drivers:
                entry = self.driver_data[d]
                new = distance.driver(entry['name'], entry['address'], entry['pId'], entry['cap'])
                t1.append(new)
                print('added')
                # solve().add_driver() did not work, for some reason would preserve for every subsequent makeride

            for r in self.riders:
                entry = self.rider_data[r]
                new = distance.rider(entry['name'], entry['address'], entry['pId'])
                t2.append(new)
                print('added')
                # solve().add_rider() did not work, for some reason would preserve for every subsequent makeride
            
            self.solns[self.uid] = distance.solve(t1, t2)
            solution = self.solns[self.uid]
            self.uid = self.uid + 1
                
            print(solution)
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
                await interaction.response.send_message('Number of riders exceeds number of seats.', ephemeral=True)


async def setup(bot):
    await bot.add_cog(maincog(bot))