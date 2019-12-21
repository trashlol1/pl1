import discord
import asyncio
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core import Config, checks
import random
#Coded by PaPí#0001

class Rainbow_Six_Siege(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.data = Config.get_conf(self, identifier=62078023501206325104, force_registration=True)
        default_guild = {
            "maps": [],
            "lobbies": {}
        }
        default_member = {
            "registered": False
        }
        self.data.register_guild(**default_guild)
        self.data.register_member(**default_member)

    @commands.group()
    async def rssset(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @rssset.command(name="add")
    async def addmap(self, ctx, *, name: str):
        """Add a map to the list."""
        maps_list = await self.data.guild(ctx.guild).maps()
        if name.lower() in maps_list:
            await ctx.send("That map already exists in the list.")
        elif name.lower() not in maps_list:
            maps_list.append(name.lower())
            await self.data.guild(ctx.guild).maps.set(maps_list)
            await ctx.send("Successfully added the map to the list.")

    @rssset.command(name="remove")
    async def removemap(self, ctx, *, name: str):
        """Remove a map from the list."""
        maps_list = await self.data.guild(ctx.guild).maps()
        if name.lower() in maps_list:
            maps_list.remove(name.lower())
            await self.data.guild(ctx.guild).maps.set(maps_list)
            await ctx.send(f"**{name}** was removed from the list.")
        elif name.lower() not in maps_list:
            await ctx.send(f"**{name}** is not in the list.")

    @commands.command()
    async def register(self, ctx):
        """Register yourself."""
        if await self.data.member(ctx.author).registered() == True:
            await ctx.send("You are already registered!")
        elif await self.data.member(ctx.author).registered() == False:
            await self.data.member(ctx.author).registered.set(True)
            await ctx.send(f"Thank you for registering {ctx.author.mention} : [0] - {ctx.author.name}")

    @commands.command()
    async def createlobby(self, ctx):
        """Create a lobby"""
        lobbies = await self.data.guild(ctx.guild).lobbies()
        if str(ctx.channel.id) in lobbies:
            await ctx.send("There is already a lobby created in this channel.")
            return

        e=discord.Embed(description="1️⃣ General Team Name\n2️⃣ Custom team name")
        e.set_footer(text="React below with a specific emoji to set the team names.")
        msg = await ctx.send(embed=e)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        def reactioncheck(reaction, user):
            if user != self.bot.user:
                if user == ctx.author:
                    if reaction.message.channel == ctx.channel:
                        if reaction.message.id == msg.id:
                            if reaction.emoji == "1️⃣" or reaction.emoji == "2️⃣":
                                return True
        try:
            response, author = await self.bot.wait_for("reaction_add", check=reactioncheck, timeout=60)
        except asyncio.TimeoutError:
            await self._remove_reactions(msg)
            return
        else:
            if response.emoji == "1️⃣":
                await self._remove_reactions(msg)
                team_name_type = "general"
            elif response.emoji == "2️⃣":
                await self._remove_reactions(msg)
                team_name_type = "custom_name"

        msg = await ctx.send("How many people would it take for a match to be begin? (Even number)")
        def confirmation_msg(m):
            return m.channel == ctx.channel and ctx.author == m.author
        try:
            answer = await self.bot.wait_for("message", timeout=60, check=confirmation_msg)
        except asyncio.TimeoutError:
            await ctx.send('Timed out, try again!')
            return

        if answer:
            try:
                if isinstance(int(answer.content), int):
                    minimum_members = int(answer.content)
                    if minimum_members%2 == 0:
                        minimum_members = int(answer.content)
                    else:
                        await ctx.send("The number you provided wasn't even.")
                        return
                else:
                    await ctx.send("Invalid amount of people provided.")
                    return
            except:
                await ctx.send("Invalid amount of people provided.")
                return
        else:
            await ctx.send("Invalid amount of people provided.")
            return

        channel_id = ctx.channel.id

        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "team_one", value={"team_name": None, "players": [], "captains": None, "max_players": minimum_members/2})
        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "team_two", value={"team_name": None, "players": [], "captains": None, "max_players": minimum_members/2})
        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "players", value={"list_of_players": [], "type": team_name_type})
        await ctx.send(f"Lobby created with {minimum_members} members limit.")

    @commands.command()
    async def join(self, ctx):
        channel_id = str(ctx.channel.id)
        if await self.data.member(ctx.author).registered() == False:
            await ctx.send(f"You should register your self first by using ``{ctx.prefix}register` command.")
        elif await self.data.member(ctx.author).registered() == True:
            if channel_id not in await self.data.guild(ctx.guild).lobbies():
                await ctx.send("There is no queue in this channel!")
                return
            elif channel_id in await self.data.guild(ctx.guild).lobbies():
                teamOne = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_one", "max_players")
                teamTwo = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_two", "max_players")
                max_players = int(teamOne + teamTwo)
                current_players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "players", "list_of_players")
                if len(current_players) < max_players:
                    current_players.append(ctx.author.id)
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "players", "list_of_players", value=current_players)
                    await ctx.send("You were added to the queue!")

                if len(current_players) == max_players:
                    team_one_leader = random.choice(current_players)
                    current_players.remove(team_one_leader)
                    team_two_leader = random.choice(current_players)
                    current_players.remove(team_two_leader)
                    channel_id  = ctx.channel.id
                    await ctx.send(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"players", "type"))
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"players", "list_of_players", value=current_players)
                    if await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"players", "type") == "general":
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "team_name", value="team_1")
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "captains", value=team_one_leader)
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "team_name", value="team_2")
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "captains", value=team_two_leader)
                    if await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"players", "type") == "custom_name":
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "team_name", value=str(ctx.guild.get_member(int(team_one_leader))))
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "captains", value=team_one_leader)
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "team_name", value=str(ctx.guild.get_member(int(team_two_leader))))
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "captains", value=team_two_leader)
                    await ctx.send(f"Team One leader {ctx.guild.get_member(int(team_one_leader))}\n\n Team Two Leader {ctx.guild.get_member(int(team_two_leader))}\n\n Leaders can now choose their team mates by using `{ctx.prefix}pick` command.")
                    return

    @commands.command()
    async def pick(self, ctx, user: discord.Member):
        """Pick a member for your team."""
        channel_id = str(ctx.channel.id)
        if channel_id not in await self.data.guild(ctx.guild).lobbies():
            await ctx.send("There is no queue in this channel!")
            return
        elif channel_id in await self.data.guild(ctx.guild).lobbies():
            captain_one = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "captains")
            captain_two = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "captains")
            if captain_one and captain_one == ctx.author.id:
                max_players = int(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "max_players"))
                players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "players")
                if len(players) == max_players - 1:
                    await ctx.send(f"Your team can't have any more players, max limit reached. - **{len(players)}/{max_players-1}**")
                else:
                    players.append(user.id)
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "players", value=players)
                    await ctx.send(f"Added {user.name} to the team.")
            elif captain_two and captain_two == ctx.author.id:
                max_players = int(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "max_players"))
                players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "players")
                if len(players) == max_players - 1:
                    await ctx.send(f"Your team can't have any more players, max limit reached. - **{len(players)}/{max_players-1}**")
                else:
                    players.append(user.id)
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "players", value=players)
                    await ctx.send(f"Added {user.name} to the team.")

        if (await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "max_players") + await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "max_players")) - 2 == (len(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "players")) + len(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "players"))):
            maps = await self.data.guild(ctx.guild).maps()
            if maps:
                map = random.choice(maps)
            else:
                map = "No maps are been set!"
            members_team_one = []
            members_team_two = []
            for member in await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "players"):
                user = ctx.guild.get_member(int(member))
                if user:
                    members_team_one.append(str(user.name))

            for member in await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "players"):
                user = ctx.guild.get_member(int(member))
                if user:
                    members_team_two.append(str(user.name))
            text_msg = f'Map: {map}\nTeam1: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "team_name")}\nMembers: {", ".join(members_team_one)}\n\nTeam2: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "team_name")}\nMembers: {", ".join(members_team_two)}\n\n\n"React with ▶ for a different map else react with ✅'
            msg = await ctx.send(text_msg)
            msg_id = msg.id
            await msg.add_reaction("▶")
            await msg.add_reaction("✅")
            def reactioncheck(reaction, user):
                if user != self.bot.user:
                    if user == ctx.author:
                        if reaction.message.channel == ctx.channel:
                            if reaction.message.id == msg_id:
                                if reaction.emoji == "▶" or reaction.emoji == "✅":
                                    return True
            x = True
            while x:
                try:
                    reaction, author = await self.bot.wait_for("reaction_add", timeout=120, check=reactioncheck)
                    if reaction.emoji == "▶":
                        map = random.choice(maps)
                        text_msg = f'Map: {map}\nTeam1: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "team_name")}\nMembers: {", ".join(members_team_one)}\n\nTeam2: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "team_name")}\nMembers: {", ".join(members_team_two)}\n\n\n"React with ▶ for a different map else react with ✅'
                        msg = await ctx.channel.fetch_message(msg_id)
                        await msg.edit(content=text_msg)
                    elif reaction.emoji == "✅":
                        await self.data.guild(ctx.guild).lobbies.clear_raw(str(ctx.channel.id))
                        await ctx.send("Teams successfully created, and the data was deleted!")
                        x = False
                except asyncio.TimeoutError:
                    try:
                        await msg.remove_reaction("▶")
                        await msg.remove_reaction("✅")
                    except:
                        pass
                    x = False

    async def _remove_reactions(self, msg):
        try:
            await msg.clear_reactions()
        except:
            return
