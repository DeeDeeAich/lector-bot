from discord import Embed
from discord.ext import commands

import datetime


class Pages(commands.Cog):
    def __init__(self, bot):
        self.about_page = Embed(title='About Lector')
        self.about_page.description = 'A Discord bot for fetching and subscribing to various Christian lectionaries.'
        self.about_page.add_field(name='Developer', value='Fen#0087')
        self.about_page.add_field(name='Version', value='Alpha')
        self.about_page.add_field(name='Library', value='[discord.py](https://github.com/Rapptz/discord.py)')

        sources = [
            '[Holy Trinity Russian Orthodox Church](https://www.holytrinityorthodox.com/calendar/)',
            '[USCCB](https://bible.usccb.org/)',
            '[Vanderbilt Univerity, Divinity Library](https://lectionary.library.vanderbilt.edu/)',
            '[VEMKAR](https://vemkar.us/lectionary/)'
        ]

        self.about_page.add_field(name='Liturgical Sources', value='\n'.join(sources))

        self.copyright_page = Embed(title='Copyright Notices')
        self.copyright_page.add_field(name='Armenian Lectionary'      , value='Copyright © 2017-2018 Vemkar.\n')
        self.copyright_page.add_field(name='Catholic Lectionary'      , value='Lectionary for Mass for Use in the Dioceses of the United States, second typical edition, Copyright © 2001, 1998, 1997, 1986, 1970 Confraternity of Christian Doctrine; Psalm refrain © 1968, 1981, 1997, International Committee on English in the Liturgy, Inc. All rights reserved. Neither this work nor any part of it may be reproduced, distributed, performed or displayed in any medium, including electronic or digital, without permission in writing from the copyright owner.')
        self.copyright_page.add_field(name='Orthodox Lectionary'      , value=datetime.datetime.today().strftime('Copyright © %Y Holy Trinity Russian Orthodox Church.'))
        self.copyright_page.add_field(name='Revised Common Lectionary', value='Revised Common Lectionary, Copyright © 1992 Consultation on Common Texts. Used by permission.')

        self.help_page = Embed(title='Command Help')

        pre = '+'

        self.help_page.description = '**Informational**'
        self.help_page.description += f'\n{pre}about - Bot info'
        self.help_page.description += f'\n{pre}copyright - Lectionary copyright info'
        self.help_page.description += f'\n{pre}help - This help page'
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
    async def copyright(self, ctx):
        await ctx.send(embed=self.copyright_page)


    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=self.help_page)


def setup(bot):
    bot.add_cog(Pages(bot))