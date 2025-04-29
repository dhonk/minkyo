import discord
import dotenv
import os

dotenv.load_dotenv()
token = os.getenv('DISC_API')

print(f'Discord api key: {token}')

# class that stores the actual bot "object"
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(token)