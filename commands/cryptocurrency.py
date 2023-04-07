from discord.embeds import Embed
from commands.resources.AutomatedMessages import automata
from discord.ext.commands import Cog, CommandError, Context, hybrid_command
from dependencies.api.crypto.abc import CryptoAPI
from bot import Bot

name = "crypto"
description = "Выводит информацию о криптовалюте (INDEV)"


class RequestNetworkError(CommandError):
    pass


class CurrencyDoesNotExist(CommandError):
    pass


class Crypto(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.crypto_api: CryptoAPI = self.bot.dependency.crypto_api

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, RequestNetworkError):
            return await ctx.send(embed=automata.generateEmbErr("Ошибка при запросе"))
        if isinstance(error, CurrencyDoesNotExist):
            return await ctx.send(
                embed=automata.generateEmbErr("Такой валюты не найдено")
            )
        raise error
        
    @hybrid_command(name=name, description=description)
    async def get_crypto_listings(self, ctx: Context):
        res = await self.crypto_api.get_biggest_currencies()

        embed = Embed(title="10 крупнейших криптовалют по капитализации")

        for crypto in res:
            finprice = float(crypto.price_usd)
            if finprice > 99.9:
                finprice = str(int(round(finprice, 1)))
            elif finprice > 0.0099:
                finprice = str(round(finprice, 2))
            else:
                finprice = str(round(finprice, 6))

            embed.add_field(
                name=f"{crypto.name} | {crypto.symbol}",
                value=f"Цена: ${finprice}",
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Crypto(bot))
