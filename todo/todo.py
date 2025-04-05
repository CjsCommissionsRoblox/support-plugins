import discord
from discord.ext import commands

class TodoList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.todo_list = []

    @commands.command(name="todo")
    async def todo(self, ctx, *, task: str = None):
        if task is None:
            # Show current to-do list if no task is provided
            if not self.todo_list:
                await ctx.send("Your to-do list is empty.")
            else:
                todo_string = "\n".join(f"- {item}" for item in self.todo_list)
                await ctx.send(f"Your to-do list:\n{todo_string}")
        else:
            # Add task to the to-do list
            self.todo_list.append(task)
            await ctx.send(f"Added '{task}' to your to-do list.")

    @commands.command(name="remove_todo")
    async def remove_todo(self, ctx, *, task: str):
        if task in self.todo_list:
            self.todo_list.remove(task)
            await ctx.send(f"Removed '{task}' from your to-do list.")
        else:
            await ctx.send(f"Task '{task}' not found in your to-do list.")

    @commands.command(name="clear_todos")
    async def clear_todos(self, ctx):
        self.todo_list.clear()
        await ctx.send("Your to-do list has been cleared.")

def setup(bot):
    bot.add_cog(TodoList(bot))  # No await here, just a simple registration
