from discord.ext.commands import Cog
from database import db


class memberJoinRemove(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = db.cursor

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute(
            "INSERT into exp (UserID, serverId) VALUES (%s,%s);", (member.id, member.guild.id))

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute('DELETE FROM exp WHERE UserID = %s and serverId=%s',
                   (member.id, member.guild.id))


def setup(bot):
    bot.add_cog(memberJoinRemove(bot))
