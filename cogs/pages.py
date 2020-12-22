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
        self.help_page.description += f'\n{pre}mit - Shows the license of discord.py'
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
    

    @commands.command()
    async def mit(self, ctx):
        text  = 'discord.py license'
        text += '```'
        text += 'The MIT License (MIT)\n\n'
        text += 'Copyright (c) 2015-2020 Rapptz\n\n'
        text += 'Permission is hereby granted, free of charge, to any person obtaining a '
        text += 'copy of this software and associated documentation files (the "Software"), '
        text += 'to deal in the Software without restriction, including without limitation '
        text += 'the rights to use, copy, modify, merge, publish, distribute, sublicense, '
        text += 'and/or sell copies of the Software, and to permit persons to whom the '
        text += 'Software is furnished to do so, subject to the following conditions:\n\n'
        text += 'The above copyright notice and this permission notice shall be included in '
        text += 'all copies or substantial portions of the Software.\n\n'
        text += 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS '
        text += 'OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, '
        text += 'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE '
        text += 'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER '
        text += 'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING '
        text += 'FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER '
        text += 'DEALINGS IN THE SOFTWARE.'
        text += '```'

        await ctx.send(text)


def setup(bot):
    bot.add_cog(Pages(bot))
