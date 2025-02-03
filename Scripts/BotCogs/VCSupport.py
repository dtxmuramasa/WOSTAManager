from discord import app_commands
from discord.ext import commands
import logging

import os
from dotenv import load_dotenv

## 必要な権限
# ・チャンネル全般の権限 > チャンネルを見る
# ・チャンネル全般の権限 > チャンネルの管理
# ・ボイスチャンネル権限 > 接続
# ・ボイスチャンネル権限 > ボイスチャンネルステータスを設定

class VCSupportCog(commands.Cog):    
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        super().__init__()
        self.bot = bot
        self.logger = logger
        load_dotenv('.env')
        self.vcs_admin_roles = []
        for role_id in os.environ.get('VCS_LRR_ADMIN_ROLES').split(','):
            self.vcs_admin_roles.append(int(role_id))
        for role_id in os.environ.get('VCS_KFC_ADMIN_ROLES').split(','):
            self.vcs_admin_roles.append(int(role_id))
        for role_id in os.environ.get('VCS_SV1697_ADMIN_ROLES').split(','):
            self.vcs_admin_roles.append(int(role_id))
        print(self.vcs_admin_roles)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('VCSupport is ready')
        
    async def trySendResponseMessage(self, ctx, message: str, error_message: str) -> bool:
        try:
            await ctx.response.send_message(message)
        except Exception as e:
            self.logger.error(error_message)
            return False
        finally:
            return True
    
    @app_commands.command()
    async def vcs_setstatus(self, ctx, text: str):
        server = self.bot.get_guild(ctx.guild_id)
        channel = self.bot.get_channel(ctx.channel_id)
        if len(list(filter(lambda role: role.id in self.vcs_admin_roles, ctx.user.roles))) <= 0:
            self.logger.warning(f'[vcs_setstatus: {channel.name}({channel.id})] called by {ctx.user.display_name}({ctx.user.id}) - unauthorized')
            _response_message = f'【{ctx.user.display_name}】はこのコマンドを実行する権限がありません'
            _error_message = f'[Error]: Require authorities in server:{server.name}({server.id}) channel:{channel.name}({channel.id}) -> SendMessage'
            await self.trySendResponseMessage(ctx, _response_message, _error_message)
            return
        
        _isSucceedChannelEdit = True
        try:
            await channel.edit(status=text)
        except Exception as e:
            _isSucceedChannelEdit = False
        finally:
            pass
        
        if not _isSucceedChannelEdit:
            self.logger.error(f'[Error]: Require authorities in server:{server.name}({server.id}) channel:{channel.name}({channel.id}) -> DiscoverChannel/ManageChannel/ConnectVoiceChannel/EditVoiceChannelStatus')
            _response_message = f'【{ctx.user.display_name}】がチャンネルステータスを設定できませんでした: {text}\nこの機能ではアプリに対して次の権限が必要です\n - チャンネル全般の権限 > チャンネルを見る\n - チャンネル全般の権限 > チャンネルの管理\n - ボイスチャンネル権限 > 接続\n - ボイスチャンネル権限 > ボイスチャンネルステータスを設定'
            _error_message = f'[Error]: Require authorities in server:{server.name}({server.id}) channel:{channel.name}({channel.id}) -> SendMessage'
            if await self.trySendResponseMessage(ctx, _response_message, _error_message):
                return
        
        self.logger.info(f'[vcs_setstatus: {channel.name}({channel.id})] called by {ctx.user.display_name}({ctx.user.id}) -> {text}')
        _response_message = f'【{ctx.user.display_name}】がチャンネルステータスを設定しました: {text}'
        _error_message = f'[Error]: Require authorities in server:{server.name}({server.id}) channel:{channel.name}({channel.id}) -> SendMessage'
        await self.trySendResponseMessage(ctx, _response_message, _error_message)
        
