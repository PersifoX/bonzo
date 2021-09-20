from discord.ext.commands import Cog, command
from discord import File
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from discord.ext.commands.errors import MissingRequiredArgument
from discord_slash import SlashContext, cog_ext
from config import guilds
from re import compile
from aiohttp import ClientSession
from discord.ext.commands.context import Context
from typing import Optional

name = 'demotivator'
description = 'Как в мемах. Нужна ссылка'


class Demotivator(Cog):
    urlValid = compile(r'https?://(?:www\.)?.+')

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send('Нужно указать текст/ссылку')

    @command(name=name, description=description)
    async def demotivator_prefix(self, ctx: Context, img_url: str, *text: str):
        img_url = img_url or (ctx.message.attachments[0].url if len(
            ctx.message.attachments) > 0 else '')
        await self.demotivator(ctx, img_url, ' '.join(text))

    @cog_ext.cog_slash(name=name, description=description)
    async def demotivator_slash(self, ctx: SlashContext, image_url: str,  text: str):
        await self.demotivator(ctx, image_url, text)

    async def demotivator(self, ctx, image_url, text):
        if not self.urlValid.match(image_url):
            await ctx.send('Ссылка не найдена')
            return

        if len(text) > 25:
            await ctx.send('Максимум 25 символов')
            return

        # O_O - первый await создает coroutine, второй его ждет и все работает
        await (await self.bot.loop.run_in_executor(None, self.asyncDemotivator, ctx, image_url, text))

    async def asyncDemotivator(self, ctx, image_url, underText):

        async with ClientSession() as session:
            async with session.get(image_url) as response:
                try:
                    photo = await response.read()
                except:
                    await ctx.send('Не удалось открыть файл')
                    return

        img = Image.open(BytesIO(photo))
        template = Image.open('./static/demotivatorTemplate.png')

        draw = ImageDraw.Draw(template)
        font = ImageFont.truetype('./static/arial.ttf', 54)
        textWidth = font.getsize(underText)[0]
        # Открываем фотку в RGB формате (фотки без фона ARGB ломают все)
        img = img.convert('RGB')
        img = img.resize((666, 655))

        template.paste(img, (50, 50))

        draw.text(((760 - textWidth) / 2, 720), underText, (255, 255, 255),
                  font=font, align='right')

        with BytesIO() as temp:
            template.save(temp, "png", quality=100)
            temp.seek(0)
            await ctx.send(file=File(fp=temp, filename='now.png'))


def setup(bot):
    bot.add_cog(Demotivator(bot))
