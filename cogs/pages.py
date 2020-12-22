from discord import Embed
from discord.ext import commands


class Pages(commands.Cog):
    def __init__(self, bot):
        self.about_page = Embed(title='About Lector')
        self.about_page.description = 'A Discord bot for fetching and subscribing to various Christian lectionaries.'
        self.about_page.add_field(name='Developer', value='Fen#0087')
        self.about_page.add_field(name='Version', value='Alpha')
        self.about_page.add_field(name='Library', value='[discord.py](https://github.com/Rapptz/discord.py)\nType "+mit"')

        sources = [
            '[Holy Trinity Russian Orthodox Church](https://www.holytrinityorthodox.com/calendar/)',
            '[United States Conference of Catholic Bishops](https://bible.usccb.org/)',
            '[Vanderbilt University, Divinity Library](https://lectionary.library.vanderbilt.edu/)',
            '[VEMKAR](https://vemkar.us/lectionary/)'
        ]

        self.about_page.add_field(name='Liturgical Sources', value='\n'.join(sources))

        self.help_page = Embed(title='Command Help')

        pre = '+'
        self.help_page.description = '**Informational**'
        self.help_page.description += f'\n{pre}about - Bot information'
        self.help_page.description += f'\n{pre}help - Shows this help page'
        self.help_page.description += '\n\n**Lectionaries**'
        self.help_page.description += f'\n{pre}[armenian|a|arm|armen]'
        self.help_page.description += f'\n{pre}[catholic|c|cath]'
        self.help_page.description += f'\n{pre}[orthodox|o|orth|ortho]'
        self.help_page.description += f'\n{pre}[rcl|r|revised|prot|protestant]'
        self.help_page.description += '\n\n**Subscriptions (Requires Manage Messages)**'
        self.help_page.description += f'\n{pre}[subscribe|sub] (a|c|o|r) (#channel)'
        self.help_page.description += f'\n{pre}[unsubscribe|unsub] (#channel|all)'
        self.help_page.description += f'\n{pre}[subscriptions|subs]'


    @commands.command()
    async def about(self, ctx):
        await ctx.send(embed=self.about_page)


    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=self.help_page)


def setup(bot):
    bot.add_cog(Pages(bot))