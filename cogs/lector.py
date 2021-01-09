from lectionary.armenian import ArmenianLectionary
from lectionary.catholic import CatholicLectionary
from lectionary.orthodox import OrthodoxLectionary
from lectionary.rcl      import RevisedCommonLectionary

from helpers.logger import log

import discord
from discord.ext import commands, tasks

import sqlite3
import typing
import re
import datetime


class Lectionary(commands.Cog):
    def __init__(self, bot):
        self.bot         = bot
        self.error_embed = discord.Embed(title='The lectionary could not be fetched', color=discord.Colour.red())

        # This list is for indexing-display purposes
        # In the database, 0 through 3 coorspond to these
        self.lectionary_names = [
            'armenian',
            'catholic',
            'orthodox',
            'revised common']

        # Lectionary Objects
        self.armenian = ArmenianLectionary()
        self.catholic = CatholicLectionary()
        self.orthodox = OrthodoxLectionary()
        self.rcl      = RevisedCommonLectionary()
        log('Initial data fetch')

        self.build_all_embeds()

        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('PRAGMA foreign_keys = ON')

        # Set up guild settings table if it isn't already
        c.execute('''
            CREATE TABLE IF NOT EXISTS GuildSettings (
                guild_id INTEGER NOT NULL,
                time     INTEGER NOT NULL,
                PRIMARY KEY (guild_id)
            )
        ''')

        # Set up subscription table if it isn't already
        c.execute('''
            CREATE TABLE IF NOT EXISTS Subscriptions (
                guild_id   INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                sub_type   INTEGER NOT NULL,
                FOREIGN KEY (guild_id) REFERENCES GuildSettings(guild_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()

        # Start up the event loop
        self.last_fufill = datetime.datetime.utcnow().hour
        self.fufill_subscriptions.start()

        log(f'Bot booted; will not fufill subscriptions for today from {self.last_fufill}:00 GMT or prior')

    
    def regenerate_all_data(self):
        self.armenian.regenerate_data()
        self.catholic.regenerate_data()
        self.orthodox.regenerate_data()
        self.rcl.regenerate_data()
        log('Lectionary data refetched')


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

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    # async def time(self, ctx, time:int=None, meridiem:str=None):   
    async def time(self, ctx, *, time=''):
        if (time == ''):
            now     = datetime.datetime.utcnow()
            output  = now.strftime(f'It is currently: %A, %B {now.day}, %Y, %I:%M:%S %p (GMT).')
            output += '\nYou can specify a time in GMT for the guild\'s subscriptions.'
            await ctx.send(output)
            return
        # If the user specified an integer, it's possibly 24-hour time
        elif time in re.findall(r'[0-9]+', time): time = int(time)
        # If a meridiem was possibly specified
        else:
            time = time.lower()
            match = re.search(r'([0-9]+) *(am|pm)', time)
            if match:
                time = int(match.group(1))
                if match.group(2) == 'pm': time += 12
            else:
                await ctx.send('You didn\'t specify a valid time.')
                return
        
        if not(7 <= time <= 23):
            await ctx.send('You need to specify a time from 7 AM to 11 PM GMT.')
            return

        guild_id = ctx.guild.id

        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('PRAGMA foreign_keys = ON')

        c.execute('SELECT * FROM GuildSettings WHERE guild_id = ?', (guild_id,))
        setting = c.fetchone()

        if setting:
            c.execute('UPDATE GuildSettings SET time = ? WHERE guild_id = ?', (time, guild_id))
        else:
            c.execute('INSERT INTO GuildSettings VALUES (?, ?)', (guild_id, time))
        
        conn.commit()
        conn.close()

        await ctx.send(f'The guild\'s subscriptions will come {time}:00 GMT daily.')


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
        c.execute('PRAGMA foreign_keys = ON')

        if channel: channel_id = channel.id
        else:       channel_id = ctx.channel.id

        guild_id = ctx.guild.id

        # Check to see if the guild has a settings entry yet
        # If not, set its subscription fufillment time to 7
        c.execute('SELECT * FROM GuildSettings WHERE guild_id = ?', (guild_id,))
        row = c.fetchone()
        if not row:
            c.execute('INSERT INTO GuildSettings VALUES (?, ?)', (guild_id, 7))

        # Check to see if a subscription for the channel already exists
        c.execute('SELECT * FROM Subscriptions WHERE channel_id = ?', (channel_id,))
        row      = c.fetchone()
        sub_name = self.lectionary_names[sub_type].title()
        if row:
            if (row[2] == sub_type):
                # If channel subscription request would not actually change any settings
                await ctx.send(f'<#{channel_id}> is already subscribed to the {sub_name} Lectionary.')
            else:
                # If the channel's subscription is changing somehow
                c.execute('''
                    UPDATE Subscriptions
                    SET sub_type = ?
                    WHERE channel_id = ?''',
                    (sub_type, channel_id)
                )
                conn.commit()

                await ctx.send(f'The subscription for <#{channel_id}> has been updated to the {sub_name} Lectionary.')

        # If a subscription does not exist for the channel
        else:
            c.execute('INSERT INTO Subscriptions VALUES (?, ?, ?)', (guild_id, channel_id, sub_type))
            conn.commit()
            await ctx.send(f'<#{channel_id}> has been subscribed to the {sub_name} Lectionary.')

        conn.close()


    @commands.command(aliases=['unsub'])
    @commands.has_permissions(manage_messages=True)
    async def unsubscribe(self, ctx, channel: typing.Optional[typing.Union[discord.TextChannel, str]] = None):
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('PRAGMA foreign_keys = ON')

        if channel is None: channel = ctx.channel

        if isinstance(channel, discord.TextChannel):
            if channel:
                channel_id = channel.id
            else:
                channel_id = ctx.channel.id
            
            c.execute('SELECT * FROM Subscriptions WHERE channel_id = ?', (channel_id,))

            row = c.fetchone()

            if row:
                c.execute('DELETE FROM Subscriptions WHERE channel_id = ?', (channel_id,))
                conn.commit()
                await ctx.send(f'<#{channel_id}> has been unsubscribed.')
            else:
                await ctx.send(f'<#{channel_id}> is not subscribed to any lectionaries.')
        
        elif isinstance(channel, str) and (channel == 'all'):
            c.execute('DELETE FROM GuildSettings WHERE guild_id = ?', (ctx.guild.id,))
            conn.commit()

            await ctx.send(f'All subscriptions for {ctx.guild.name} have been removed.')
        
        else:
            await ctx.send('You didn\'t specify a valid unsubscription option.')

        conn.close()
    

    @commands.command(aliases=['subs'])
    @commands.has_permissions(manage_messages=True)
    async def subscriptions(self, ctx):
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('PRAGMA foreign_keys = ON')

        c.execute('SELECT time FROM GuildSettings WHERE guild_id = ?', (ctx.guild.id,))
        time = c.fetchone()
        if time:
            time = time[0] # Nonetype cannot be subscripted
        else:
            time = 7
            c.execute('INSERT INTO GuildSettings VALUES (?, ?)', (ctx.guild.id, time))

        conn.commit()

        # Get all the subscription entries for the current guild
        c.execute('SELECT * FROM Subscriptions WHERE guild_id = ?', (ctx.guild.id,))
        subscriptions = c.fetchall()
        conn.close()

        embed = discord.Embed(title=f'Subscriptions for {ctx.guild.name}')
        if subscriptions:
            embed.description = ''
            for subscription in subscriptions:
                channel_id      = subscription[1]
                sub_name        = self.lectionary_names[subscription[2]].title()
                embed.description += f'\n<#{channel_id}> - {sub_name} Lectionary'

            embed.set_footer(text=f'(Daily @ {time}:00 GMT)')
        else:
            embed.description = 'There are none'
        
        await ctx.send(embed=embed)


    async def _remove_deleted_guilds(self):
        '''
        Helper method to purge the settings of deleted guilds from
        the database. The ON CASCADE DELETE option in the database
        also makes this wipe the subscriptions automatically.
        '''
        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('PRAGMA foreign_keys = ON')

        c.execute('SELECT guild_id FROM GuildSettings')
        guild_ids = [item[0] for item in c.fetchall()]
        
        total = len(guild_ids)
        count = 0

        for guild_id in guild_ids:
            if not self.bot.get_guild(guild_id):
                c.execute('DELETE FROM GuildSettings WHERE guild_id = ?', (guild_id ,))
                count += 1
        
        conn.commit()
        conn.close()

        log(f'Purged {count} out of {total} guilds')


    async def push_subscriptions(self, hour):
        await self._remove_deleted_guilds()

        conn = sqlite3.connect('data.db')
        c    = conn.cursor()
        c.execute('PRAGMA foreign_keys = ON')

        # Get all subscriptions for the guilds that have their time preference
        # set to the given hour
        c.execute('''
            SELECT Subscriptions.channel_id, Subscriptions.sub_type
            FROM Subscriptions
            INNER JOIN GuildSettings
            ON Subscriptions.guild_id = GuildSettings.guild_id
            WHERE GuildSettings.time = ?
        ''', (hour,))

        subscriptions = c.fetchall()
        # Each subscription is a tuple: (channel_id, sub_type)
        for subscription in subscriptions:
            channel_id = subscription[0]
            channel    = self.bot.get_channel(channel_id)
            sub_type   = subscription[1]

            if channel:
                for embed in self.feeds[sub_type]:
                    await channel.send(embed=embed)
            else:
                c.execute('DELETE FROM Subscriptions WHERE channel_id = ?', (channel_id,))
        
        conn.commit()
        conn.close()

        log(f'Pushed {len(subscriptions)} subscription(s) for {hour}:00 GMT')


    '''SYSTEM COMMANDS'''

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        '''
        Command to safely shutdown the bot with a reduced chance of
        damaging the database. (Bot owner only.)
        '''
        self.fufill_subscriptions.stop()
        await ctx.message.add_reaction('✅')
        log('Shutdown request, logging out')
        await ctx.bot.close()


    @commands.command()
    @commands.is_owner()
    async def push(self, ctx, current_hour:int=datetime.datetime.utcnow().hour):
        log(f'Manual subscription push requested for {current_hour}:00 GMT')

        if 7 <= current_hour <= 23:
            self.regenerate_all_data()
            self.build_all_embeds()
            await self.push_subscriptions(current_hour)


    '''TASK LOOP'''

    @tasks.loop(minutes=10)
    async def fufill_subscriptions(self):
        # Push the current hour's subscriptions if they haven't been already
        current_hour = datetime.datetime.utcnow().hour
        log(f'Subscription check for {current_hour}:00 GMT; last fufillment was {self.last_fufill}:00 GMT')

        if (7 <= current_hour <= 23) and (self.last_fufill != current_hour):
            # Make sure the lectionary embeds are updated for the day
            if (current_hour == 7):
                self.regenerate_all_data()
                self.build_all_embeds()

            await self.push_subscriptions(current_hour)
            self.last_fufill = current_hour
    

    @fufill_subscriptions.before_loop
    async def before_fufill_subscriptions(self):
        await self.bot.wait_until_ready()
    

def setup(bot):
    bot.add_cog(Lectionary(bot))