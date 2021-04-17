from discord import TextChannel
from discord.ext.commands import Cog, command, is_owner
from discord.ext.commands.errors import CommandInvokeError, NotOwner
name = 'evala'
description = 'Исполняет код (только для разработчиков)'


class evala(Cog):
    def __init__(self, bot):
        self.bot = bot
    # Обработка ошибок

    async def cog_command_error(self, ctx, error):
        if isinstance(error, CommandInvokeError):
            await ctx.send('Ошибка при выполении запроса')

        if isinstance(error, NotOwner):
            await ctx.send('Только для разработчиков бота')

    # eval - запуск кода от лица бота овнером через discord.
    # не следует использовать рядовым пользователям. дословно закомментировано не будет (!)
    @is_owner()
    @command(name=name, description=description)
    async def evala(self, ctx, evcode: str):
        if not evcode:
            raise CommandInvokeError()

        execute = eval(evcode)

        await ctx.message.delete()

        await execute


def setup(bot):
    bot.add_cog(evala(bot))
