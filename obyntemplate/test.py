from typing import List, Dict, Any
import disnake
from disnake.ext import commands
from obyntemplate.config import get_guild_configurations, set_guild_configuration

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.guild_only()
    async def get_config(self, inter: disnake.ApplicationCommandInteraction):
        """Fetch the current configuration for the guild."""
        async with self.bot.db_session() as session:
            config = await get_guild_configurations(guild_id=inter.guild.id, session=session)
            await inter.response.send_message(f"Current config: {config}")

    @commands.slash_command()
    @commands.guild_only()
    async def set_prefix(self, inter: disnake.ApplicationCommandInteraction, prefix: str):
        """Set a new prefix for the guild."""
        async with self.bot.db_session() as session:
            await set_guild_configuration(guild_id=inter.guild.id, session=session, data={"prefix": prefix})
            await inter.response.send_message(f"Prefix set to: {prefix}")

    @commands.slash_command()
    @commands.guild_only()
    async def set_welcome_message(self, inter: disnake.ApplicationCommandInteraction, message: str):
        """Set a new welcome message for the guild."""
        async with self.bot.db_session() as session:
            await set_guild_configuration(guild_id=inter.guild.id, session=session, data={"welcome_message": message})
            await inter.response.send_message(f"Welcome message set to: {message}")

    @commands.slash_command()
    @commands.guild_only()
    async def set_welcome_channel(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        """Set the welcome channel for the guild."""
        async with self.bot.db_session() as session:
            await set_guild_configuration(guild_id=inter.guild.id, session=session, data={"welcome_channel": channel.id})
            await inter.response.send_message(f"Welcome channel set to: {channel.mention}")