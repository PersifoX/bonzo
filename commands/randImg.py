from discord.ext.commands import Cog, CommandOnCooldown, command, cooldown, BucketType
from discord_slash import SlashContext, cog_ext
from bonzoboot import guilds
from random import sample
from aiohttp import ClientSession

name = 'randImg'
description = 'Отправляет случайное изображение из imgur'


class randImg(Cog):
    def __init__(self, bot):
        self.bot = bot

    # Обработка ошибок
    async def cog_command_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.message.reply(error)

    @cog_ext.cog_slash(name=name, description=description, guild_ids=guilds)
    async def randimg(self, ctx: SlashContext):
        photo = await self.process(ctx=ctx)

        while(photo == None):
            photo = await self.process(ctx=ctx)

        await ctx.send(photo)

    async def process(self, ctx: SlashContext):
        url = 'https://i.imgur.com/'
        symbols = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

        # Генерируем 5 рандомных  символов
        randSymbols = ''.join(sample(symbols, 5))

        # Делаем ссылку на картинку
        iImgurUrl = url + randSymbols + '.png'

        # Получаем инфу об картинке
        async with ClientSession() as session:
            async with session.head(iImgurUrl) as response:
                res = response

        # Если картинки нет, то она имеет размер 161х81 (размер 0 на сервере)
        if res.headers['content-length'] == '0':
            return None
        else:
            # Картинка нашлась, отправляем ссылку на картинку
            return iImgurUrl


def setup(bot):
    bot.add_cog(randImg(bot))
