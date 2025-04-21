# made for cj_daboi36 on discord

import discord
import asyncio
import datetime

from discord.ext import commands
from core import checks
from core.models import PermissionLevel

class Counting(commands.Cog):
    """
    A cog for a counting game in a Discord channel. Users must count up by 1 each message.
    If someone posts the wrong number or counts twice in a row, the count resets.
    """
    default_global = {
        "counting_channel_id": None,
        "current_number": 0,
        "last_user_id": None,
        "high_score": 0,  # Track highest number reached
        "high_score_user": None,  # Track user who reached high score
        "last_reset_time": None,  # Timestamp of last reset
        "allowed_roles": [],  # Restrict counting to certain roles
        "reset_message": None,  # Customizable reset message
        "counting_enabled": True,  # Toggle the game on/off
    }

    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()  # To prevent race conditions
        self.db = bot.api.get_plugin_partition(self)
        self.global_config = None

    async def cog_load(self):
        self.global_config = await self.db.find_one({"_id": "counting"})
        if self.global_config is None:
            self.global_config = self.default_global
            await self.config_update()
            self.global_config = await self.db.find_one({"_id": "counting"})

    async def config_update(self):
        await self.db.find_one_and_update(
            {"_id": "counting"},
            {"$set": self.global_config},
            upsert=True,
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
        # Only operate in the configured channel
        if not self.global_config or self.global_config.get("counting_channel_id") is None:
            return
        if not self.global_config.get("counting_enabled", True):
            return
        if message.channel.id != self.global_config["counting_channel_id"]:
            return
        # Restrict to allowed roles if set
        allowed_roles = self.global_config.get("allowed_roles", [])
        if allowed_roles:
            if not any(role.id in allowed_roles for role in getattr(message.author, "roles", [])):
                return
        # Check if the message is a number
        try:
            number = int(message.content.strip())
        except ValueError:
            return  # Ignore non-number messages

        async with self.lock:
            # Check if the same user is counting twice
            if message.author.id == self.global_config["last_user_id"]:
                await self.reset_count(message.channel, reason=f"{message.author.mention} counted twice in a row!")
                return
            # Check if the number is correct
            if number != self.global_config["current_number"] + 1:
                await self.reset_count(message.channel, reason=f"{message.author.mention} counted incorrectly! (Expected {self.global_config['current_number'] + 1})")
                return
            # All good, increment
            self.global_config["current_number"] = number
            self.global_config["last_user_id"] = message.author.id
            # Update high score if needed
            if number > self.global_config.get("high_score", 0):
                self.global_config["high_score"] = number
                self.global_config["high_score_user"] = message.author.id
            await self.config_update()

    async def reset_count(self, channel, reason=None):
        self.global_config["current_number"] = 0
        self.global_config["last_user_id"] = None
        self.global_config["last_reset_time"] = datetime.datetime.utcnow().isoformat()
        await self.config_update()
        # Respect Discord rate limits: avoid spamming
        await asyncio.sleep(1)
        reset_msg = self.global_config.get("reset_message")
        if reset_msg:
            msg = reset_msg.format(reason=reason or "", high_score=self.global_config.get("high_score", 0))
        else:
            msg = f"Count has been reset. {reason if reason else ''} Start again from 1!"
        embed = discord.Embed(description=msg, color=discord.Color.red())
        await channel.send(embed=embed)

    @commands.group(name="count", invoke_without_command=True)
    async def count_group(self, ctx):
        """Counting game settings and status."""
        embed = discord.Embed(
            title="Counting Game",
            description="Use a subcommand: `setchannel`, `enable`, `allowedroles`, `resetmessage`, `status`",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @count_group.command(name="setchannel")
    @checks.has_permissions(PermissionLevel.MOD)
    async def set_counting_channel(self, ctx):
        """Set the current channel as the counting channel."""
        self.global_config["counting_channel_id"] = ctx.channel.id
        self.global_config["current_number"] = 0
        self.global_config["last_user_id"] = None
        await self.config_update()
        embed = discord.Embed(
            description=f"Counting channel set to {ctx.channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @count_group.command(name="enable")
    @checks.has_permissions(PermissionLevel.MOD)
    async def enable_counting(self, ctx, enabled: bool = True):
        """Enable or disable counting game."""
        self.global_config["counting_enabled"] = enabled
        await self.config_update()
        embed = discord.Embed(
            description=f"Counting enabled: {enabled}",
            color=discord.Color.green() if enabled else discord.Color.red()
        )
        await ctx.send(embed=embed)

    @count_group.command(name="allowedroles")
    @checks.has_permissions(PermissionLevel.MOD)
    async def set_allowed_roles(self, ctx, *roles: discord.Role):
        """Restrict counting to specific roles (mention the roles). Empty to allow all."""
        self.global_config["allowed_roles"] = [role.id for role in roles]
        await self.config_update()
        if roles:
            embed = discord.Embed(
                description=f"Allowed roles set: {', '.join(role.mention for role in roles)}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description="All roles can count now.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

    @count_group.command(name="resetmessage")
    @checks.has_permissions(PermissionLevel.MOD)
    async def set_reset_message(self, ctx, *, message: str = None):
        """Set a custom reset message. Use {reason} and {high_score} as placeholders. Empty to reset to default."""
        self.global_config["reset_message"] = message
        await self.config_update()
        if message:
            embed = discord.Embed(
                description="Custom reset message set.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description="Reset message reverted to default.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

    @count_group.command(name="status")
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def count_status(self, ctx):
        """Show the current count, last user, and high score."""
        user = f"<@{self.global_config['last_user_id']}>" if self.global_config.get("last_user_id") else "None"
        high_score_user = f"<@{self.global_config['high_score_user']}>" if self.global_config.get("high_score_user") else "None"
        # Format last reset as Discord timestamp
        last_reset_iso = self.global_config.get('last_reset_time')
        if last_reset_iso:
            try:
                dt = datetime.datetime.fromisoformat(last_reset_iso)
                unix_ts = int(dt.timestamp())
                last_reset_disp = f"<t:{unix_ts}:f>"
            except Exception:
                last_reset_disp = last_reset_iso
        else:
            last_reset_disp = "Never"
        embed = discord.Embed(
            title="Counting Game Status",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Current Number", value=str(self.global_config.get('current_number', 0)), inline=False)
        embed.add_field(name="Last User", value=user, inline=False)
        embed.add_field(name="High Score", value=f"{self.global_config.get('high_score', 0)} by {high_score_user}", inline=False)
        embed.add_field(name="Last Reset", value=last_reset_disp, inline=False)
        embed.add_field(name="Counting Enabled", value=str(self.global_config.get('counting_enabled', True)), inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Counting(bot))
