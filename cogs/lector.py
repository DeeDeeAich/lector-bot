from lectionary import armenian
from lectionary import catholic
from lectionary import orthodox
from lectionary import rcl

import discord
from discord.ext import commands, tasks

import sqlite3
import typing
import datetime


class Lectionary(commands.Cog):
    def __init__(self, bot):
        self.bot         = bot
        self.error_embed = discord.Embed(title='The lectionary could not be fetched', color=discord.Colour.red())

        # This list is for indexing-display purposes
        # In the database, 0 through 3 coorspond to these
        self.l = ['Armenian', 'Catholic', 'Orthodox', 'Revised Common']

        # Lectionary Objects
        self.armenian_lectionary = armenian.ArmenianLectionary()
        self.catholic_lectionary = catholic.CatholicLectionary()
        self.orthodox_lectionary = orthodox.OrthodoxLectionary()
        self.rcl_lectionary      = rcl.RevisedCommonLectionary()

        # Build initial embeds
        self.build_all_embeds()

        # Set up the subscription database if it isn't already
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS subscriptions (server_id INT, channel_id INT, sub_type INT)')
        conn.commit()
        conn.close()

        # Start up the event loops
        self.update_embeds.start()
        self.fufill_subscriptions.start()

    
    def build_all_embeds(self):
        self.armenian_embeds  = self.armenian_lectionary.build_embeds()
        self.catholic_embeds  = self.catholic_lectionary.build_embeds()
        self.orthodox_embeds  = self.orthodox_lectionary.build_embeds()
        self.rcl_embeds       = self.rcl_lectionary.build_embeds()


    '''BASIC LECTIONARY REQUEST COMMANDS'''

    @commands.command(aliases=['a', 'arm', 'armen'])
    async def armenian(self, ctx):
        if self.armenian_embeds == []:
            self.armenian_embeds  = self.armenian_lectionary.build_embeds()
            if self.armenian_embeds == []:
                await ctx.send(embed=self.error_embed)
                return

        for embed in self.armenian_embeds:
            await ctx.send(embed=embed)


    @commands.command(aliases=['c', 'cath'])
    async def catholic(self, ctx):
        if self.catholic_embeds == []:
            self.catholic_embeds  = self.catholic_lectionary.build_embeds()
            if self.catholic_embeds == []:
                await ctx.send(embed=self.error_embed)
                return

        for embed in self.catholic_embeds:
            await ctx.send(embed=embed)


    @commands.command(aliases=['o', 'orth', 'ortho'])
    async def orthodox(self, ctx):
        if self.orthodox_embeds == []:
            self.orthodox_embeds  = self.orthodox_lectionary.build_embeds()
            if self.orthodox_embeds == []:
                await ctx.send(embed=self.error_embed)
                return

        for embed in self.orthodox_embeds:
            await ctx.send(embed=embed)
    

    @commands.command(aliases=['r', 'revised', 'prot', 'protestant'])
    async def rcl(self, ctx, arg:str=None):
        if self.rcl_embeds == []:
            self.rcl_embeds = self.rcl_lectionary.build_embeds()
            if self.rcl_embeds == []:
                await ctx.send(embed=self.error_embed)
                return

        for embed in self.rcl_embeds:
            await ctx.send(embed=embed)
    

    '''SUBSCRIPTION COMMANDS'''

    @commands.command(aliases=['sub'])
    @commands.has_permissions(manage_messages=True)
    async def subscribe(self, ctx, arg: str, channel: typing.Optional[discord.TextChannel] = None):
        if   arg in ['armenian','a','arm','armen']            : sub_type = 0
        elif arg in ['catholic','c','cath']                   : sub_type = 1
        elif arg in ['orthodox','o','orth','ortho']           : sub_type = 2
        elif arg in ['rcl','r','revised','prot','protestant'] : sub_type = 3
        else:
            await ctx.send('You didn\'t specify a valid lectionary option.')
            return
        
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()

        if channel:
            channel_id = channel.id
        else:
            channel_id = ctx.channel.id

        server_id = ctx.guild.id

        # Check to see if a subscription for the channel already exists
        c.execute('SELECT * FROM subscriptions WHERE channel_id = ?', (channel_id,))
        row = c.fetchone()
        sub_name = self.l[sub_type]

        if row:
            # If a subscription already exists for the current channel
            if row[2] == sub_type:
                # If the channel is already subscribed to what was requested
                await ctx.send(f'<#{channel_id}> is already subscribed to the {sub_name} Lectionary.')
            else:
                # If the subscription for a channel is changing from one lectionary to another
                c.execute('UPDATE subscriptions SET sub_type = ? WHERE channel_id = ?', (sub_type, channel_id))
                conn.commit()
                await ctx.send(f'The subscription for <#{channel_id}> has been updated to the {sub_name} Lectionary.')
        else:
            # If a subscription does not exist for the channel
            c.execute('INSERT INTO subscriptions VALUES (?, ?, ?)', (server_id, channel_id, sub_type))
            conn.commit()
            await ctx.send(f'<#{channel_id}> has been subscribed to the {sub_name} Lectionary.')

        conn.close()


    @commands.command(aliases=['unsub'])
    @commands.has_permissions(manage_messages=True)
    async def unsubscribe(self, ctx, channel: typing.Optional[typing.Union[discord.TextChannel, str]] = None):
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()

        if channel is None: channel = ctx.channel

        if isinstance(channel, discord.TextChannel):
            if channel:
                channel_id = channel.id
            else:
                channel_id = ctx.channel.id
            
            c.execute('SELECT * FROM subscriptions WHERE channel_id = ?', (channel_id,))

            row = c.fetchone()

            if row:
                c.execute('DELETE FROM subscriptions WHERE channel_id = ?', (channel_id,))
                conn.commit()
                await ctx.send(f'<#{channel_id}> has been unsubscribed.')
            else:
                await ctx.send(f'<#{channel_id}> is not subscribed to any lectionaries.')
        elif isinstance(channel, str) and channel == 'all':
            c.execute('DELETE FROM subscriptions WHERE server_id = ?', (ctx.guild.id,))
            conn.commit()
            await ctx.send(f'All subscriptions for {ctx.guild.name} have been removed.')

        conn.close()
    

    @commands.command(aliases=['subs'])
    @commands.has_permissions(manage_messages=True)
    async def subscriptions(self, ctx):
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('SELECT * FROM subscriptions WHERE server_id = ?', (ctx.guild.id,))
        subscriptions = c.fetchall()
        conn.close()

        embed = discord.Embed(title=f'Subscriptions for {ctx.guild.name}')
        if subscriptions:
            embed.description = '\n'.join([f'<#{sub[1]}> - {self.l[sub[2]]} Lectionary' for sub in subscriptions])
        else:
            embed.description = 'There are none'
        
        await ctx.send(embed=embed)


    '''TASK LOOPS'''

    @tasks.loop(hours=1)
    async def update_embeds(self):
        # Update the embeds between 2AM and 3AM
        if 2 <= datetime.datetime.now().hour < 3:
            self.build_all_embeds()

    
    @tasks.loop(hours=1)
    async def fufill_subscriptions(self):
        # Push the subscriptions between 3AM and 4AM
        if 3 <= datetime.datetime.now().hour < 4:
            conn = sqlite3.connect('data.db')
            c    = conn.cursor()
            c.execute('SELECT * FROM subscriptions')
            subscriptions = c.fetchall()

            feeds = [self.armenian_embeds, self.catholic_embeds, self.orthodox_embeds, self.rcl_embeds]
            for subscription in subscriptions:
                channel_id, sub_type = subscription[1], subscription[2]
                channel = self.bot.get_channel(channel_id)

                # If channel exists and is accessible to the bot
                if channel:
                    if feeds[sub_type] != []:
                        for embed in feeds[sub_type]:
                            await channel.send(embed=embed)
                    else:
                        await channel.send(embed=self.error_embed)
                else:
                    c.execute('DELETE FROM subscriptions WHERE channel_id = ?', (channel_id,))
                        
            conn.commit()
            conn.close()
    

    @fufill_subscriptions.before_loop
    async def before_fufill_subscriptions(self):
        await self.bot.wait_until_ready()


    '''SYSTEM COMMANDS'''

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        self.update_embeds.stop()
        self.fufill_subscriptions.stop()
        await ctx.message.add_reaction('✅')
        await ctx.bot.close()


    '''ERROR HANDLERS'''

    @subscribe.error
    async def subscribe_error(error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send('You need the manage messages perm to subscribe')
    

    @unsubscribe.error
    async def unsubscribe_error(error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send('You need the manage messages perm to unsubscribe')


    @subscriptions.error
    async def subscriptions_error(error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send('You need the manage messages perm to view server subscriptions')
    

def setup(bot):
    bot.add_cog(Lectionary(bot))