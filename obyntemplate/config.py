from typing import List, Dict, Any, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import GuildModel  # Assuming this is the SQLAlchemy model

Configuration = Dict[str, Union[str, Dict[str, Union[str, Dict[str, str]]]]]
Category = Dict[str, Dict[str, Union[str, Dict[str, str]]]]


def ConfigData() -> Dict[str, Union[str, Dict[str, Union[str, Dict[str, Category]]]]]:
    return {
        "CONFIG_DATA": {
            "TITLE": "Template Settings",
            "DESCRIPTION": "Settings for the Template Module",
            "CONFIGURATION": {
                "CATEGORIES": {
                    "TEMPLATE": {
                        "TITLE": "Template",
                        "guild_id": {
                            "TYPE": "CHANNEL",
                            "DESCRIPTION": "Channel to send daily stats"
                        },
                        "prefix": {
                            "TYPE": "STRING",
                            "DESCRIPTION": "Prefix for the bot"
                        },
                        "welcome_channel": {
                            "TYPE": "CHANNEL",
                            "DESCRIPTION": "Channel to send welcome messages"
                        },
                        "welcome_message": {
                            "TYPE": "STRING",
                            "DESCRIPTION": "Welcome message"
                        }
                    }
                }
            }
        }
    }


def get_config_categories() -> List[str]:
    categories_list = []
    config_data: Configuration = ConfigData()
    categories: Dict[str] = config_data['CONFIG_DATA']['CONFIGURATION']['CATEGORIES']  # type: ignore
    for category_name, category_properties in categories.items():
        categories_list.append(category_name)
    return categories_list


def get_config_category(category_name: str) -> List[str]:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    if category_name in config:
        category_config = config[category_name]
        return [key for key in category_config.keys() if key != "TITLE"]
    else:
        return []


def get_config_category_with_description(category_name: str) -> Dict[str, str]:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    if category_name in config:
        category_config = config[category_name]
        return {key: category_config[key]["DESCRIPTION"] for key in category_config.keys() if key != "TITLE"}
    else:
        return {}


def get_config_category_setting_type(category_name: str, setting: str) -> str:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    return config[category_name][setting]["TYPE"]


def get_config_data() -> Dict[str, Union[str, Dict[str, Union[str, Dict[str, Category]]]]]:
    return ConfigData()


def get_config_category_setting_options(category_name: str, setting: str) -> Union[str, List[Any]]:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    if category_name in config and setting in config[category_name]:
        setting_config = config[category_name][setting]
        if "OPTIONS" in setting_config:
            return setting_config["OPTIONS"]
    return []


# Updated to use SQLAlchemy with AsyncSession
async def get_guild_configurations(guild_id: str, session: AsyncSession) -> Dict[str, Any]:
    """
    Fetches the configuration for a specific guild from the database using SQLAlchemy.

    :param guild_id: The guild ID to fetch configurations for.
    :param session: The AsyncSession instance to use for database operations.
    :return: A dictionary of configuration settings for the guild.
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
                # Add any other settings you might want to fetch
            }
        else:
            # Return default configuration if no guild is found in the database
            return {
                "guild_id": guild_id,
                "prefix": "!",  # Default prefix
                "welcome_channel": None,
                "welcome_message": "Welcome to the server!",
                # Add any default settings
            }


async def set_guild_configuration(guild_id: str, session: AsyncSession, data: Dict[str, Any]) -> None:
    """
    Update or insert guild configuration in the database.

    :param guild_id: The guild ID to set configurations for.
    :param session: The AsyncSession instance to use for database operations.
    :param data: A dictionary of configuration data to update.
    """
    async with session.begin():
        stmt = select(GuildModel).filter_by(guild_id=guild_id)
        result = await session.execute(stmt)
        guild = result.scalar()

        if guild:
            # Update existing guild config
            for key, value in data.items():
                setattr(guild, key, value)
        else:
            # Create new guild config
            new_guild = GuildModel(guild_id=guild_id, **data)
            session.add(new_guild)

        await session.commit()