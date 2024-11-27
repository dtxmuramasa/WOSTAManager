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
        # 1/32の確率でサイコロの呪いを受ける
        if(not(str(ctx.user.id) in self.fixed_dices.keys()) and random.randint(0, 32) % 32 == 0):
            self.fixed_dices[str(ctx.user.id)] = random.randint(1, 6)
            self.logger.info(f'[dice_roll 呪い: {self.fixed_dices[str(ctx.user.id)]} > {ctx.user.display_name}({ctx.user.id})] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id})')
            await channel.send(f'【{ctx.user.display_name}】がサイコロの呪いを受けました！！')
        
        # サイコロを振る(呪われていたら固定の数字になる)
        dice = self.fixed_dices.get(str(ctx.user.id), random.randint(1, 6))
        
        # 1/2の確率で芸人サイコロを使う
        if(str(ctx.user.id) in self.fixed_dices.keys() and random.randint(1, 6) >= 4):
            crazy_dice = [0, 7, 100, '勝ち', '勝ち？ｗ', '負け', '圧倒的負け', '『恋の話』、恋バナ～ｗｗｗ', 'ここで一発芸！皆がウケたら勝ち！', CrazyDiceCog.strCancelChallenge]
            dice = crazy_dice[random.randrange(len(crazy_dice))]
            # 1/10の確率でサイコロの解呪チャレンジ
            if(dice == CrazyDiceCog.strCancelChallenge):
                # 1/6の確率で解呪成功
                if(random.randint(1, 6 - self.fixed_dices[str(ctx.user.id)] + 1) % (6 - self.fixed_dices[str(ctx.user.id)] + 1) == 0):
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


