import discord
from discord.ext import commands
from discord import app_commands

from minkyo import distance
from minkyo import gmaps

import pickle

class maincog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # store message ID & channel in order to know where to track reactions
        # this currently won't work for applications where makeride is called twice, for instance
        self.recent_msg_id = None
        self.recent_chn = None

        @bot.tree.command(name='hello', description='say hello', guild=discord.Object(id=1356468638726492231))
        async def hello(interaction: discord.Interaction):
            await interaction.response.send_message('hi wsp!')

        @bot.tree.command(name='makeride', description='make a new ride', guild=discord.Object(id=1356468638726492231))
        @app_commands.describe(
            dest='The destination'
        )
        async def makeride(interaction: discord.Interaction, ping: discord.Member | discord.Role = None, dest: str = None):
            embed = discord.Embed(
                title=f'React here for rides to **{dest or "?"}**!!!!!',
                description=f'Drivers, react with :red_car:\n\nRiders, react with :person_standing:',
            )
            channel = interaction.channel
            msg = '‼️'
            if ping != None:
                msg = f'<@{ping.id}>' if type(ping) == discord.Member else f'<@&{ping.id}>'
            sent = await interaction.response.send_message(msg, embed=embed)
            print(type(sent))
            sent_id = sent.message_id
            message = await channel.fetch_message(sent_id)
            await message.add_reaction('🚗')
            await message.add_reaction('🧍')
            self.recent_msg_id = message.id
            self.recent_chn = channel
        
        @bot.tree.command(description='generate a rides list', guild=discord.Object(id=1356468638726492231))
        async def genride(interaction: discord.Interaction):
            if self.recent_msg_id == None or self.recent_chn == None:
                await interaction.response.send_message('Use /makeride to first create a ride query!')
            else:
                await interaction.response.send_message('Processing:')
                message = await self.recent_chn.fetch_message(self.recent_msg_id)
                drivers_reacts = message.reactions[0]
                riders_reacts = message.reactions[1]
                raw_drivers = [u async for u in drivers_reacts.users()]
                raw_riders = [u async for u in riders_reacts.users()]
                driver_objs = list(filter(lambda n: n.bot == False, raw_drivers))
                rider_objs = list(filter(lambda n: n.bot == False, raw_riders))

                # got the drivers and riders lists
                print(driver_objs)
                print(rider_objs)
                location_data = {}

                # this implementation just has one massive file, probably try to change for per-server in the future
                with open('./server_data/1356468638726492231.pickle', 'rb') as f:
                    location_data = pickle.load(f)
                
                def check(m):
                    return m.author.id == u.id and m.channel == self.recent_chn

                for u in driver_objs:
                    if u.id not in location_data:
                        # TODO: have bot dm, and use reactions + minkyo.gmaps to get the place id
                        await self.recent_chn.send(f'<@{u.id}> Where do you live?')
                        msg = await bot.wait_for('message', check=check)
                        response = gmaps.get_place(msg.content)
                        pIds, addys = gmaps.extract_from_place(response)
                        await self.recent_chn.send(f'Which address looks the most correct?\n'+'\n'.join([f'{i}: {a}' for i, a in enumerate(addys)]))
                        selection = await bot.wait_for('message', check=check)
                        location_data[u.id] = [addys[int(selection.content)], pIds[int(selection.content)], 0]
                    if location_data[u.id][2] == 0:
                        await self.recent_chn.send(f'How many people can you drive?')
                        cap = await bot.wait_for('message', check=check)
                        location_data[u.id] = [location_data[u.id][0], location_data[u.id][1], int(cap.content)]
                
                for u in rider_objs:
                    if u.id not in location_data:
                        # TODO: have bot dm, and use reactions + minkyo.gmaps to get the place id
                        await self.recent_chn.send(f'<@{u.id}> Where do you need to be picked up/dropped off from?')
                        msg = await bot.wait_for('message', check=check)
                        response = gmaps.get_place(msg.content)
                        pIds, addys = gmaps.extract_from_place(response)
                        await self.recent_chn.send(f'Which address looks the most correct?\n'+'\n'.join([f'{i}: {a}' for i, a in enumerate(addys)]))
                        selection = await bot.wait_for('message', check=check)
                        location_data[u.id] = [addys[int(selection.content)], pIds[int(selection.content)], 0]
                
                print(location_data)

                with open('./server_data/1356468638726492231.pickle', 'wb') as f:
                    pickle.dump(location_data, f)

                drivers = [distance.driver(d.nick if d.nick != None else d.user, location_data[d.id][0], location_data[d.id][1], location_data[d.id][2]) for d in driver_objs]
                riders = [distance.rider(r.nick if r.nick != None else r.user, location_data[r.id][0], location_data[r.id][1]) for r in rider_objs]

                for d in drivers:
                    print(d)
                for r in riders:
                    print(r)

                soln = distance.solve(drivers, riders)
                soln.show_distances()
                if soln.solveable():
                    soln.find_routes_greedy()
                    routes = soln.route_to_str()
                    embed=discord.Embed(
                        title='**Rides: 🌞**',
                        description=routes,
                    )
                    await self.recent_chn.send(embed=embed)
                else:
                    await self.recent_chn.send('Number of riders exceeds number of seats.')

                self.recent_msg_id = None
                self.recent_chn = None

    @commands.Cog.listener()
    async def on_message(self, message = discord.Message):
        print(message.content)

async def setup(bot):
    await bot.add_cog(maincog(bot))