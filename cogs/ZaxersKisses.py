import discord
from discord.ext import commands
import random


from shared_vars import intents,googleClient

client = discord.Client(intents=intents)

KissSheet = googleClient.open("Hellscube Database").worksheet("Zaxer's Wacky Database Sheet")


class ZaxersKissesCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
    @commands.command(aliases=['awardkisses'])
    async def awardkiss(self,ctx:commands.Context, user, number = 1):
        moderators_list = KissSheet.col_values(1)
        print(ctx.author.id)
        print(moderators_list)
        print(ctx.author.id in moderators_list)
        if str(ctx.author.id) in moderators_list:
            member = await commands.MemberConverter().convert(ctx, user)
            members_list = KissSheet.col_values(2)
            print(members_list)
            print(str(member.id))
            if str(member.id) in members_list:
                row = members_list.index(str(member.id)) + 1
            else:
                row = len(members_list) + 1
                KissSheet.update_cell(row, 2, str(member.id))
                KissSheet.update_cell(row, 3, 0)
                KissSheet.update_cell(row, 4, 0)
                KissSheet.update_cell(row, 5, 0)

            currentKisses = int(KissSheet.cell(row, 3).value) + number
            lifetimeKisses = int(KissSheet.cell(row, 4).value) + number
            KissSheet.update_cell(row, 3, currentKisses)
            KissSheet.update_cell(row, 4, lifetimeKisses)
            await ctx.send(str(user) + " earned " + str(number) + " kisses! Total: " + str(currentKisses) + ". \nUse !kiss @user to give a kiss, or !kisses to check your lifetime kiss stats.")
        else:
            await ctx.send("Only verified kiss arbiters can award kisses! Talk to Zaxer to inquire about becoming a verified kiss arbiter.")

    @commands.command()
    async def kiss(self,ctx:commands.Context, user):
        kissers_list = KissSheet.col_values(2)
        if str(ctx.author.id) in kissers_list:
            row = kissers_list.index(str(ctx.author.id)) + 1
            kissCount =  int(KissSheet.cell(row, 3).value)
            if kissCount > 0:
                try:
                    KissedMember = await commands.MemberConverter().convert(ctx, user)
                except:
                    await ctx.send("Something went wrong. Be sure to ping the user you want me to kiss! Maybe that's what went wrong?")
                if (KissedMember == ctx.author):
                    await ctx.send("You can't send a kiss to yourself! How would that even work??")
                    return
                if str(KissedMember.id) in kissers_list:
                    kissedrow = kissers_list.index(str(KissedMember.id)) + 1
                else:
                    kissedrow = len(kissers_list) + 1
                    KissSheet.update_cell(kissedrow, 2, str(KissedMember.id))
                    KissSheet.update_cell(kissedrow, 3, 0)
                    KissSheet.update_cell(kissedrow, 4, 0)
                    KissSheet.update_cell(kissedrow, 5, 0)
                KissSheet.update_cell(kissedrow, 5, int(KissSheet.cell(kissedrow, 5).value) + 1)
                MessageList = ["mmmmwah!", "mwah!", "smooch!", "*kisses u*", "mwa!", "dis a kis from me to u :)", "^3^ mweh!", ":*", ";*", "just a quick peck, to be safe- mwa!", "໒(∗ ⇀ 3 ↼ ∗)७", "mwah!"]
                ThisKiss = random.choice(MessageList)
                await ctx.send(user + " " + ThisKiss)
                KissSheet.update_cell(row, 3, kissCount - 1)

            else:
                await ctx.send("You don't have any kisses to send!")
        else:
            await ctx.send("You don't have any kisses to send!")

    @commands.command()
    async def kisses(self, ctx:commands.Context):
        kissers_list = KissSheet.col_values(2)
        if str(ctx.author.id) in kissers_list:
            row = kissers_list.index(str(ctx.author.id)) + 1
            current = KissSheet.cell(row, 3).value
            lifetime = KissSheet.cell(row, 4).value
            kissed = KissSheet.cell(row, 5).value
            await ctx.send(f'You have {current} kisses to give!\nYou have earned {lifetime} kisses in total!\nYou have been kissed {kissed} times!')
        else:
            await ctx.send("You have 0 kisses to give!\nYou have earned 0 kisses in total!\nYou have been kissed 0 times!") 


async def setup(bot:commands.Bot):
    await bot.add_cog(ZaxersKissesCog(bot))