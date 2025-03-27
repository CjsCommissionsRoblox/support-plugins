import discord
from discord.ext import commands

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.count = 1
        self.last_user = None
        self.counting_channel_id = 1352201669433364550  # Set counting channel ID here

    def evaluate_math(self, expression):
        """Evaluates a math expression safely."""
        try:
            return eval(expression, {"__builtins__": {}}, {})
        except:
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != self.counting_channel_id:
            return
        
        content = message.content.strip()

        # Check if it's a number or a math expression
        if content.isdigit():
            number = int(content)
        else:
            number = self.evaluate_math(content)

        # Validate the count
        if number == self.count:
            self.count += 1
            self.last_user = message.author
            await message.add_reaction("✅")  # React with a tick
        else:
            await message.channel.send(f"``{message.author.mention}`` broke the chain... restarting at `1``!")
            self.count = 1  # Reset counter
            await message.channel.send("The next number is ``1``.")

async def setup(bot):
    await bot.add_cog(Counting(bot))
