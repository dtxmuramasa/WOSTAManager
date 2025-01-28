import discord
from discord import app_commands
from discord.ext import commands
import logging
from Models import TADB
from Models import NormalizedWoSTime
from typing import Union

class TAManagerCog(commands.Cog):
    ALLOW_TIME_FORMAT = NormalizedWoSTime.NormalizedWoSTime.ALLOW_FORMAT
    
    def __init__(self, bot: commands.Bot, tadb: TADB.TADatabase, logger: logging.Logger):
        self.bot = bot
        self.tadb = tadb
        self.logger = logger
    
    def getMentionName(self, user_id: str):
        user = self.bot.get_user(user_id)
        return user.mention
    
    def getUserDisplayName(self, user_id: int):
        user = self.bot.get_user(user_id)
        return user.display_name
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('TAManagerCog is ready')


    @app_commands.command(description='2つの時刻AとBの時間差を計算します')
    @app_commands.describe(a_time=f'時刻A {ALLOW_TIME_FORMAT}', b_time=f'時刻B {ALLOW_TIME_FORMAT}')
    async def calc_offset(self, ctx, a_time: str, b_time: str):
        channel = self.bot.get_channel(ctx.channel_id)
        a = NormalizedWoSTime.CreateNormalizedWoSTime(a_time)
        b = NormalizedWoSTime.CreateNormalizedWoSTime(b_time)
        if a.convertToSeconds() >= b.convertToSeconds():
            offset_seconds = (a - b).convertToSeconds()
            self.logger.info(f'[ta_calc_offset] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - A: {a_time}, B: {b_time} -> offset_seconds: {offset_seconds}')
            await ctx.response.send_message(f'【{ctx.user.display_name}】A[{a.getFullUTCFormat()}] - B[{b.getFullUTCFormat()}] -> 誤差: {offset_seconds} 秒')
        else:
            offset_seconds = (b - a).convertToSeconds()
            self.logger.info(f'[ta_calc_offset] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - B: {b_time}, A: {a_time} -> offset_seconds: {offset_seconds}')
            await ctx.response.send_message(f'【{ctx.user.display_name}】B[{b.getFullUTCFormat()}] - A[{a.getFullUTCFormat()}] -> 誤差: {offset_seconds} 秒')

        
    @app_commands.command(description='現在時刻と行軍時間から着弾時刻を計算します')
    @app_commands.describe(start_time=f'現在時刻 {ALLOW_TIME_FORMAT}', march_time=f'行軍時間 {ALLOW_TIME_FORMAT}')
    async def calc_arrival(self, ctx, start_time: str, march_time: str):
        channel = self.bot.get_channel(ctx.channel_id)
        marchTime = NormalizedWoSTime.CreateNormalizedWoSTime(march_time, self.logger)
        startTime = NormalizedWoSTime.CreateNormalizedWoSTime(start_time, self.logger)
        arrivalTime = startTime + marchTime
        self.logger.info(f'[ta_calc_arrival] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - start_time: {start_time}, march_time: {march_time} -> arrival_time: {arrivalTime.getFullUTCFormat()}')
        await ctx.response.send_message(f'【{ctx.user.display_name}】UTC[{startTime.getFullUTCFormat()}] + 行軍時間[{marchTime.getFullUTCFormat()}] -> 到着予定時刻: {arrivalTime.getFullUTCFormat()}')


    @app_commands.command(description='目標着弾時刻と行軍時間から集結開始時刻を計算します')
    @app_commands.describe(target_time=f'目標着弾時刻 {ALLOW_TIME_FORMAT}', march_time=f'行軍時間 {ALLOW_TIME_FORMAT}', prepare_time=f'集結時間 {ALLOW_TIME_FORMAT}')
    async def calc_start_timing(self, ctx, target_time: str, march_time: str, prepare_time: str = '500'):
        channel = self.bot.get_channel(ctx.channel_id)
        marchTime = NormalizedWoSTime.CreateNormalizedWoSTime(march_time, self.logger)
        targetTime = NormalizedWoSTime.CreateNormalizedWoSTime(target_time, self.logger)
        prepareTime = NormalizedWoSTime.CreateNormalizedWoSTime(prepare_time, self.logger)
        startTime = targetTime - marchTime - prepareTime
        self.logger.info(f'[ta_calc_stat_timing] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - target_time: {target_time}, march_time: {march_time}, prepare_time: {prepare_time} -> start_time: {startTime.getFullUTCFormat()}')
        await ctx.response.send_message(f'【{ctx.user.display_name}】行軍開始時刻 UTC[{startTime.getFullUTCFormat()}] 集結時間[{prepareTime.getMinutesFromString()} 分] - 行軍時間[{marchTime.getFullUTCFormat()}] -> 到達時刻: UTC[{targetTime.getFullUTCFormat()}]')

    
    @app_commands.command(description='連集結を発起します')
    @app_commands.describe(march_time=f'行軍時間 {ALLOW_TIME_FORMAT}')
    async def ta_create(self, ctx, march_time: str):
        channel = self.bot.get_channel(ctx.channel_id)
        normalizedTime = NormalizedWoSTime.CreateNormalizedWoSTime(march_time, self.logger)
        newId = self.tadb.CreateTA(ctx.guild.id, ctx.channel_id, ctx.user.id, normalizedTime.convertToSeconds())
        self.logger.info(f'[ta_create](TAID: {newId}) called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - march_time: {march_time}')
        # view = TAManager_JoinButtonView(timeout=180, logger=self.logger, taManager=self, taid=newId)
        # await ctx.response.send_message(f'【TA発起】{ctx.user.display_name} が TAID: {newId} を発起しました', view=view)
        await ctx.response.send_message(f'【TA発起】{ctx.user.display_name} が TAID: {newId} を発起しました')


    @app_commands.command(description='連集結に参加します')
    @app_commands.describe(ta_id='参加する連集結のTAID', march_time=f'行軍時間 {ALLOW_TIME_FORMAT}')
    async def ta_join(self, ctx, ta_id: int, march_time: str):
        channel = self.bot.get_channel(ctx.channel_id)
        normalizedTime = NormalizedWoSTime.CreateNormalizedWoSTime(march_time, self.logger)
        if not self.tadb.IsExistTA(ta_id):
            self.logger.warning(f'[ta_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return
        
        self.tadb.JoinTA(ta_id, ctx.guild.id, ctx.channel_id, ctx.user.id, normalizedTime.convertToSeconds())
        self.logger.info(f'[ta_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}, march_time: {march_time}')
        await ctx.response.send_message(f'【TA参加】{ctx.user.display_name} が TAID: {ta_id} に参加しました')


    @app_commands.command(description='連集結に他のプレイヤーを招集します')
    @app_commands.describe(ta_id='招集する連集結のTAID', user='招集するプレイヤー', march_time=f'招集するプレイヤーの行軍時間 {ALLOW_TIME_FORMAT}')
    async def ta_invite(self, ctx, ta_id: int, user: Union[discord.User, discord.Member], march_time: str):
        user_id = user.id
        channel = self.bot.get_channel(ctx.channel_id)
        normalizedTime = NormalizedWoSTime.CreateNormalizedWoSTime(march_time, self.logger)
        if not self.tadb.IsExistTA(ta_id):
            self.logger.warning(f'[ta_proxy_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return
        
        self.tadb.JoinTA(ta_id, ctx.guild.id, ctx.channel_id, user_id, normalizedTime.convertToSeconds())
        self.logger.info(f'[ta_proxy_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}, user_id: {user_id}, march_time: {march_time}')
        await ctx.response.send_message(f'【TA招集】{user.display_name} が {ctx.user.display_name} によって TAID: {ta_id} に招集されました')


    @app_commands.command(description='連集結から離脱します')
    @app_commands.describe(ta_id='離脱する連集結のTAID')
    async def ta_leave(self, ctx, ta_id: int):
        channel = self.bot.get_channel(ctx.channel_id)
        if not self.tadb.IsExistTA(ta_id):
            self.logger.warning(f'[ta_leave] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return

        self.tadb.LeaveTA(ta_id, ctx.guild.id, channel.id, ctx.user.id)
        self.logger.info(f'[ta_leave] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}')
        await ctx.response.send_message(f'【TA離脱】{ctx.user.display_name} が TAID: {ta_id} から離脱しました')


    @app_commands.command(description='連集結から他のプレイヤーをキックします')
    @app_commands.describe(ta_id='キックする連集結のTAID', user='キックするプレイヤー')
    async def ta_kick(self, ctx, ta_id: int, user: Union[discord.User, discord.Member]):
        user_id = user.id
        channel = self.bot.get_channel(ctx.channel_id)
        if not self.tadb.IsExistTA(ta_id):
            self.logger.warning(f'[ta_kick] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return
        
        self.tadb.LeaveTA(ta_id, ctx.guild.id, channel.id, user_id)
        self.logger.info(f'[ta_kick] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}, user_id: {user_id}')
        await ctx.response.send_message(f'【TAキック】{self.getUserDisplayName(user_id)} が {ctx.user.display_name} によって TAID: {ta_id} からキックされました')


    @app_commands.command(description='連集結の参加者を確定し、参加者に集結開始時刻を通知します')
    @app_commands.describe(ta_id='確定する連集結のTAID', start_time=f'連集結開始時刻 {ALLOW_TIME_FORMAT}')
    async def ta_decide(self, ctx, ta_id: int, start_time: str):
        channel = self.bot.get_channel(ctx.channel_id)
        if not self.tadb.IsExistTA(ta_id):
            self.logger.warning(f'[ta_join] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return

        normalizedStartTime = NormalizedWoSTime.CreateNormalizedWoSTime(start_time, self.logger)
        starter_start_utc = normalizedStartTime.getFullUTCFormat()
        
        ta = self.tadb.CloseTA(ta_id)
        sorted_ta = sorted(ta.items(), key = lambda x: x[1], reverse=True)
        starter = sorted_ta.pop(0)

        self.logger.info(f'[ta_decide] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}, start_time: {start_time}')
        self.logger.info(f'[ta_decide - TAID: {ta_id} starter] {self.getUserDisplayName(starter[0])}({starter[0]}) march_time: {starter[1]} sec, start at {starter_start_utc}')
        await channel.send(f'【TAID: {ta_id} - スターター】{self.getMentionName(starter[0])} **{starter_start_utc} スタート** 行軍時間: {starter[1]} 秒', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        for user_id, march_time in sorted_ta:
            user_mention_name = self.getMentionName(user_id)
            user_display_name = self.getUserDisplayName(user_id)
            joiner_offset_time = NormalizedWoSTime.CreateNormalizedWoSTimeFromSeconds(starter[1] - march_time, self.logger)
            joiner_start_time = normalizedStartTime + joiner_offset_time
            joiner_start_utc = joiner_start_time.getFullUTCFormat()
            self.logger.info(f'[ta_decide - TAID: {ta_id} joiner] {user_display_name}({user_id}) march_time: {march_time} sec, start at {joiner_start_utc}')
            await channel.send(f'【TAID: {ta_id} - 参加者】{user_mention_name} **{joiner_start_utc} スタート** (元の行軍時間: {march_time} 秒)', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        await ctx.response.send_message(f'【TAクローズ】TAID: {ta_id} が {ctx.user.display_name} によってクローズされました')
        self.logger.info(f'[ta_decide - finalize:0] TAID: {ta_id} is finalized')
    
    
    @app_commands.command(description='連集結を解散します')
    @app_commands.describe(ta_id='解散する連集結のTAID')
    async def ta_cancel(self, ctx, ta_id: int):
        channel = self.bot.get_channel(ctx.channel_id)
        if not self.tadb.IsExistTA(ta_id):
            self.logger.warning(f'[ta_cancel] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) TA not found: {ta_id}')
            await ctx.response.send_message(f'TAが見つかりません: {ta_id}')
            return
        
        self.tadb.CloseTA(ta_id)
        self.logger.info(f'[ta_cancel] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - TAID: {ta_id}')
        await ctx.response.send_message(f'【TAキャンセル】TAID: {ta_id} が {ctx.user.display_name} によってキャンセルされました')
        self.logger.info(f'[ta_cancel - finalize:0] TAID: {ta_id} is finalized')


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
