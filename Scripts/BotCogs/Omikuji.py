from discord import app_commands
from discord.ext import commands
import logging
import random


class OmikujiCog(commands.Cog):
    omikuji_map = [
        '大吉',
        '吉',
        '中吉',
        '小吉',
        '末吉',
        '凶',
        '大凶',
    ]
    
    omikuji_unsei_map = {
        '大吉': 'これまでの努力が実を結ぶ\n現状がピークなので維持を心がけるべき',
        '吉': '大吉に次いで良い運勢\n下降の可能性が低い安定した運気',
        '中吉': '吉の半分の運勢\n努力次第で運気上昇の可能性あり',
        '小吉': '良くも悪くもない運勢\n小さな幸せで停滞',
        '末吉': '「吉」の中では最も劣る運勢\nこれから吉に向かう可能性あり',
        '凶': '運勢としては良くはない\n気を引き締めて物事にあたるとよい',
        '大凶': '最も良くない運勢\nむやみに動かず力を備えてチャンスの到来を待つとよい',
    }
    
    omikuji_ganbo_map = [
        '総じて叶いやすい',
        '慎重に事を運べば望み通りとなる',
        '多く望まなければ叶う',
        '急がず着実に進めば良き結果となる',
        '忍耐を持って進めば次第に叶う',
        '焦ることなかれ\n機は来る',
        '力を合わせればきっと叶う',
        '叶うまで時間がかかる',
        '膨らませるは自由\n叶うはあなた次第',
    ]
    
    omikuji_gakugyo_map = [
        '努力が実を結び周りからの信頼を得られる\n新しい挑戦も吉',
        '一歩一歩の積み重ねが確かな成果となる\n焦らず前進すべし',
        '地道な努力が実を結び少しずつ前進する\n基礎を固めることが吉',
        '努力が報われる時期 焦らず着実に進むことが吉',
        '困難に直面しますが諦めずに進めば道は開かれる',
    ]
    
    omikuji_renai_map = [
        '迷うことなかれ\n心に決めた人が最上',
        '良き出会いあり\n誠実な心で接すれば想いは必ず通じる',
        '年齢などにとらわれる必要なし',
        '縁は近くにあり\n自然な心で接すれば良き関係が築ける',
        '告白はしばらく待て',
        '一時の感情に流されず真心を持って接すれば良き方向へ向かう',
        '焦らず自然に任せれば良き出会いあり\n誠実さを忘れずべからず',
    ]
    
    omikuji_kenko_map = [
        '健やかな日々が続く\n適度な運動を心がければ更なる活力を得る',
        '平安な日々が続く\n規則正しい生活を心がけ心身の調和を保つべし',
        '普段の生活に気を配り軽い運動を心がければ健やかに過ごせる',
        '無理は禁物\n十分な休息を取り心身の調和を保つべし',
        '気になる箇所は早めに医師に診せろ',
        '異変を感じたら迷わず休め',
        '心穏やかに過ごせ\n快方に向かう',
        '体を休ませる時間をきちんととるべし',
        '医師はしっかり選べ',
    ]
    
    omikuji_tabi_map = [
        '新天地での出会いに恵まれ思わぬ幸運が訪れる',
        '無理のない計画で進めれば順調に運ぶ',
        '慎重に計画を立て着実に進めるべし',
        '慎重に計画を立て時期を見極めるべし',
        'いまは慎むべき 時機を改めることで新たな道が開かれる'
    ]
    
    omikuji_machibito_map = [
        'まもなく訪れる\n待ちわびた人との出会いは喜びに満ちたものとなる\n心を開いて迎えるべし',
        '程なく来る兆しあり\nその人を思う気持ちは必ずや通ずる\n穏やかな心で待つべし',
        '今しばらくの時を要す\n諦めることなく待てば必ず良き便りあり\nその時まで心静かに待つべし',
        'いまは巡り合わぬ時',
    ]
    
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        super().__init__()
        self.bot = bot
        self.logger = logger
        random.seed()
        # self.omikuji_results = {}
    
    def getRandomUnseiId(self):
        dice = random.randrange(len(self.omikuji_map))
        return self.omikuji_map[dice]
    
    def getUnseiText(self, unsei_id: str):
        return self.omikuji_unsei_map[unsei_id]
    
    def getRandomGanbo(self):
        dice = random.randrange(len(self.omikuji_ganbo_map))
        return self.omikuji_ganbo_map[dice]
    
    def getRandomGakugyo(self):
        dice = random.randrange(len(self.omikuji_gakugyo_map))
        return self.omikuji_gakugyo_map[dice]
    
    def getRandomRenai(self):
        dice = random.randrange(len(self.omikuji_renai_map))
        return self.omikuji_renai_map[dice]
    
    def getRandomKenko(self):
        dice = random.randrange(len(self.omikuji_kenko_map))
        return self.omikuji_kenko_map[dice]
    
    def getRandomTabi(self):
        dice = random.randrange(len(self.omikuji_tabi_map))
        return self.omikuji_tabi_map[dice]
    
    def getRandomMachibito(self):
        dice = random.randrange(len(self.omikuji_machibito_map))
        return self.omikuji_machibito_map[dice]
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('OmikujiCog is ready')
        
    @app_commands.command()
    async def omikuji(self, ctx):
        channel = self.bot.get_channel(ctx.channel_id)
        
        # if ctx.user.id in self.omikuji_results.keys():
        #     self.logger.info(f'[omikuji] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) -> already done')
        #     await ctx.response.send_message(f'【{ctx.user.display_name}】おみくじを引きました\n\n{self.omikuji_results[ctx.user.id]}', silent=True)
        #     return

        # 運勢を決める
        unsei = self.getRandomUnseiId()
        unsei_text = self.getUnseiText(unsei)
        ganbo = self.getRandomGanbo()
        gakugyo = self.getRandomGakugyo()
        renai = self.getRandomRenai()
        kenko = self.getRandomKenko()
        tabi = self.getRandomTabi()
        machibito = self.getRandomMachibito()

        omikuji_text = f'◆{unsei}◆\n{unsei_text}\n-------------------------------------\n●願望\n{ganbo}\n●学業\n{gakugyo}\n●恋愛\n{renai}\n●健康\n{kenko}\n●旅行\n{tabi}\n●待人\n{machibito}'
        # self.omikuji_results[ctx.user.id] = omikuji_text
        self.logger.info(f'[omikuji ({unsei})] called by {ctx.user.display_name}({ctx.user.id}) on {channel.name}({channel.id}) -> {omikuji_text}')
        await ctx.response.send_message(f'【{ctx.user.display_name}】おみくじを引きました\n\n{omikuji_text}', silent=True)
