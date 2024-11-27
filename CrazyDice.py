import discord
from discord import app_commands
from discord.ext import commands
import logging
import random
import pprint


class CrazyDiceCog(commands.Cog):
    strCancelChallenge = 'サイコロの呪い解除チャレーンジ！！結果は～...'
    
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        super().__init__()
        self.bot = bot
        self.logger = logger
        random.seed()
        self.fixed_dices = {}
        
    def getMentionName(self, user_id: str):
        user = self.bot.get_user(user_id)
        return user.mention
    
    def getUserDisplayName(self, user_id: str):
        user = self.bot.get_user(user_id)
        return user.display_name
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('CrazyDiceCog is ready')
        
    @app_commands.command()
    async def dice_roll(self, ctx):
        channel = self.bot.get_channel(ctx.channel_id)
        dice = self.fixed_dices.get(str(ctx.user.id), random.randint(1, 6))
        if(str(ctx.user.id) in self.fixed_dices.keys() and random.randint(1, 6) >= 4):
            crazy_dice = [0, 7, 100, '勝ち', '負け', 'ここで一発芸！皆がウケたら勝ち！', CrazyDiceCog.strCancelChallenge]
            dice = crazy_dice[random.randrange(len(crazy_dice))]
            if(dice == CrazyDiceCog.strCancelChallenge):
                if(random.randint(1, 6) >= 5):
                    self.fixed_dices.pop(str(ctx.user.id))
                    dice = dice + '成功！！！！'
                    await channel.send(f'【{ctx.user.display_name}】がサイコロの呪いを解除しました！！')
                else:
                    dice = dice + '失敗！！ｗｗｗ'
        self.logger.info(f'[dice_roll: {dice}] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id})')
        await ctx.response.send_message(f'【{ctx.user.display_name}】サイコロを振りました: {dice}', silent=True)
    
    @app_commands.command()
    async def dice_fixer(self, ctx, user_id: str, dice: int):
        channel = self.bot.get_channel(ctx.channel_id)
        # target_user_name = self.getUserDisplayName(user_id)
        self.fixed_dices[user_id] = dice
        # self.logger.info(f'[dice_fixer: {dice} > {target_user_name}({user_id})] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - user: {user_id}')
        # await ctx.response.send_message(f'【{ctx.user.display_name}】が{target_user_name}({user_id})のサイコロを{dice}に固定しました')
        self.logger.info(f'[dice_fixer: {dice} > {user_id}] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - user: {user_id}')
        await ctx.response.send_message(f'【{ctx.user.display_name}】が{user_id}のサイコロを{dice}に固定しました')
        
    @app_commands.command()
    async def dice_unfixer(self, ctx, user_id: str):
        channel = self.bot.get_channel(ctx.channel_id)
        # target_user_name = self.getUserDisplayName(user_id)
        self.fixed_dices.pop(user_id)
        # self.logger.info(f'[dice_unfixer: {target_user_name}({user_id})] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - user: {user_id}')
        # await ctx.response.send_message(f'【{ctx.user.display_name}】が{target_user_name}({user_id})のサイコロ固定を解除しました')
        self.logger.info(f'[dice_unfixer: {user_id}] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) - user: {user_id}')
        await ctx.response.send_message(f'【{ctx.user.display_name}】が{user_id}のサイコロ固定を解除しました')


