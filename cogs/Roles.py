import discord
from discord.ext import commands
from discord.utils import get
import pprint as pp


class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def announcements(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(862806291844300830))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed Announcements from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " Announcements")

    @commands.command()
    async def vent(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(1003397744267898920))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed Vent from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " Vent")

    @commands.command()
    async def becomeArtist(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(819320922666041355))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed HCArtist from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " HCArtist")

    @commands.command()
    async def wantToDraft(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(661721357066698762))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed WantToDraft from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " WantToDraft")

    @commands.command()
    async def wantToEdh(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(720043670870425691))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed WantToEdh from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " WantToEdh")

    @commands.command()
    async def wantToJumpstart(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(733995427237724180))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed WantToJumpstart from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " WantToJumpstart")

    @commands.command()
    async def wantToConstructed(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(856927890120769576))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed WantToConstructed from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " WantToConstructed")

    @commands.command()
    async def wantToLeaks(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(794254398775361578))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed WantToLeaks from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " WantToLeaks")

    @commands.command()
    async def popcornCube(self, ctx):
        role = get(ctx.message.author.guild.roles, id=int(758033490133385308))
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Removed PopcornCube from " + str(ctx.message.author))
            return
        await ctx.author.add_roles(role)
        await ctx.send("Gave " + str(ctx.message.author) + " PopcornCube")

    @commands.command()
    async def pronoun(self, ctx, roleName):
        roleId = {
            "he": 745661999513469069,
            "she": 745662055842840718,
            "it": 745662178702655578,
            "they": 745662219001528340,
            "zir": 745662416280485929,
            "xir": 745662465639186465,
            "fae": 745662506915332247,
            "ey": 786272241234214923,
            "xe": 862497482709401620,
            "any": 867939179768729651,
            "all": 1006744588385534002,
            "gar": 1006737438967857242,
            "thou": 1006747294399471647,
            "ciri": 1006748383752507522,
            "who": 1006749672179765278,
            "sie": 1007104561674211419
        }
        if roleName == "help":
            message = "To give yourself a pronoun role type !pronoun and the subjective version of that pronoun. (You can have as many as you want.) The current list of pronouns is:\n"
            for i in roleId.keys():
                message += i + "\n"
            message += "If your pronouns are missing please tag Exalted"
            await ctx.send(message)
            return
        if roleName in roleId.keys():
            print(roleName)
            role = get(ctx.message.author.guild.roles, id=int(roleId[roleName]))
            pp.pprint(ctx.author.roles)
            if role in ctx.author.roles:
                print("got one")
                await ctx.author.remove_roles(role)
                await ctx.send("Removed the role " + role.name + " from " + str(ctx.message.author))
                return
            print("got two")
            await ctx.author.add_roles(role)
            await ctx.send("Gave " + str(ctx.message.author) + " the role " + role.name)
            return
        await ctx.send(
            "This is not currently a pronoun role, make sure to type !pronoun and then only the subjective pronoun (Example !pronoun they), If your pronouns are missing please tag Exalted")


async def setup(bot):
    await bot.add_cog(RolesCog(bot))
