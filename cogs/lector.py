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
        self.last_fufill = datetime.date.today()

        # This list is for indexing-display purposes
        # In the database, 0 through 3 coorspond to these
        self.lectionary_names = [
            'armenian',
            'catholic',
            'orthodox',
            'revised common']

        # Lectionary Objects
        self.armenian = armenian.ArmenianLectionary()
        self.catholic = catholic.CatholicLectionary()
        self.orthodox = orthodox.OrthodoxLectionary()
        self.rcl      = rcl.RevisedCommonLectionary()

        self.build_all_embeds()

        # Set up the subscription database if it isn't already
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS subscriptions (server_id INT, channel_id INT, sub_type INT)')
        conn.commit()
        conn.close()

        # Start up the event loop
        self.last_fufill = datetime.date.today()
        self.fufill_subscriptions.start()

    
    def regenerate_all_data(self):
        self.armenian.regenerate_data()
        self.catholic.regenerate_data()
        self.orthodox.regenerate_data()
        self.rcl.regenerate_data()


    def build_all_embeds(self):
        self.feeds = [
            self.armenian.build_embeds(),
            self.catholic.build_embeds(),
            self.orthodox.build_embeds(),
            self.rcl.build_embeds()
        ]


    '''BASIC LECTIONARY REQUEST COMMANDS'''

    @commands.command(aliases=['a', 'arm', 'armen'])
    async def armenian(self, ctx):
        for embed in self.feeds[0]:
            await ctx.send(embed=embed)


    @commands.command(aliases=['c', 'cath'])
    async def catholic(self, ctx):
        for embed in self.feeds[1]:
            await ctx.send(embed=embed)


    @commands.command(aliases=['o', 'orth', 'ortho'])
    async def orthodox(self, ctx):
        for embed in self.feeds[2]:
            await ctx.send(embed=embed)


    @commands.command(aliases=['r', 'revised', 'prot', 'protestant'])
    async def rcl(self, ctx):
        for embed in self.feeds[3]:
            await ctx.send(embed=embed)
    

    '''SUBSCRIPTION COMMANDS'''

    @commands.command(aliases=['sub'])
    @commands.has_permissions(manage_messages=True)
    async def subscribe(self, ctx, lectionary, channel:typing.Optional[discord.TextChannel] = None):
        if   lectionary in ['armenian','a','arm','armen']            : sub_type = 0
        elif lectionary in ['catholic','c','cath']                   : sub_type = 1
        elif lectionary in ['orthodox','o','orth','ortho']           : sub_type = 2
        elif lectionary in ['rcl','r','revised','prot','protestant'] : sub_type = 3
        else:
            await ctx.send('You didn\'t specify a valid lectionary option.')
            return
        
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()

        if channel: channel_id = channel.id
        else:       channel_id = ctx.channel.id

        server_id = ctx.guild.id

        # Check to see if a subscription for the channel already exists
        c.execute('SELECT * FROM subscriptions WHERE channel_id = ?', (channel_id,))
        row = c.fetchone()
        sub_name = self.lectionary_names[sub_type].title()

        # If a subscription already exists for the current channel
        if row:
            # If channel subscription request would not actually change any settings
            if (row[2] == sub_type) and (row[3] == view_mode):
                await ctx.send(f'<#{channel_id}> is already subscribed to the {sub_name} Lectionary.')
            else:
                # If the subscription for a channel is changing somehow
                c.execute('''
                    UPDATE subscriptions
                    SET sub_type = ?
                    WHERE channel_id = ?''',
                    (sub_type, channel_id))
                conn.commit()
                await ctx.send(f'The subscription for <#{channel_id}> has been updated to the {sub_name} Lectionary.')

        # If a subscription does not exist for the channel
        else:
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
        
        elif isinstance(channel, str) and (channel == 'all'):
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
            embed.description = '\n'.join([
                f'<#{sub[1]}> - {self.lectionary_names[sub[2]].title()} Lectionary'
                for sub in subscriptions])
        else:
            embed.description = 'There are none'
        
        await ctx.send(embed=embed)


    '''SYSTEM COMMAND'''

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        self.fufill_subscriptions.stop()
        await ctx.message.add_reaction('✅')
        await ctx.bot.close()


    '''TASK LOOP'''

    @tasks.loop(minutes=10)
    async def fufill_subscriptions(self):
        # Push today's subscriptions on or after 2AM if they haven't been already
        if (self.last_fufill != datetime.date.today()) and (datetime.datetime.now().hour >= 2):
            # Make sure the cached lectionary embeds are updated
            self.regenerate_all_data()
            self.build_all_embeds()

            conn = sqlite3.connect('data.db')
            c    = conn.cursor()
            c.execute('SELECT * FROM subscriptions')
            subscriptions = c.fetchall()

            for subscription in subscriptions:
                channel  = self.bot.get_channel(subscription[1])
                sub_type = subscription[2]

                if channel:
                    for embed in self.feeds[sub_type]:
                        await channel.send(embed=embed)
                else:
                    c.execute('DELETE FROM subscriptions WHERE channel_id = ?', (channel_id,))
                        
            conn.commit()
            conn.close()

            self.last_fufill = datetime.date.today()
    

    @fufill_subscriptions.before_loop
    async def before_fufill_subscriptions(self):
        await self.bot.wait_until_ready()


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