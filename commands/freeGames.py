from discord.ext.commands import (
    GroupCog,
    guild_only,
    has_permissions,
    bot_has_permissions,
    BucketType,
    cooldown,
)
from apscheduler.triggers.cron import CronTrigger
from asyncio import sleep
from discord.ext.commands import  hybrid_command, Context
from discord.ext.commands.core import is_owner

from discord.enums import ChannelType
from discord import Embed, Colour, app_commands, Interaction
from discord.app_commands import guilds
from .resources.AutomatedMessages import automata

from dependencies.repository.free_games.abc import FreeGamesRepository
from dependencies.repository.free_games.memory import FreeGamesRepositoryMemory
from database.memory.db import DictMemoryDB

from dependencies.api import epic_games

from bot import Bot
from config import MAIN_GUILD

import logging
import traceback

class FreeGames(GroupCog, group_name='freegames'):
    def __init__(self, bot, free_games_repo: FreeGamesRepository):
        self.bot: Bot = bot
        self.free_games_repo = free_games_repo

        self.bot.scheduler.add_job(
            self.send_free_games,
            CronTrigger(day_of_week="thu", hour=19, minute=3, jitter=120),
        )

    @app_commands.command(
        name="init",
        description="Инициализирует данный канал для рассылки бесплатных игр",
    )
    @guild_only()
    @cooldown(rate=2, per=15, type=BucketType.guild)
    @has_permissions(administrator=True)
    @bot_has_permissions(send_messages=True)
    async def init_free_games(self, inter: Interaction):
        channel = await self.free_games_repo.get_channel_by_guild(inter.guild.id)
        if channel:
            guild_channel = self.bot.get_channel(channel)
            return await inter.response.send_message(
                f"На этом сервере уже указан канал для бесплатных игр: {guild_channel.mention} (удаление через 3с)", delete_after=3
            )

        await self.free_games_repo.insert_channel(inter.guild.id, inter.channel.id)
        await inter.response.send_message(
            "Этот канал будет использоваться для рассылки бесплатных игр (удаление через 3с)", delete_after=3
        )

    @app_commands.command(name="stop", description="Останавливает рассылку бесплатных игр")
    @cooldown(rate=2, per=15, type=BucketType.guild)
    @has_permissions(administrator=True)
    @bot_has_permissions(send_messages=True)
    @guild_only()
    async def removeFromFreeGames(self, inter: Interaction):
        await self.free_games_repo.delete_channel(inter.guild.id)
        await inter.response.send_message("Рассылка бесплатных игр остановлена (удаление через 3с)", delete_after=3)

    async def build_free_game_embed(self, game):
        embedd = Embed(
            title="**Бесплатная игра недели (Epic Games)**", colour=Colour.random()
        )
        embedd.set_image(
            url=game['game_photo_url']
        )
        embedd.add_field(name=f"**{game['name']}**", value=f"**{game['link_to_game']}**", inline=False)
        embedd.add_field(name="**Цена до раздачи: **", value=f"{game['price_before']}")
        embedd.add_field(name="**Действует до: **", value=f"{game['due_date']}")

        return embedd

    @hybrid_command(
        name="owner_run",
        description="Ручной запуск бесплатных игр (только для создателей)"
    )
    @guilds(MAIN_GUILD)
    @is_owner()
    async def runFreeGanes(self, ctx):
        await self.send_free_games()

    async def send_free_games(self):
        channels = await self.free_games_repo.get_channels()
        if len(channels) < 1:
            return

        free_games = await epic_games.get_free_games()
        for free_game in free_games:
            free_game_embed = await self.build_free_game_embed(free_game)

            for channel in channels:
                channel = self.bot.get_channel(channel)
                if not channel:
                    continue
                
                try:
                    announcement = await channel.send(embed=free_game_embed)
                except Exception as e:
                    logging.warning(f'Could not send free game notification: {"".join(traceback.format_exception(type(e), value=e, tb=e.__traceback__))}')
                if channel.type == ChannelType.news:
                    await announcement.publish()

                await sleep(1)


async def setup(bot):
    free_games_repo = FreeGamesRepositoryMemory(DictMemoryDB)
    await bot.add_cog(FreeGames(bot, free_games_repo))
