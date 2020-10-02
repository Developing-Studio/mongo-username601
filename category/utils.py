import discord
from discord.ext import commands
import sys
from os import getcwd, name, environ
sys.path.append(environ['BOT_MODULES_DIR'])
from decorators import command, cooldown
import random
from io import BytesIO
from requests import post, get
from json import loads
from datetime import datetime as t

class utils(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @command('colorthief,getcolor,accent,accentcolor,accent-color,colorpalette,color-palette')
    @cooldown(3)
    async def palette(self, ctx, *args):
        url, person = self.client.utils.getUserAvatar(ctx, args), self.client.utils.getUser(ctx, args)
        async with ctx.channel.typing():
            data = self.client.canvas.get_multiple_accents(url)
            return await ctx.send(file=discord.File(self.client.canvas.get_palette(data), 'palette.png'))

    @command('isitup,webstatus')
    @cooldown(2)
    async def isitdown(self, ctx, *args):
        if len(list(args))==0: return await ctx.send('{} | Please send a website link...'.format(self.client.utils.emote(self.client, 'error')))
        wait = await ctx.send('{} | Pinging...'.format(self.client.utils.emote(self.client, 'loading')))
        web = list(args)[0].replace('<', '').replace('>', '')
        if not web.startswith('http'): web = 'http://' + web
        try:
            a = t.now()
            ping = get(web, timeout=5)
            pingtime = round((t.now()-a).total_seconds()*1000)
            await wait.edit(content='{} | That website is up.\nPing: {} ms\nStatus code: {}'.format(self.client.utils.emote(self.client, 'success'), pingtime, ping.status_code))
        except:
            await wait.edit(content='{} | Yes. that website is down.'.format(self.client.utils.emote(self.client, 'error')))
    
    @command('img2ascii,imagetoascii,avascii,avatarascii,avatar2ascii,av2ascii')
    @cooldown(10)
    async def imgascii(self, ctx, *args):
        parsed_arg = self.client.utils.parse_parameter(args, '--img')
        if parsed_arg['available']:
            args = parsed_arg['parsedarg']
            url = self.client.utils.getUserAvatar(ctx, args)
            async with ctx.channel.typing():
                res_im = self.client.canvas.imagetoASCII_picture(url)
                return await ctx.send(file=discord.File(res_im, 'imgascii.png'))
        url = self.client.utils.getUserAvatar(ctx, args)
        wait = await ctx.send('{} | Please wait...'.format(self.client.utils.emote(self.client, 'loading')))
        text = self.client.canvas.imagetoASCII(url)
        try:
            data = post("https://hastebin.com/documents", data=text, timeout=3)
            assert data.status_code == 200
        except:
            await wait.delete()
            file = discord.File(BytesIO(bytes(text, 'utf-8')), filename='ascii.txt')
            return await ctx.send(content="{} | Oops! there was an error on posting it there. Don't worry, instead i send it as an attachment here:\n(Tip: you can also add `--img` so i send it as an image attachment!)".format(self.client.utils.emote(self.client, 'error')), file=file)
        return await wait.edit(content='{} | You can see the results at **https://hastebin.com/{}**!'.format(self.client.utils.emote(self.client, 'success'), data.json()['key']))
    
    @command()
    @cooldown(15)
    async def nasa(self, ctx, *args):
        query = 'earth' if len(list(args))==0 else self.client.utils.urlify(' '.join(list(args)))
        data = self.client.utils.fetchJSON(f'https://images-api.nasa.gov/search?q={query}&media_type=image')
        await ctx.channel.trigger_typing()
        if len(data['collection']['items'])==0: return await ctx.send('{} | Nothing found.'.format(self.client.utils.emote(self.client, 'error')))
        img = random.choice(data['collection']['items'])
        em = discord.Embed(title=img['data'][0]['title'], description=img['data'][0]["description"], color=self.client.utils.get_embed_color())
        em.set_image(url=img['links'][0]['href'])
        await ctx.send(embed=em)

    @command('pokedex,dex,bulbapedia,pokemoninfo,poke-info,poke-dex,pokepedia')
    @cooldown(10)
    async def pokeinfo(self, ctx, *args):
        query = 'Missingno' if (len(list(args))==0) else self.client.utils.urlify(' '.join(list(args)))
        try:
            data = self.client.utils.fetchJSON('https://bulbapedia.bulbagarden.net/w/api.php?action=query&titles={}&format=json&formatversion=2&pithumbsize=150&prop=extracts|pageimages&explaintext&redirects&exintro'.format(query))
            embed = discord.Embed(
                url='https://bulbapedia.bulbagarden.net/wiki/{}'.format(query),
                color=self.client.utils.get_embed_color(),
                title=data['query']['pages'][0]['title'], description=data['query']['pages'][0]['extract'][0:1000]
            )
            try:
                pokeimg = data['query']['pages'][0]['thumbnail']['source']
                embed.set_thumbnail(url=pokeimg)
            except: pass
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            return await ctx.send("{} | Pokemon not found!".format(
                str(self.client.utils.emote(self.client, 'error'))
            ))

    @command('recipes,cook')
    @cooldown(2)
    async def recipe(self, ctx, *args):
        if len(list(args))==0:
            await ctx.send(embed=discord.Embed(title='Here is a recipe to cook nothing:', description='1. Do nothing\n2. Profit'))
        else:
            data = self.client.utils.fetchJSON("http://www.recipepuppy.com/api/?q={}".format(self.client.utils.urlify(' '.join(list(args)))))
            if len(data['results'])==0: 
                await ctx.send("{} | Did not find anything.".format(str(self.client.utils.emote(self.client, 'error'))))
            elif len([i for i in data['results'] if i['thumbnail']!=''])==0:
                await ctx.send("{} | Did not find anything with a delicious picture.".format(str(self.client.utils.emote(self.client, 'error'))))
            else:
                total = random.choice([i for i in data['results'] if i['thumbnail']!=''])
                embed = discord.Embed(title=total['title'], url=total['href'], description='Ingredients:\n{}'.format(total['ingredients']), color=self.client.utils.get_embed_color())
                embed.set_image(url=total['thumbnail'])
                await ctx.send(embed=embed)

    @command()
    @cooldown(5)
    async def time(self, ctx):
        data = self.client.utils.fetchJSON("http://worldtimeapi.org/api/timezone/africa/accra")
        year, time, date = str(data["utc_datetime"])[:-28], str(data["utc_datetime"])[:-22], str(str(data["utc_datetime"])[:-13])[11:]
        if int(year)%4==0: yearType, yearLength = 'It is a leap year.', 366
        else: yearType, yearLength = 'It is not a leap year yet.', 365
        progressDayYear = round(int(data["day_of_year"])/int(yearLength)*100)
        progressDayWeek = round(int(data["day_of_week"])/7*100)
        embed = discord.Embed(
            title = str(date)+' | '+str(time)+' (API)',
            description = str(t.now())[:-7]+' (SYSTEM)\nBoth time above is on UTC.\n**Unix Time:** '+str(data["unixtime"])+'\n**Day of the year: **'+str(data["day_of_year"])+' ('+str(progressDayYear)+'%)\n**Day of the week: **'+str(data["day_of_week"])+' ('+str(progressDayWeek)+'%)\n'+str(yearType),
            colour = self.client.utils.get_embed_color()
        )
        await ctx.send(embed=embed)
    @command()
    @cooldown(3)
    async def calc(self, ctx, *args):
        if len(list(args))==0: await ctx.send(str(self.client.utils.emote(self.client, 'error'))+" | You need something... i smell no args nearby.")
        else:
            start_counting = True
            for i in list('abcdefghijklmnopqrstuvwxyz.'):
                if i in ''.join(list(args)).lower():
                    start_counting = False
                    break
            if start_counting:
                try: # i know it's eval, but at least it is protected
                    result = eval(' '.join(list(args)))
                    await ctx.send('`'+str(result)+'`')
                except:
                    await ctx.send(str(self.client.utils.emote(self.client, 'error'))+" | Somehow your calculation returns an error...")             
    @command()
    @cooldown(7)
    async def quote(self, ctx):
        async with ctx.channel.typing():
            data = self.client.utils.insp('https://quotes.herokuapp.com/libraries/math/random')
            text, quoter = data.split(' -- ')[0], data.split(' -- ')[1]
            await ctx.send(embed=discord.Embed(description=f'***{text}***\n\n-- {quoter} --', color=self.client.utils.get_embed_color()))

    @command()
    @cooldown(10)
    async def robohash(self, ctx, *args):
        if len(list(args))==0: url='https://robohash.org/'+str(src.randomhash())
        else: url = 'https://robohash.org/'+str(self.client.utils.urlify(' '.join(list(args))))
        await ctx.send(file=discord.File(self.client.canvas.urltoimage(url), 'robohash.png'))

    @command()
    @cooldown(10)
    async def weather(self, ctx, *args):
        if len(list(args))==0: await ctx.send(str(self.client.utils.emote(self.client, 'error'))+" | Please send a location or a city!")
        else: await ctx.send(file=discord.File(self.client.canvas.urltoimage('https://wttr.in/'+str(self.client.utils.urlify(' '.join(list(args))))+'.png?m'), 'weather.png'))

    @command()
    @cooldown(10)
    async def ufo(self, ctx):
        num = str(random.randint(50, 100))
        data = self.client.utils.fetchJSON('http://ufo-api.herokuapp.com/api/sightings/search?limit='+num)
        if data['status']!='OK':
            await ctx.send(str(self.client.utils.emote(self.client, 'error'))+' | There was a problem on retrieving the info.\nThe server said: "'+str(data['status'])+'" :eyes:')
        else:
            ufo = random.choice(data['sightings'])
            embed = discord.Embed(title='UFO Sighting in '+str(ufo['city'])+', '+str(ufo['state']), description='**Summary:** '+str(ufo['summary'])+'\n\n**Shape:** '+str(ufo['shape'])+'\n**Sighting Date: **'+str(ufo['date'])[:-8].replace('T', ' ')+'\n**Duration: **'+str(ufo['duration'])+'\n\n[Article Source]('+str(ufo['url'])+')', colour=self.client.utils.get_embed_color())
            embed.set_footer(text='Username601 raided area 51 and found this!')
            await ctx.send(embed=embed)
    
    @command('rhymes')
    @cooldown(7)
    async def rhyme(self, ctx, *args):
        if len(list(args))==0: await ctx.send('Please input a word! And we will try to find the word that best rhymes with it.')
        else:
            wait, words = await ctx.send(str(self.client.utils.emote(self.client, 'loading')) + ' | Please wait... Searching...'), []
            data = self.client.utils.fetchJSON('https://rhymebrain.com/talk?function=getRhymes&word='+str(self.client.utils.urlify(' '.join(list(args)))))
            if len(data)<1: await wait.edit(content='We did not find any rhyming words corresponding to that letter.')
            else:
                for i in range(0, len(data)):
                    if data[i]['flags']=='bc': words.append(data[i]['word'])
                words = dearray(words)
                if len(words)>1950:
                    words = limitify(words)
                embed = discord.Embed(title='Words that rhymes with '+str(' '.join(list(args)))+':', description=words, colour=self.client.utils.get_embed_color())
                await wait.edit(content='', embed=embed)

    @command('sof')
    @cooldown(12)
    async def stackoverflow(self, ctx, *args):
        if len(list(args))==0:
            await ctx.send(str(self.client.utils.emote(self.client, 'error'))+' | Hey fellow developer, Try add a question!')
        else:
            try:
                query = self.client.utils.urlify(' '.join(list(args)))
                data = self.client.utils.fetchJSON("https://api.stackexchange.com/2.2/search/advanced?q="+str(query)+"&site=stackoverflow&page=1&answers=1&order=asc&sort=relevance")
                leng = len(data['items'])
                ques = data['items'][0]
                tags = ''
                for i in range(0, len(ques['tags'])):
                    if i==len(ques['tags'])-1:
                        tags += '['+str(ques['tags'][i])+'](https://stackoverflow.com/questions/tagged/'+str(ques['tags'][i])+')'
                        break
                    tags += '['+str(ques['tags'][i])+'](https://stackoverflow.com/questions/tagged/'+str(ques['tags'][i])+') | '
                embed = discord.Embed(title=ques['title'], description='**'+str(ques['view_count'])+' *desperate* developers looked into this post.**\n**TAGS:** '+str(tags), url=ques['link'], colour=self.client.utils.get_embed_color())
                embed.set_author(name=ques['owner']['display_name'], url=ques['owner']['link'], icon_url=ques['owner']['profile_image'])
                embed.set_footer(text='Shown 1 result out of '+str(leng)+' results!')
                await ctx.send(embed=embed)
            except:
                await ctx.send(str(self.client.utils.emote(self.client, 'error')) + ' | There was an error on searching! Please check your spelling :eyes:')

    @command('birbfact,birdfact')
    @cooldown(7)
    async def pandafact(self, ctx):
        if 'pandafact' in str(ctx.message.content).lower(): link = 'https://some-random-api.ml/facts/panda'
        else: link = 'https://some-random-api.ml/facts/bird'
        data = self.client.utils.fetchJSON(link)['fact']
        await ctx.send(embed=discord.Embed(title='Did you know?', description=data, colour=self.client.utils.get_embed_color()))

    @command()
    @cooldown(2)
    async def iss(self, ctx):
        iss, ppl, total = self.client.utils.fetchJSON('https://open-notify-api.herokuapp.com/iss-now.json'), self.client.utils.fetchJSON('https://open-notify-api.herokuapp.com/astros.json'), '```'
        for i in range(0, len(ppl['people'])):
            total += str(i+1) + '. ' + ppl['people'][i]['name'] + ((20-(len(ppl['people'][i]['name'])))*' ') + ppl['people'][i]['craft'] + '\n'
        embed = discord.Embed(title='Position: '+str(iss['iss_position']['latitude'])+' '+str(iss['iss_position']['longitude']), description='**People at craft:**\n\n'+str(total)+'```', colour=self.client.utils.get_embed_color())
        await ctx.send(embed=embed)

    @command('ghibli')
    @cooldown(5)
    async def ghiblifilms(self, ctx, *args):
        wait = await ctx.send(str(self.client.utils.emote(self.client, 'loading')) + ' | Please wait... Getting data...')
        data = self.client.utils.fetchJSON('https://ghibliapi.herokuapp.com/films')
        if len(list(args))==0:
            films = ""
            for i in range(0, int(len(data))):
                films = films+'('+str(int(i)+1)+') '+str(data[i]['title']+' ('+str(data[i]['release_date'])+')\n')
            embed = discord.Embed(
                title = 'List of Ghibli Films',
                description = str(films),
                color = self.client.utils.get_embed_color()
            )
            embed.set_footer(text='Type `'+str(self.client.utils.prefix)+'ghibli <number>` to get each movie info.')
            await wait.edit(content='', embed=embed)
        else:
            try:
                num = int([i for i in list(args) if i.isnumeric()][0])-1
                embed = discord.Embed(
                    title = data[num]['title'] + ' ('+str(data[num]['release_date'])+')',
                    description = '**Rotten Tomatoes Rating: '+str(data[num]['rt_score'])+'%**\n'+data[num]['description'],
                    color = self.client.utils.get_embed_color()
                )
                embed.add_field(name='Directed by', value=data[num]['director'], inline='True')
                embed.add_field(name='Produced by', value=data[num]['producer'], inline='True')
                await wait.edit(content='', embed=embed)
            except: await wait.edit(content=str(self.client.utils.emote(self.client, 'error'))+' | the movie you requested does not exist!?')

    @command()
    @cooldown(10)
    async def steamprofile(self, ctx, *args):
        try:
            getprof = self.client.utils.urlify(list(args)[0].lower())
            data = self.client.utils.fetchJSON('https://api.alexflipnote.dev/steam/user/'+str(getprof))
            state, privacy, url, username, avatar, custom_url, steam_id = data["state"], data["privacy"], data["url"], data["username"], data["avatarfull"], data["customurl"], data["steamid64"]
            embed = discord.Embed(title=username, description='**[Profile Link]('+str(url)+')**\n**Current state: **'+str(state)+'\n**Privacy: **'+str(privacy)+'\n**[Profile pic URL]('+str(avatar)+')**', colour = self.client.utils.get_embed_color())
            embed.set_thumbnail(url=avatar)
            await ctx.send(embed=embed)
        except:
            await ctx.send(str(self.client.utils.emote(self.client, 'error'))+" | Error; profile not found!")

    @command('nation')
    @cooldown(5)
    async def country(self, ctx, *args):
        try:
            country = self.client.utils.urlify(' '.join(list(args)))
            data = self.client.canvas.country(country)
            file = discord.File(data['buffer'], 'country.png')
            embed = discord.Embed(title=' '.join(list(args)), color=discord.Color.from_rgb(
                data['color'][0], data['color'][1], data['color'][2]
            ))
            embed.set_thumbnail(url=data['image'])
            embed.set_image(url='attachment://country.png')
            return await ctx.send(file=file, embed=embed)
        except:
            return await ctx.send('{} | Country not found!'.format(self.client.utils.emote(self.client, 'error')))

    @command()
    @cooldown(5)
    async def bored(self, ctx):
        data = self.client.utils.fetchJSON("https://www.boredapi.com/api/activity?participants=1")
        await ctx.send('**Feeling bored?**\nWhy don\'t you '+str(data['activity'])+'? :wink::ok_hand:')

    @command()
    @cooldown(20)
    async def googledoodle(self, ctx):
        wait = await ctx.send(str(self.client.utils.emote(self.client, 'loading')) + ' | Please wait... This may take a few moments...')
        data = self.client.utils.fetchJSON('https://www.google.com/doodles/json/{}/{}'.format(str(t.now().year), str(t.now().month)))[0]
        embed = discord.Embed(title=data['title'], colour=self.client.utils.get_embed_color(), url='https://www.google.com/doodles/'+data['name'])
        embed.set_image(url='https:'+data['high_res_url'])
        embed.set_footer(text='Event date: '+str('/'.join(
            [str(i) for i in data['run_date_array'][::-1]]
        )))
        await wait.edit(content='', embed=embed)

    @command()
    @cooldown(10)
    async def steamapp(self, ctx, *args):
        data = self.client.utils.fetchJSON('https://store.steampowered.com/api/storesearch?term='+self.client.utils.urlify(str(' '.join(list(args))))+'&cc=us&l=en')
        if data['total']==0: await ctx.send(str(self.client.utils.emote(self.client, 'error'))+' | Did not found anything. Maybe that app *doesn\'t exist...*')
        else:
            try:
                prize = data['items'][0]['price']['initial']
                prize = str(prize / 100)+ ' ' + data['items'][0]['price']['currency']
            except KeyError: prize = 'FREE'
            if data['items'][0]['metascore']=="": rate = '???'
            else: rate = str(data['items'][0]['metascore'])
            oss_raw = []
            for i in range(0, len(data['items'][0]['platforms'])):
                if data['items'][0]['platforms'][str(list(data['items'][0]['platforms'].keys())[i])]==True:
                    oss_raw.append(str(list(data['items'][0]['platforms'].keys())[i]))
            embed = discord.Embed(title=data['items'][0]['name'], url='https://store.steampowered.com/'+str(data['items'][0]['type'])+'/'+str(data['items'][0]['id']), description='**Price tag:** '+str(prize)+'\n**Metascore: **'+str(rate)+'\n**This app supports the following OSs: **'+str(dearray(oss_raw)), colour=self.client.utils.get_embed_color())
            embed.set_image(url=data['items'][0]['tiny_image'])
            await ctx.send(embed=embed)

    @command('dogfact,funfact')
    @cooldown(6)
    async def catfact(self, ctx):
        if 'cat' in str(ctx.message.content).lower(): await ctx.send('**Did you know?**\n'+str(self.client.utils.fetchJSON("https://catfact.ninja/fact")['fact']))
        elif 'dog' in str(ctx.message.content).lower(): await ctx.send('**Did you know?**\n'+str(self.client.utils.fetchJSON("https://dog-api.kinduff.com/api/facts")['facts'][0]))
        else:
            await ctx.send('**Did you know?**\n'+str(self.client.utils.fetchJSON("https://useless-api--vierofernando.repl.co/randomfact")['fact']))
    @command('em')
    @cooldown(2)
    async def embed(self, ctx, *args):
        try:
            return await ctx.send(embed=discord.Embed(description=' '.join(list(args))))
        except:
            return await ctx.message.add_reaction(self.client.utils.emote(self.client, 'error'))
            
    @command('col')
    @cooldown(3)
    async def color(self, ctx, *args):
        if len(list(args)) == 0: return await ctx.send("{} | Invalid argument. use `{}help color` for more info.".format(self.client.utils.emote(self.client, 'error')), self.client.utils.prefix)
        async with ctx.channel.typing():
            parameter_data = self.client.utils.parse_parameter(args, 'role', get_second_element=True)
            if parameter_data['available']:
                iterate_result = [i.id for i in ctx.guild.roles if parameter_data['secondparam'].lower() in i.name.lower()]
                if len(iterate_result) == 0: return await ctx.send("{} | Role not found.".format(self.client.utils.emote(self.client, 'error')))
                colim = self.client.canvas.color(str(ctx.guild.get_role(iterate_result[0]).colour))
            else:
                colim = self.client.canvas.color(None, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))) if self.client.utils.parse_parameter(args, 'random')['available'] else self.client.canvas.color(' '.join(list(args)))
            if colim == None: return await ctx.send("{} | Invalid hex color.".format(self.client.utils.emote(self.client, 'error')))
            return await ctx.send(file=discord.File(colim, 'color.png'))
    
    @command('fast')
    @cooldown(10)
    async def typingtest(self, ctx):
        async with ctx.channel.typing():
            data = self.client.utils.fetchJSON("https://random-word-api.herokuapp.com/word?number=5")
            text, guy, first = arrspace(data), ctx.author, t.now().timestamp()
            main = await ctx.send(content='**Type the text on the image. (Only command invoker can play)**\nYou have 2 minutes.\n', file=discord.File(self.client.canvas.simpletext(text), 'test.png'))
        def check(m):
            return m.author == guy
        try:
            trying = await self.client.wait_for('message', check=check, timeout=120.0)
        except:
            await main.edit(content='Time is up.')
        if str(trying.content)!=None:
            offset = t.now().timestamp()-first
            asked, answered, wrong = text.lower(), str(trying.content).lower(), 0
            for i in range(len(asked)):
                try:
                    if asked[i]!=answered[i]: wrong += 1
                except: break
            try: accuracy, cps = round((len(asked)-wrong)/len(asked)*100), round(len(answered)/offset)
            except: accuracy, cps = "???", "???"
            await ctx.send(embed=discord.Embed(title='TYPING TEST RESULTS', description='**Your time: **'+str(round(offset))+' seconds.\n**Your accuracy: **'+str(accuracy)+'%\n**Your speed: **'+str(cps)+' Characters per second.', colour=self.client.utils.get_embed_color()))

def setup(client):
    client.add_cog(utils(client))
