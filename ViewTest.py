import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import logging

class TestView(discord.ui.View):
    def __init__(self, logger: logging.Logger):
        super().__init__(timeout=180)
        self.logger = logger
    
    @discord.ui.button(label='TAに参加', style=discord.ButtonStyle.success)
    async def test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.logger.info(f'[test_button] called by {interaction.user.display_name}({interaction.user.id})')
        await interaction.response.send_message('Button clicked!', ephemeral=True)


class ViewTestCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        self.bot = bot
        self.logger = logger
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('ViewTestCog is ready')
    
    @app_commands.command()
    async def create_view_test(self, ctx):
        channel = self.bot.get_channel(ctx.channel_id)
        self.logger.info(f'[create_view_test] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id})')
        view = TestView(self.logger)
        await ctx.response.send_message(view=view)
