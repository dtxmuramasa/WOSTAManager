import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta


class TAManagerCog(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot
        self.ta_list = {}
    
    def convert2seconds(self, time: int):
        minutes = (time - (time % 100)) / 100
        return int(minutes * 60 + time % 100)
    
    def getMentionName(self, name: str):
        user = self.bot.get_user(name)
        print(user)
        return user.mention
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('TAManagerCog is ready')

    @app_commands.command()
    async def ta_calc_offset(self, ctx, starter_time: int, self_time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        starter_totalSeconds = self.convert2seconds(starter_time)
        self_totalSeconds = self.convert2seconds(self_time)
        offset = int(self_totalSeconds - starter_totalSeconds)
        await channel.send(f'【{ctx.user.display_name}】誤差: {offset} 秒')
    
    @app_commands.command()
    async def ta_create(self, ctx, time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        totalSeconds = self.convert2seconds(time)
        newId = len(self.ta_list)
        print(f'TAを発起しました: [{newId}] = [{ctx.user.id}: {totalSeconds}]')
        self.ta_list[newId] = {ctx.user.id: totalSeconds}
        await channel.send(f'【TA発起】{ctx.user.display_name} が TAID: {newId} を発起しました')


    @app_commands.command()
    async def ta_join(self, ctx, ta_id: int, time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        
        ta = self.ta_list.get(ta_id, None)
        print(ta)
        if ta is None:
            print(f'TAが見つかりません: {ta_id}')
            await channel.send(f'TAが見つかりません: {ta_id}')
            return
        
        self.ta_list[ta_id][ctx.user.id] = self.convert2seconds(time)
        print(f'参加しました: [{ta_id}] {self.ta_list.get(ta_id)}')
        await channel.send(f'【TA参加】{ctx.user.display_name} が TAID: {ta_id} に参加しました')

    
    @app_commands.command()
    async def ta_decide(self, ctx, ta_id: int, start_time: int):
        channel = self.bot.get_channel(ctx.channel_id)
        
        ta = self.ta_list.get(ta_id, None)
        if ta is None:
            print(f'TAが見つかりません: {ta_id}')
            await channel.send(f'TAが見つかりません: {ta_id}')
            return
        
        start_time = f'{str(int(start_time / 100)).zfill(2)}:{str(int(start_time % 100)).zfill(2)}:00'
        start_utc = datetime.strptime(start_time, '%H:%M:%S')
        
        sorted_ta = sorted(self.ta_list[ta_id].items(), key = lambda x: x[1], reverse=True)
        starter = sorted_ta.pop(0)
        
        print(f'TA確定: {ta}')
        await channel.send(f'【TAID: {ta_id} - スターター】{self.getMentionName(starter[0])} **{start_utc.strftime('%H:%M:%S')} スタート** 行軍時間: {starter[1]} 秒', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        for user_id, time in sorted_ta:
            td = timedelta(seconds=starter[1] - time)
            print(f'【参加者】{self.getMentionName(user_id)} 行軍時間: {time} 秒')
            await channel.send(f'【TAID: {ta_id} - 参加者】{self.getMentionName(user_id)} **{(start_utc + td).strftime('%H:%M:%S')} スタート** (元の行軍時間: {time} 秒)', allowed_mentions=discord.AllowedMentions.all(), mention_author=True)
        
        del self.ta_list[ta_id]
