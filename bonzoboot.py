# Created by ムAloneStranger (c) 2020.
# файл-загрузчик бота.
# осуществлять запуск только из этого файла.

import discord
from discord.ext import commands

import platform
from time import time

# для безопасного импорта токена
import os 
from dotenv import load_dotenv 
load_dotenv() # загружает файл env

game = discord.Game("v0.5.1 osmplesher") # пишем боту в активити
bot = commands.Bot(command_prefix='b/', help_command=None) # лёгкая референс-комманда для нашего бота, задаём префикс и встроенную команду help 

# функция запуска (можно узнать разницу между прочитыванием кода компьютером и связью с discord api)
def bonzo():
    global ctimest # переменная, содержащая разницу между временем прочтения кода и готовым к работе ботом
    ctimest = time() # таймштамп: код успешно прочитан
    print('/', 'initialization file has been successfully read. starting up bonzo...', sep='\n')
    bot.run(os.getenv('TOKEN')) # берёт переменную TOKEN из .env

# eval - запуск кода от лица бота овнером через discord.
# не следует использовать рядовым пользователям. дословно закомментировано не будет (!)
@bot.command() 
async def evala(ctx, evcode=None):
    ownerids = [221246477630963722, 196314341572608000, 393807398047055883] # определяем овнеров
    if evcode == None: # проверяем, указан ли код
        await discord.TextChannel.purge(ctx.message.channel, limit=1)
        await ctx.send("укажите код для экзекьюции.")
    else:
        if ctx.author.id in ownerids: # проверяем, овнер ли запросил команду?
            execute = eval(str(evcode))
            await discord.TextChannel.purge(ctx.message.channel, limit=1) # удаляем команду
            await execute
        else: 
            await ctx.send("ты бесправное чмо " + '{0.author.mention}'.format(ctx))

# импорт файла-фикса для импорта наших функций
from botlib.blankfix import * 

# импорт наших собственных функций в файл инстанции.
from botlib.func_alone import *
from botlib.func_vlaner import *
from botlib.func_nohame import *
from botlib.music import *

# on_ready выполняется при полной готовности бота к действиям
@bot.event 
async def on_ready():
    global ctimest # переменная, содержащая разницу между временем прочтения кода и готовым к работе ботом
    await bot.change_presence(status=discord.Status.online, activity=game) # бот меняет свой статус именно благодаря этой команде (и "играет" в "игру" которую мы задали в строке 13)
    ctimest = time() - ctimest # дельта времени: бот готов к работе
    print('/', 'bonzo has been successfully initialized on ' + platform.platform(), 'timestamp delta is: ' + str(round(ctimest,3)) + 's', 'discord latency is: ' + str(round(bot.latency, 3)) + 's', '/', sep='\n')

# запускаем инстанцию бота
bonzo()