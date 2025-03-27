import discord
from discord.ext import commands

class AntiGhostPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1350802717194326019  # Hardcoded log channel ID

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.mentions and not message.author.bot:  # Check if mentions exist
            log_channel = self.bot.get_channel(self.log_channel_id)

            if log_channel:
                embed = discord.Embed(
                    title="🚨 Ghost Ping Detected!",
                    description=f"**User:** {message.author.mention} ({message.author.id})\n"
                                f"**Mentioned:** {' '.join(m.mention for m in message.mentions)}",
                    color=discord.Color.red()
                )
                embed.set_footer(text=f"Deleted in #{message.channel.name}")
                await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiGhostPing(bot))
