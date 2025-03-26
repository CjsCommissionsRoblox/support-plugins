import discord
import random
import string
from discord.ext import commands

class ScrambleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Scramble function with salt and randomization
    def scramble_word(self, word):
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=5))  # Salt added
        word_with_salt = word + salt
        scrambled = ''.join(random.sample(word_with_salt, len(word_with_salt)))  # Shuffle letters
        return scrambled

    # Scramble command
    @commands.command(name='scramble')
    async def scramble(self, ctx, *, word: str):
        scrambled_word = self.scramble_word(word)
        await ctx.send(f"Original word: {word}\nScrambled word: {scrambled_word}")

# Setup function to add the cog
def setup(bot):
    bot.add_cog(ScrambleCog(bot))
