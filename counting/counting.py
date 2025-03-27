import discord
from discord.ext import commands

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.count = 1
        self.last_user = None
        self.counting_channel_id = 1352201669433364550  # Set counting channel ID here
        self.blocked_users = []  # List of blocked users

    def evaluate_math(self, expression):
        """Evaluates a math expression safely."""
        try:
            return eval(expression, {"__builtins__": {}}, {})
        except:
            return None

@commands.command()
async def counting(self, ctx, action: str, number: int):
    """Command to change the expected number."""
    if action.lower() == "number":
        if ctx.author.guild_permissions.administrator:  # Only admins can use this
            self.count = {number} + 1  # Go one past the set number
            await ctx.send(f"The number has been set to ``{self.count}``.")
        else:
            await ctx.send("You do not have permission to use this command.")
    else:
        await ctx.send("Invalid action. Use `-counting number [NUM]`.")


    @commands.command(name="block_user")
    async def block_user(self, ctx, user: discord.User):
        """Block a user from counting."""
        if ctx.author.guild_permissions.administrator:
            if user.id not in [blocked.id for blocked in self.blocked_users]:
                self.blocked_users.append(user)
                await ctx.send(f"``{user.mention}`` has been blocked from counting.")
            else:
                await ctx.send(f"``{user.mention}`` is already blocked from counting.")
        else:
            await ctx.send("You do not have permission to block users.")

    @commands.command(name="unblock_user")
    async def unblock_user(self, ctx, user: discord.User):
        """Unblock a user from counting."""
        if ctx.author.guild_permissions.administrator:
            if user.id in [blocked.id for blocked in self.blocked_users]:
                self.blocked_users = [blocked for blocked in self.blocked_users if blocked.id != user.id]
                await ctx.send(f"``{user.mention}`` has been unblocked and can now count again.")
            else:
                await ctx.send(f"``{user.mention}`` is not blocked.")
        else:
            await ctx.send("You do not have permission to unblock users.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != self.counting_channel_id:
            return

        if message.author.id in [blocked.id for blocked in self.blocked_users]:
            await message.channel.send(f"You are blocked from counting, the number is still ``{self.count}``.")
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
            await message.channel.send(f"``{message.author.mention}`` broke the chain... restarting at ``1``!")
            self.count = 1  # Reset counter
            await message.channel.send("The next number is ``1``.")

async def setup(bot):
    await bot.add_cog(Counting(bot))
