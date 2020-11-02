import discord
from discord.ext import commands, tasks
import os
import shutil
import asyncio
import json
import re


#Setup these enviorment names with the variable name being the name in the quotes
BOT_ID = os.environ.get('BOT_ID')
#API_KEY = os.environ.get('API_KEY')
GUILD_IDS = [702020759803134023]
BASE_ROLE = 702372853382643732
DEFAULT_NICKNAME_CHANNEL = "portal"
#URL = "https://api.jsonbin.io/b/5f47f33a514ec5112d0f825d"
#headers = {'Content-Type': 'application/json','secret-key':API_KEY}


client = commands.Bot(command_prefix="+")
client.remove_command('help')

with open('EmojiToCountry.json', encoding='utf8') as json_file:
    data = json.load(json_file)

with open('CountryStateCodes.json', encoding='utf8') as Country_State:
    Country_State_JSON = json.load(Country_State)

Country_State.close()
json_file.close()

SpecialCharacterPattern = re.compile(r"^[_A-z0-9]*((-|\s)*[_A-z0-9])*$")


@client.event
async def on_ready():
    print('Bot is ready.')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="NovaCrypt", large_image="primary"))

@client.event
async def on_member_join(member):
    print(f'{member.display_name} just joined')
    for channel in member.guild.channels:
        if channel.name == DEFAULT_NICKNAME_CHANNEL:
            await channel.send(f'{member.display_name} please type `+nickname (Username)` to change your username\nExample: `+nickname John`.')

@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(
        colour = discord.Colour.blue()
    )
    embed.set_author(name="Help Menu")
    embed.add_field(name=f'{ctx.prefix}help',value="Sends this embed to you.",inline=False)
    embed.add_field(name=f'{ctx.prefix}nickname',value="Use this in a server to change your nickname!",inline=False)
    embed.add_field(name=f'{ctx.prefix}convert',value=f"Converts ISO codes to locations. Try {ctx.prefix}convert for more info.",inline=False)

    await author.send(embed=embed)

#Converts ISO3 Tags to Country Names
@client.command(aliases=["country","ISO","Country"])
async def convert(ctx,Country,*State):
    Country = Country.upper()
    with open('CountryStateCodes.json',encoding='utf8') as ConversionTableJSON:
        ConversionTable = json.load(ConversionTableJSON)
        ConversionTableJSON.close()
        if Country in ConversionTable and len(Country)==2 and SpecialCharacterPattern.match(Country):
            response = "The country name is " + ConversionTable[Country]["name"] + ". "
            try:
                StateClean = SpecialCharacterPattern.match(State[0])
                State = Country + "-" + State[0].upper()
                if State in ConversionTable[Country]["divisions"] and len(State)<=6 and StateClean:
                    response = response + "The state/province/city name is " + ConversionTable[Country]["divisions"][State] + "."
                else:
                    response = response + "The state/province/city was unable to be found."    
            except:
                pass
            await ctx.send(response)
        else:
            await ctx.send("The country code was invalid, try again.")
@convert.error
async def convert_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Use this command to convert the tags from nicknames in the structure of `Nickname | [Region_Code] | [Country_Code]` to real locations.\nType `{ctx.prefix}convert (Country_Code) (Optional: Region_Code)`')

