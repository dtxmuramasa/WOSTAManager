import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import logging
import TADB


class TAManagerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, tadb: TADB.TADatabase, logger: logging.Logger):
        self.bot = bot
        self.tadb = tadb
        self.logger = logger
    
    def convert2seconds(self, time: int):
        minutes = (time - (time % 100)) / 100
        return int(minutes * 60 + time % 100)
    
    def getMentionName(self, user_id: str):
        user = self.bot.get_user(user_id)
        return user.mention
    
    def getUserDisplayName(self, user_id: int):
        user = self.bot.get_user(user_id)
        return user.display_name
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('TAManagerCog is ready')

    @app_commands.command()
    async def ta_calc_offset(self, ctx, starter_time: int, self_time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        starter_totalSeconds = self.convert2seconds(starter_time)
        self_totalSeconds = self.convert2seconds(self_time)
        offset = int(self_totalSeconds - starter_totalSeconds)
        self.logger.info(f'[ta_calc_offset] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - starter_time: {starter_time}, self_time: {self_time}')
        await ctx.response.send_message(f'【{ctx.user.display_name}】誤差: {offset} 秒')
    
    @app_commands.command()
    async def ta_create(self, ctx, time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        totalSeconds = self.convert2seconds(time)
        newId = self.tadb.CreateTA(ctx.guild.id, ctx.channel_id, ctx.user.id, totalSeconds)
        self.logger.info(f'[ta_create](TAID: {newId}) called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - time: {time}')
        view = TAManager_JoinButtonView(timeout=180, logger=self.logger, taManager=self, taid=newId)
        await ctx.response.send_message(f'【TA発起】{ctx.user.display_name} が TAID: {newId} を発起しました', view=view)
        # await ctx.response.send_message(f'【TA発起】{ctx.user.display_name} が TAID: {newId} を発起しました')


    @app_commands.command()
    async def ta_join(self, ctx, ta_id: int, time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        if self.tadb.IsExistTA(ta_id) is None:
            self.logger.warning(f'[ta_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return
        
        self.tadb.JoinTA(ta_id, ctx.guild.id, ctx.channel_id, ctx.user.id, self.convert2seconds(time))
        self.logger.info(f'[ta_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}, time: {time}')
        await ctx.response.send_message(f'【TA参加】{ctx.user.display_name} が TAID: {ta_id} に参加しました')

    
    @app_commands.command()
    async def ta_decide(self, ctx, ta_id: int, start_time: int):
        channel = self.bot.get_channel(ctx.channel_id)

        if self.tadb.IsExistTA(ta_id) is None:
            self.logger.warning(f'[ta_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return
                
        start_time = f'{str(int(start_time / 100)).zfill(2)}:{str(int(start_time % 100)).zfill(2)}:00'
        start_utc = datetime.strptime(start_time, '%H:%M:%S')
        starter_start_utc = start_utc.strftime('%H:%M:%S')
        
        ta = self.tadb.CloseTA(ta_id)
        sorted_ta = sorted(ta.items(), key = lambda x: x[1], reverse=True)
        starter = sorted_ta.pop(0)

        self.logger.info(f'[ta_decide] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}, start_time: {start_time}')
        self.logger.info(f'[ta_decide - TAID: {ta_id} starter] {self.getUserDisplayName(starter[0])}({starter[0]}) march_time: {starter[1]} sec, start at {starter_start_utc}')
        await channel.send(f'【TAID: {ta_id} - スターター】{self.getMentionName(starter[0])} **{starter_start_utc} スタート** 行軍時間: {starter[1]} 秒', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        for user_id, time in sorted_ta:
            user_mention_name = self.getMentionName(user_id)
            user_display_name = self.getUserDisplayName(user_id)
            td = timedelta(seconds=starter[1] - time)
            joiner_start_utc = (start_utc + td).strftime('%H:%M:%S')
            self.logger.info(f'[ta_decide - TAID: {ta_id} joiner] {user_display_name}({user_id}) march_time: {time} sec, start at {joiner_start_utc}')
            await channel.send(f'【TAID: {ta_id} - 参加者】{user_mention_name} **{joiner_start_utc} スタート** (元の行軍時間: {time} 秒)', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        await ctx.response.send_message(f'【TAクローズ】TAID: {ta_id} が {ctx.user.display_name} によってクローズされました')
        self.logger.info(f'[ta_decide - finalize:0] TAID: {ta_id} is finalized')


class TAManager_JoinButtonView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180,
                    logger: logging.Logger, taManager: TAManagerCog, taid: int):
        super().__init__(timeout=timeout)
        self.logger = logging.getLogger('discord')
        self.taManager = taManager
        self.taid = taid
    
    @discord.ui.button(label='TAに参加(機能実装中)', style=discord.ButtonStyle.success)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.logger.info(f'[join_button] called by {interaction.user.display_name}({interaction.user.id})')
        await self.taManager.ta_join(interaction, self.taid, 0)
        await interaction.response.send_message('Button clicked!', ephemeral=True)
