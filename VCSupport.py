import discord
from discord import app_commands
from discord.ext import commands
import logging
import pprint

import os
from dotenv import load_dotenv
load_dotenv('.env')
_LRR_R5_ROLE_ID_ = int(os.environ.get('LRR_R5_ROLE_ID'))
_LRR_R4_ROLE_ID_ = int(os.environ.get('LRR_R4_ROLE_ID'))
_LRR_R3_ROLE_ID_ = int(os.environ.get('LRR_R3_ROLE_ID'))
_LRR_MEDITATION_MODERATOR_ROLE_ID_ = int(os.environ.get('LRR_MEDITATION_MODERATOR_ROLE_ID'))


class VCSupportCog(commands.Cog):
    vcs_admin_roles = [
        _LRR_R5_ROLE_ID_,    # LRR::R5
        _LRR_R4_ROLE_ID_,    # LRR::R4
        _LRR_R3_ROLE_ID_,    # LRR::R3
        _LRR_MEDITATION_MODERATOR_ROLE_ID_,    # LRR::寝落ち警備隊
    ]
    
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        super().__init__()
        self.bot = bot
        self.logger = logger
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('VCSupport is ready')
    
    @app_commands.command()
    async def vcs_setstatus(self, ctx, text: str):
        channel = self.bot.get_channel(ctx.channel_id)
        if len(list(filter(lambda role: role.id in VCSupportCog.vcs_admin_roles, ctx.user.roles))) <= 0:
            self.logger.warning(f'[vcs_setstatus: {channel.name}({channel.id})] called by {ctx.user.display_name}({ctx.user.id}) - unauthorized')
            await ctx.response.send_message(f'【{ctx.user.display_name}】はこのコマンドを実行する権限がありません')
            return

        await channel.edit(status=text)
        self.logger.info(f'[set_chstatus: {channel.name}({channel.id})] called by {ctx.user.display_name}({ctx.user.id})')
        await ctx.response.send_message(f'【{ctx.user.display_name}】がチャンネルステータスを設定しました: {text}')
