from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from discord.ext.commands import Cog, command
from database import db
from discord import Embed
from datetime import datetime, timedelta


class AddXP(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = db.cursor
        self.messageXP = 1
        self.voiceXP = 10
        self.guild = None

    @Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(664485208745050112)

        for channel in self.guild.voice_channels:
            if channel.name != 'AFK':
                for voiceUser in self.bot.get_channel(channel.id).members:
                    if not voiceUser.bot:
                        self.addVoiceJob(voiceUser)

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.addMessageXp(message.author)
        return

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and member.guild.id == self.guild.id:
            # Если чел зашел в войс и не в канале АФК, и не замучен
            if member.voice and member.voice.channel.name != 'AFK' and member.voice.self_deaf == False:
                try:
                    # Добавляем таск получения опыта
                    self.addVoiceJob(member)
                # Если уже есть задача, то пофиг (если чел перемещается по каналам, то появляется ошибка,
                # поэтому дропаем в блок исключения )
                except ConflictingIdError:
                    pass

            else:
                try:
                    # Удаляем задачу
                    self.bot.scheduler.remove_job(f'{member.id}')

                # Если задачи нет, то пофиг (чел может быть в афк, т.е у него не будет задачи,
                # если он выйдет из канала афк, то появится ошибка.
                # Если зайдет в другой канал, все должно быть норм)
                except JobLookupError:
                    pass

        return

    def addVoiceJob(self, memberId: int):
        self.bot.scheduler.add_job(
            self.addVoiceXp, 'interval', minutes=1, id=f'{memberId}', args=[memberId])

    async def addMessageXp(self, member):
        selectQuery = 'with res as (select id from user_server where userid=(%s) and serverid=(%s)) \
                    select xp, nexttextxpat  from xpinfo where xpinfo.id = (select res.id from res);'

        values = ((member.id, member.guild.id))

        self.cursor.execute(selectQuery, values)

        xpInfo = self.cursor.fetchone()

        if xpInfo is None:
            insertQuery = 'with res as (insert into user_server (userid, serverid) values (%s, %s) returning id)\
                        insert into xpinfo (id) select res.id from res;'

            self.cursor.execute(insertQuery, values)
            return

        xp, nextMessageXpAt = xpInfo

        if datetime.now() > nextMessageXpAt:
            newXp = xp + self.messageXP
            newLvl = self.calculateLevel(newXp)

            updateQuery = 'with res as (select id from user_server where userid=(%s) and serverid=(%s)) \
                        update xpinfo set xp=%s, LVL=%s, NextTextXpAt = %s where xpinfo.id = (select res.id from res);'
            values = ((member.id, member.guild.id, newXp, newLvl,
                       datetime.now()+timedelta(seconds=60)))

            self.cursor.execute(updateQuery, values)

    async def addVoiceXp(self, member):
        selectQuery = 'with res as (select id from user_server where userid=(%s) and serverid=(%s)) \
                    select xp from xpinfo where xpinfo.id = (select res.id from res);'

        values = ((member.id, member.guild.id))

        self.cursor.execute(selectQuery, values)

        xpInfo = self.cursor.fetchone()[0]

        if xpInfo is None:
            insertQuery = 'with res as (insert into user_server (userid, serverid) values (%s, %s) returning id)\
                        insert into xpinfo (id) select res.id from res;'

            self.cursor.execute(insertQuery, values)
            return

        newXp = xpInfo + self.voiceXP
        newLvl = self.calculateLevel(newXp)

        updateQuery = 'with res as (select id from user_server where userid=(%s) and serverid=(%s)) \
                        update xpinfo set xp=%s, LVL=%s  where xpinfo.id = (select res.id from res);'
        values = ((member.id, member.guild.id, newXp, newLvl))

        self.cursor.execute(updateQuery, values)

    def calculateLevel(self, exp):
        return int((exp/45) ** 0.6)

    def calculateXp(self, lvl):
        return int((45*lvl**(5/3)))+1

    @ command(name='leaderboard', description='Показывает топ 10 по опыту', aliases=['top'])
    async def leaderboard(self, ctx):
        selectQuery = 'select userId, xp, lvl from user_server join xpinfo ON user_server.id = xpinfo.id where user_server.serverid = %s and xp > 0 order by xp desc;'
        values = ((str(ctx.guild.id),))
        self.cursor.execute(selectQuery, values)

        result = self.cursor.fetchmany(10)

        if result is None:
            await ctx.message.reply('Значения не найдены')
            return

        embed = Embed(
            title='TOP 10 участников по опыту', color=ctx.author.color)

        embed.set_footer(
            text=f'/by bonzo/ for {ctx.message.author}', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)

        for id_, exp, lvl in result:
            member = self.bot.guild.get_member(id_)
            embed.add_field(
                name=f'`{member.display_name}`', value=f'LVL: {lvl}\nEXP: {exp}', inline=False)
        await ctx.message.reply(embed=embed)


def setup(bot):
    bot.add_cog(AddXP(bot))
