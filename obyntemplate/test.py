from typing import List, Dict, Any
import disnake
from disnake.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import GuildModel

class ConfigEvent(disnake.Event):
    def __init__(self, guild_id: str, config_key: str, old_value: Any, new_value: Any):
        self.guild_id = guild_id
        self.config_key = config_key
        self.old_value = old_value
        self.new_value = new_value
        super().__init__()


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_configurations(self, guild_id: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Fetches the configuration for a specific guild from the database using SQLAlchemy.
        """
        async with session.begin():
            stmt = select(GuildModel).filter_by(guild_id=guild_id)
            result = await session.execute(stmt)
            guild = result.scalar()

            if guild:
                return {
                    "guild_id": guild.guild_id,
                    "prefix": guild.prefix,
                    "welcome_channel": guild.welcome_channel,
                    "welcome_message": guild.welcome_message,
                }
            else:
                # Default configuration
                return {
                    "guild_id": guild_id,
                    "prefix": "!",
                    "welcome_channel": None,
                    "welcome_message": "Welcome to the server!",
                }

    async def set_guild_configuration(self, guild_id: str, session: AsyncSession, data: Dict[str, Any]) -> None:
        """
        Update or insert guild configuration in the database.
        """
        async with session.begin():
            stmt = select(GuildModel).filter_by(guild_id=guild_id)
            result = await session.execute(stmt)
            guild = result.scalar()

            if guild:
                # Update existing guild config
                for key, value in data.items():
                    old_value = getattr(guild, key, None)
                    setattr(guild, key, value)

                    # Trigger an event if configuration changes
                    if old_value != value:
                        await self.bot.dispatch_event(
                            ConfigEvent(guild_id=guild_id, config_key=key, old_value=old_value, new_value=value)
                        )

            else:
                # Create new guild config
                new_guild = GuildModel(guild_id=guild_id, **data)
                session.add(new_guild)

            await session.commit()

    @commands.slash_command()
    @commands.guild_only()
    async def get_config(self, inter: disnake.ApplicationCommandInteraction):
        """Fetch the current configuration for the guild."""
        async with self.bot.db_session() as session:
            config = await self.get_guild_configurations(guild_id=inter.guild.id, session=session)
            await inter.response.send_message(f"Current config: {config}")

    @commands.slash_command()
    @commands.guild_only()
    async def set_prefix(self, inter: disnake.ApplicationCommandInteraction, prefix: str):
        """Set a new prefix for the guild."""
        async with self.bot.db_session() as session:
            await self.set_guild_configuration(guild_id=inter.guild.id, session=session, data={"prefix": prefix})
            await inter.response.send_message(f"Prefix set to: {prefix}")

    @commands.slash_command()
    @commands.guild_only()
    async def set_welcome_message(self, inter: disnake.ApplicationCommandInteraction, message: str):
        """Set a new welcome message for the guild."""
        async with self.bot.db_session() as session:
            await self.set_guild_configuration(guild_id=inter.guild.id, session=session, data={"welcome_message": message})
            await inter.response.send_message(f"Welcome message set to: {message}")

    @commands.slash_command()
    @commands.guild_only()
    async def set_welcome_channel(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        """Set the welcome channel for the guild."""
        async with self.bot.db_session() as session:
            await self.set_guild_configuration(guild_id=inter.guild.id, session=session, data={"welcome_channel": channel.id})
            await inter.response.send_message(f"Welcome channel set to: {channel.mention}")

    @commands.Cog.listener()
    async def on_config_event(self, event: ConfigEvent):
        """Listener for configuration changes."""
        # Handle configuration changes
        self.bot.logger.info(
            f"Configuration changed in guild {event.guild_id}: {event.config_key} changed from {event.old_value} to {event.new_value}"
        )

    