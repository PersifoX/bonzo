# created by ムAloneStranger (c) 2020. 
# вносить дальнейшие изменения в этот файл следует только автору файла.

# необходимое каждому модулю команд начало
from bonzoboot import bot
from random import randint

# функция, отправляющая рандомного котика :3
@bot.command()
async def randomcat(ctx):
    await ctx.send('https://cataas.com/cat?' + str(randint(0, 10**6)))
