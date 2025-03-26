import discord
import random
import string
from discord.ext import commands

class ScrambleCog(commands.Cog):
    """Scrambles a given word and returns a randomized version."""
    
    def __init__(self, bot):
        self.bot = bot

    def scramble_word(self, word):
        """Scrambles the given word with a salt for added complexity."""
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=5))  # Salt added
        word_with_salt = word + salt
        scrambled = ''.join(random.sample(word_with_salt, len(word_with_salt)))  # Shuffle letters
        return scrambled

    @commands.command(name='scramble')
    async def scramble(self, ctx, *, word: str):
        """Scrambles the word provided by the user."""
        if word:
            scrambled_word = self.scramble_word(word)
            await ctx.send(f"Original word: {word}\nScrambled word: {scrambled_word}")
        else:
            await ctx.send("Please provide a word to scramble!")

async def setup(bot):
    """Sets up the ScrambleCog in the bot."""
    await bot.add_cog(ScrambleCog(bot))
