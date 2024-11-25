import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import logging


class TAManagerCog(commands.Cog):    
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        self.bot = bot
        self.logger = logger
        self.ta_list = {}
        self.used_ta_id_list = []
    
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
        self.logger.info(f'[ta_calc_offset] called by {ctx.user.display_name} on {channel.name} - starter_time: {starter_time}, self_time: {self_time}')
        await channel.send(f'【{ctx.user.display_name}】誤差: {offset} 秒')
    
    @app_commands.command()
    async def ta_create(self, ctx, time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        totalSeconds = self.convert2seconds(time)
        newId = self.used_ta_id_list[-1] + 1 if (len(self.used_ta_id_list) > 0) else 0
        self.ta_list[newId] = {ctx.user.id: totalSeconds}
        self.used_ta_id_list.append(newId)
        self.logger.info(f'[ta_create](TAID: {newId}) called by {ctx.user.display_name} on {channel.name} - time: {time}')
        await channel.send(f'【TA発起】{ctx.user.display_name} が TAID: {newId} を発起しました')


    @app_commands.command()
    async def ta_join(self, ctx, ta_id: int, time: int):
        channel = self.bot.get_channel(ctx.channel_id)

        ta = self.ta_list.get(ta_id, None)
        if ta is None:
            self.logger.warning(f'[ta_join] called by {ctx.user.display_name} on {channel.name} TA not found: {ta_id}')
            await channel.send(f'TAが見つかりません: {ta_id}')
            return
        
        self.ta_list[ta_id][ctx.user.id] = self.convert2seconds(time)
        self.logger.info(f'[ta_join] called by {ctx.user.display_name} on {channel.name} - TAID: {ta_id}, time: {time}')
        await channel.send(f'【TA参加】{ctx.user.display_name} が TAID: {ta_id} に参加しました')

    
    @app_commands.command()
    async def ta_decide(self, ctx, ta_id: int, start_time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        
        ta = self.ta_list.get(ta_id, None)
        if ta is None:
            self.logger.warning(f'[ta_join] called by {ctx.user.display_name} on {channel.name} TA not found: {ta_id}')
            await channel.send(f'TAが見つかりません: {ta_id}')
            return
        
        start_time = f'{str(int(start_time / 100)).zfill(2)}:{str(int(start_time % 100)).zfill(2)}:00'
        start_utc = datetime.strptime(start_time, '%H:%M:%S')
        
        sorted_ta = sorted(self.ta_list[ta_id].items(), key = lambda x: x[1], reverse=True)
        starter = sorted_ta.pop(0)

        self.logger.info(f'[ta_decide] called by {ctx.user.display_name} on {channel.name} - TAID: {ta_id}, start_time: {start_time}')
        self.logger.info(f'[ta_decide - starter] {self.getMentionName(starter[0])} march_time: {starter[1]} sec, start at {start_utc}')
        await channel.send(f'【TAID: {ta_id} - スターター】{self.getMentionName(starter[0])} **{start_utc.strftime('%H:%M:%S')} スタート** 行軍時間: {starter[1]} 秒', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        for user_id, time in sorted_ta:
            user_mention_name = self.getMentionName(user_id)
            user_display_name = self.getUserDisplayName(user_id)
            td = timedelta(seconds=starter[1] - time)
            joiner_start_utc = (start_utc + td).strftime('%H:%M:%S')
            self.logger.info(f'[ta_decide - joiner] {user_display_name}({user_id}) march_time: {time} sec, start at {joiner_start_utc}')
            await channel.send(f'【TAID: {ta_id} - 参加者】{user_mention_name} **{joiner_start_utc} スタート** (元の行軍時間: {time} 秒)', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        self.logger.info(f'[ta_decide - finalize:0] TAID: {ta_id} is finalize')
        self.logger.info(self.ta_list[ta_id])
        del self.ta_list[ta_id]
        self.logger.info(f'[ta_decide - finalize:1] TAID: {ta_id} is deleted')