#Allows the user to change their nickname.
@client.command(aliases=["nick","Nick","Nickname"])
async def nickname(ctx, *, nickname):
    if len(nickname) <= 20 and SpecialCharacterPattern.match(nickname):
        get_flag = await ctx.send(f"Okay {ctx.message.author.mention}, **REACT** to this message with your country's flag. \n[Tutorial: https://support.discord.com/hc/en-us/articles/360041139231-Adding-Emojis-and-Reactions#h_eea1a076-21c7-4554-b593-7fe750b63ef8]")
        def check(reaction,user):
            return user == ctx.message.author and user != client.user and reaction.emoji in data.keys()

        try:
            reaction, user = await client.wait_for("reaction_add",timeout=120.0,check=check)
        except asyncio.TimeoutError:
            await get_flag.delete()
            await ctx.send(f"{ctx.message.author.display_name} you did not respond with a valid flag in time, terminating command. Please try again.")

        USER_COUNTRY_ID = data[reaction.emoji]
        USER_COUNTRY_INFO = Country_State_JSON[USER_COUNTRY_ID]
        USER_COUNTRY_NAME = USER_COUNTRY_INFO["name"]
        DIVISIONS = USER_COUNTRY_INFO['divisions']
        KEYS = sorted(list(DIVISIONS))
        EMBEDS = []
        await get_flag.delete()
        State_Info = await ctx.send(f'You stated that you live in {USER_COUNTRY_NAME}, please select a State/City/Province. Here are some valid codes.')
        if len(DIVISIONS) > 25:
            NumEmbeds = len(DIVISIONS)//25
            for i in range(NumEmbeds):
                embedVar = discord.Embed(title=f"{USER_COUNTRY_NAME}", description="Type the 2-3 letter code.", color=0x00b8ff)
                for j in range(25*i,25+25*i):
                    embedVar.add_field(name=KEYS[j].replace(f'{USER_COUNTRY_ID}-',''), value=DIVISIONS[KEYS[j]], inline=True)
                embeded_item = await ctx.send(embed=embedVar)
                EMBEDS.append(embeded_item)
            embedVar = discord.Embed(title=f"{USER_COUNTRY_NAME}", description="Type the 2-3 letter code.", color=0x00b8ff)
            for j in range(25*NumEmbeds,len(USER_COUNTRY_INFO["divisions"])):
                embedVar.add_field(name=KEYS[j].replace(f'{USER_COUNTRY_ID}-',''), value=DIVISIONS[KEYS[j]], inline=True)
            embeded_item = await ctx.send(embed=embedVar)
            EMBEDS.append(embeded_item)
        else:
            embedVar = discord.Embed(title=f"{USER_COUNTRY_NAME}", description="Type the 2-3 letter code.", color=0x00b8ff)
            for item in DIVISIONS:
                embedVar.add_field(name=item.replace(f'{USER_COUNTRY_ID}-',''), value=DIVISIONS[item], inline=True)
            await ctx.send(embed=embedVar)


        try:
            StateSelect = await client.wait_for("message", timeout=120.0, check=lambda message: message.author == ctx.author)
            if len(StateSelect.content) <= 3 and USER_COUNTRY_ID+"-"+StateSelect.content.upper() in DIVISIONS.keys():
                Complete_Nickname = f"{nickname} | {StateSelect.content.upper()} | {USER_COUNTRY_ID}"
                await ctx.message.author.edit(nick=Complete_Nickname)
                await ctx.send(f"Sucess! Your nickname has successfully been changed to {Complete_Nickname}. Welcome to NovaCrypt.")
                for role in ctx.guild.roles:
                    if role.id == BASE_ROLE:
                        ADD_ROLE = role
                await ctx.message.author.add_roles(ADD_ROLE,reason=f"Nickname Sucessfully Created [Nickname: {Complete_Nickname}]")
            else:
                await ctx.send(f"Command was unsuccessful, make sure the Code matches the ones offered exactly. Terminating command. Please try again.")
            for embed_item in EMBEDS:
                await embed_item.delete()
            await State_Info.delete()
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.message.author.display_name} you did not respond with a valid Code in time, terminating command. Please try again.")
            for embed_item in EMBEDS:
                await embed_item.delete()
            await State_Info.delete()
    else:
        await ctx.send("Your nickname is too long, please keep it within 20 letters. Special Characters are not permitted. Spaces are allowed. \nExample: `+nickname John`.")


@nickname.error
async def nickname_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Use this command to change your nickname, type `{ctx.prefix}nickname (Username)`\nExample: `+nickname John`.')


@tasks.loop(minutes=60.0)
async def NicknameCollection():
    for ID in GUILD_IDS:
        guild = client.get_guild(ID)
        guild_name_filtered = guild.name.split(" ")[0]
        src = os.path.join(os.getcwd(),"BaseGuildJson.json")
        dst = os.path.join(os.getcwd(),f"GuildFiles",f"{guild_name_filtered}.json")
        shutil.copyfile(src,dst)
        GuildMemberFile = open(f"GuildFiles/{guild_name_filtered}.json","r")
        GuildMemberJSON = json.load(GuildMemberFile)
        GuildMemberFile.close()
        for member in guild.members:
            try:
                GuildMemberJSON[member.display_name[-2:]] = GuildMemberJSON[member.display_name[-2:]] + 1
            except KeyError:
                pass
                print(f"Key not found for {member.display_name}. In {guild.name}")
        GuildMemberFile = open(f"GuildFiles/{guild_name_filtered}.json","w")
        json.dump(GuildMemberJSON,GuildMemberFile,indent=4)
        GuildMemberFile.close()

@NicknameCollection.before_loop
async def wait_for_NicknameCollection():
    await client.wait_until_ready()

NicknameCollection.start()
client.run(BOT_ID)
