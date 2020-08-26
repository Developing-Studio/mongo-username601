import discord
from discord.ext import commands
import sys
sys.path.append('/home/runner/hosting601/modules')
import username601 as myself
from decorators import command, cooldown
from username601 import *
from datetime import datetime as t
from database import selfDB, username601Stats

class bothelp(commands.Cog):
    def __init__(self, client):
        self.client = client

    @command('supportserver,support-server,botserver,bot-server')
    @cooldown(1)
    async def support(self, ctx):
        return await ctx.send(Config.SupportServer.invite)

    @command('commands,yardim,yardım')
    @cooldown(1)
    async def help(self, ctx, *args):
        data = myself.jsonisp("https://vierofernando.github.io/username601/assets/json/commands.json")
        types = Config.cmdtypes
        args = list(args)
        if len(args)<1:
            cate = ''
            for i in range(0, len(types)):
                cate += f'**{str(i+1)}. **[{Config.prefix}help {str(types[i])}](https://vierofernando.github.io/username601/commands?category={i})\n'
            embed = discord.Embed(
                title='Username601\'s commands',
                description='[Join the support server]('+str(Config.SupportServer.invite)+') | [Vote us on top.gg](https://top.gg/bot/'+str(Config.id)+'/vote)\n\n**[More information on our website here.](https://vierofernando.github.io/username601/commands)**\n**Command Categories:** \n'+str(cate),
                colour=discord.Colour.from_rgb(201, 160, 112)
            )
            embed.set_footer(text=f'Type {Config.prefix}help <command/category> for more details.')
            await ctx.send(embed=embed)
        else:
            source = None
            typ = ''
            category_name = None
            query = ' '.join(list(args))
            for i in range(0, len(types)):
                if query.lower()==types[i].lower():
                    source = data[i][types[i]]
                    typ = 'Category'
                    category_name = types[i]
                    break
            if source==None:
                for i in range(0, len(data)):
                    for j in range(0, len(data[i][types[i]])):
                        if query.lower()==data[i][types[i]][j]['n'].lower():
                            source = data[i][types[i]][j]
                            typ = 'Command'
                            break
                    if not typ=='':
                        break
            if source==None:
                await ctx.send('Oops... Your command doesn\'t seem to exist.')
            else:
                if typ=='Category':
                    cmds = []
                    for i in range(0, len(source)):
                        cmds.append(source[i]['n'])
                    cmds = myself.dearray(cmds)
                    embed = discord.Embed(title='Category help for '+str(category_name)+':', description='**Commands:** \n```'+str(cmds)+'```', colour=discord.Colour.from_rgb(201, 160, 112))
                if typ=='Command':
                    parameters = 'No parameters required.'
                    if len(source['p'])>0:
                        parameters = ''
                        for i in range(0, len(source['p'])):
                            parameters += '**'+source['p'][i]+'**\n'
                    embed = discord.Embed(title='Command help for '+str(source['n'])+':', description='**Function: **'+str(source['f'])+'\n**Parameters:** \n'+str(parameters), colour=discord.Colour.from_rgb(201, 160, 112))
                await ctx.send(embed=embed)

    @command()
    @cooldown(1)
    async def vote(self, ctx):
        embed = discord.Embed(title='Support by Voting us at top.gg!', description='Sure thing, mate! [Vote us at top.gg by clicking me!](https://top.gg/bot/'+str(Config.id)+'/vote)', colour=discord.Colour.from_rgb(201, 160, 112))
        await ctx.send(embed=embed)
    
    @command()
    @cooldown(1)
    async def github(self, ctx):
        embed = discord.Embed(title="Click me to visit the Bot's github page.", colour=discord.Colour.from_rgb(201, 160, 112), url='https://github.com/vierofernando/username601')
        await ctx.send(embed=embed)
    
    @command('inviteme,invitelink,botinvite,invitebot,addtoserver,addbot')
    @cooldown(1)
    async def invite(self, ctx):
        embed = discord.Embed(
            title='Sure thing! Invite this bot to your server by clicking me.',
            description='[Invite link](https://discord.com/api/oauth2/authorize?client_id='+str(Config.id)+'&permissions=8&scope=bot) | [Support Server]('+str(Config.SupportServer.invite)+')',
            colour=discord.Colour.from_rgb(201, 160, 112)
        )
        await ctx.send(embed=embed)
    
    @command('report,suggest,bug,reportbug,bugreport')
    @cooldown(30)
    async def feedback(self, ctx, *args):
        if len(list(args))==0:
            await ctx.send(str(self.client.get_emoji(BotEmotes.error))+' | Where\'s the feedback? :(')
        elif len(list(args))>1000:
            await ctx.send(str(self.client.get_emoji(BotEmotes.error))+' | That\'s too long! Please provide a simpler description.')
        elif 'discord.gg/' in ' '.join(list(args)):
            await ctx.send(str(self.client.get_emoji(BotEmotes.error))+' | Do NOT send discord invites through feedback! Use the advertising channel in our support server instead!')
        else:
            wait = await ctx.send(str(self.client.get_emoji(BotEmotes.loading)) + ' | Please wait... Transmitting data to owner...')
            banned = selfDB.is_banned(ctx.message.author.id)
            if not banned:
                try:
                    fb = ' '.join(list(args))
                    feedbackCh = self.client.get_channel(Config.SupportServer.feedback)
                    await feedbackCh.send('<@'+str(Config.owner.id)+'>, User with ID: '+str(ctx.message.author.id)+' sent a feedback: **"'+str(fb)+'"**')
                    embed = discord.Embed(title='Feedback Successful', description=str(self.client.get_emoji(BotEmotes.success)) + '** | Success!**\nThanks for the feedback!\n**We will DM you as the response. **If you are unsatisfied, [Join our support server and give us more details.]('+str(Config.SupportServer.invite)+')',colour=discord.Colour.from_rgb(201, 160, 112))
                    await wait.edit(content='', embed=embed)
                except:
                    await wait.edit(content=str(self.client.get_emoji(BotEmotes.error)) + ' | Error: There was an error while sending your feedback. Sorry! :(')
            else:
                await wait.edit(content='', embed=discord.Embed(
                    title="You have been banned from using the Feedback command.",
                    description="**Reason: **```"+str(banned)+"```",
                    color=discord.Colour.red()
                ))
    @command()
    @cooldown(5)
    async def ping(self, ctx):
        dbping = selfDB.ping()
        webping = myself.ping()
        ping = str(round(self.client.latency*1000))
        embed = discord.Embed(title=f'Pong!', description=f'**Client Latency:** {ping} ms.\n**Message Latency:** {str(round(int((t.now()-ctx.message.created_at).microseconds)/1000))} ms.\n**Database latency:** {dbping} ms.\n**Hosting latency: **{webping} ms.', colour=discord.Colour.from_rgb(201, 160, 112))
        embed.set_thumbnail(url='https://i.pinimg.com/originals/21/02/a1/2102a19ea556e1d1c54f40a3eda0d775.gif')
        await ctx.send(embed=embed)
    
    @command('botstats,meta')
    @cooldown(15)
    async def stats(self, ctx):
        up, cmds, commandLength = selfDB.get_uptime(), username601Stats.retrieveData(), myself.getCommandLength()
        imageurl = myself.urlify(myself.uptimerobot())
        bot_uptime = up.split('|')[0].split(':')[0]+' Hours, '+up.split('|')[0].split(':')[1]+' minutes, '+up.split('|')[0].split(':')[2]+' seconds.'
        embed = discord.Embed(description='This bot is in {} servers.\nWith {} users\n\nBot uptime: {}\nOS uptime: {}\nLast downtime: {} UTC\n\nCommands run in the past {}: {}'.format(len(self.client.guilds), len(self.client.users), bot_uptime, str(myself.terminal('uptime -p'))[3:], up.split('|')[1], myself.time_encode(round(t.now().timestamp()) - round(cmds['lastreset'])), str(cmds['count'])), color=discord.Colour.from_rgb(201, 160, 112))
        embed.set_image(url='https://quickchart.io/chart?c='+imageurl)
        await ctx.send(embed=embed)

    @command('botinfo,aboutbot,bot,username601')
    @cooldown(5)
    async def about(self, ctx):
        if str(self.client.get_guild(Config.SupportServer.id).get_member(Config.owner.id).status)=='offline': devstatus = 'Offline'
        else: devstatus = 'Online'
        embed = discord.Embed(title = 'About '+str(ctx.message.guild.get_member(Config.id).display_name), colour = discord.Colour.from_rgb(201, 160, 112))
        embed.add_field(name='Bot general Info', value='**Bot name: ** Username601\n**Library: **Discord.py\n**Default prefix: **'+str(Config.prefix))
        embed.add_field(name='Programmer info', value='**Programmed by: **'+str(self.client.get_user(Config.owner.id))+'\n(Indie developed)\n**Current Discord Status:** '+devstatus)
        embed.add_field(name='Version Info', value='**Bot version: ** '+Config.Version.number+'\n**Changelog: **'+Config.Version.changelog)#+'\n'+str(osinfo))
        embed.add_field(name='Links', value='[Invite this bot to your server!](http://vierofernando.github.io/programs/username601)\n[The support server!]('+str(Config.SupportServer.invite)+')\n[Vote us on top.gg](https://top.gg/bot/'+str(Config.id)+'/vote)\n[Official Website](https://vierofernando.github.io/username601)')
        embed.set_thumbnail(url='https://raw.githubusercontent.com/vierofernando/username601/master/assets/pics/pfp.png')
        embed.set_footer(text='© Viero Fernando Programming, 2020. All rights reserved.')
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(bothelp(client))
