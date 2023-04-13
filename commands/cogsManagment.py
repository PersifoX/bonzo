from discord.ext.commands import Cog, is_owner, hybrid_command, Context
import traceback
from bot import Bot
from config import MAIN_GUILD
from discord.app_commands import guilds

class CogsManagement(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @hybrid_command(name="load", description="Загружает ког", hidden=True)
    @guilds(MAIN_GUILD)
    @is_owner()
    async def load_cog(self, ctx: Context, cog: str):
        try:
            await self.bot.load_extension("commands." + cog)
        except Exception as e:
            return await ctx.send(f"Невозможно загрузить ког: {traceback.format_exc()}")
        await ctx.send(f"Ког {cog} загружен")

    @hybrid_command(name="unload", description="Выгружает ког", hidden=True)
    @guilds(MAIN_GUILD)
    @is_owner()
    async def unload_cog(self, ctx: Context, cog: str):
        try:
            await self.bot.unload_extension("commands." + cog)
        except Exception as e:
            return await ctx.send(f"Невозможно выгрузить ког: {traceback.format_exc()}")

        await ctx.send(f"Ког {cog} выгружен")

    @hybrid_command(name="reload", description="Перезагружает ког", hidden=True)
    @guilds(MAIN_GUILD)
    @is_owner()
    async def reload_reload(self, ctx: Context, cog: str):
        try:
            await self.bot.unload_extension("commands." + cog)
            await self.bot.load_extension("commands." + cog)
        except Exception as e:
            return await ctx.send(f"Невозможно перезагрузить ког {traceback.format_exc()}")

        await ctx.send(f"Ког {cog} перезагружен")


    @hybrid_command(name="sync", description="Синхронизирует команды", hidden=True)
    @guilds(MAIN_GUILD)
    @is_owner()
    async def sync_cmds(self, ctx: Context):
        synced = await self.bot.tree.sync()
        print(synced)
        await ctx.send('Команды синхронизированы')

async def setup(bot):
    await bot.add_cog(CogsManagement(bot))
