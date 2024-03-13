from pprint import pp
import random
import discord
from discord.ext import commands
from shared_vars import drive
from dpymenus import PaginatedMenu
import hc_constants


global blueRed
blueRed = False
log = ""


class GeneralCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name="dumplog")
    async def _dumplog(self, ctx:commands.Context):
        global log
        if ctx.author.id == hc_constants.LLLLLL:
            with open("log.txt", 'a', encoding='utf8') as file:
                file.write(log)
                log = ""
                print("log dumped")

    @commands.command()
    async def BlueRed(self, ctx:commands.Context):
        if ctx.author.id == hc_constants.CIRION:
            global BlueRed
            if BlueRed:
                    BlueRed = False
                    await ctx.send("Turned Off")
            else:
                    BlueRed = True
                    await ctx.send("Turned On")
        else:
            await ctx.send("cirion Only Command")

    @commands.command()
    async def help(self, ctx:commands.Context):
        await ctx.send("https://discord.com/channels/631288872814247966/803384271766683668/803389199503982632")

    @commands.command()
    async def menu(self, ctx:commands.Context):
        if ctx.channel.id == hc_constants.RESOURCES_CHANNEL or hc_constants.BOT_TEST_CHANNEL:
            embed = discord.Embed(title="Resources Menu", description="[Channel Explanation](https://discord.com/channels/631288872814247966/803384271766683668/803384426360078336)\n[Command List](https://discord.com/channels/631288872814247966/803384271766683668/803389199503982632)\n[Achievements](https://discord.com/channels/631288872814247966/803384271766683668/803389622247882782)\n[Database](https://discord.com/channels/631288872814247966/803384271766683668/803390530145878057)\n[Release Notes](https://discord.com/channels/631288872814247966/803384271766683668/803390718801346610)\n[Cubecobras](https://discord.com/channels/631288872814247966/803384271766683668/803391239294025748)\n[Tabletop Simulator](https://discord.com/channels/631288872814247966/803384271766683668/803391314095636490)")
            await ctx.send(embed)

    @commands.command()
    async def getMessage(self, ctx:commands.Context, id):
        subChannel = self.bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
        message = await subChannel.fetch_message(id)
        await ctx.send(message.jump_url)

    
    @commands.command()
    async def macro(ctx:commands.Context, thing:str, *args):
        if thing == "help":
            message = "Macros are:\nJoke [word]\n"
            for name in hc_constants.macroList.keys():
                if type(hc_constants.macroList[name]) is str:
                    message += f"{name}\n"
                else:
                    message += f"{name}\n"
                    for subname in hc_constants.macroList[name]:
                        message += f"                {subname}\n"
            await ctx.send(message)
            return
        if thing.lower() in hc_constants.macroList.keys():
            if type(hc_constants.macroList[thing.lower()]) is str:
                await ctx.send(hc_constants.macroList[thing.lower()].replace("@arg", " ".join(args)))
            else:
                pp.pprint(hc_constants.macroList[thing.lower()])
                await ctx.send(hc_constants.macroList[thing.lower()][args[0].lower()])

async def setup(bot:commands.Bot):
    await bot.add_cog(GeneralCog(bot))

