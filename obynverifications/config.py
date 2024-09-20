from typing import List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import VerificationGuild
from sqlalchemy.orm.attributes import flag_modified

# Typing definitions
Configuration = Dict[str, Union[str, Dict[str, Union[str, Dict[str, str]]]]]
Category = Dict[str, Dict[str, Union[str, Dict[str, str]]]]


def ConfigData() -> Dict[str, Union[str, Dict[str, Union[str, Dict[str, Category]]]]]:
    return {
        "CONFIG_DATA": {
            "TITLE": "Verification Settings",
            "DESCRIPTION": "Settings for the Verification Module",
            "CONFIGURATION": {
                "CATEGORIES": {
                    "VERIFICATION": {
                        "TITLE": "Verification",
                        "verification_logging_channel": {
                            "TYPE": "CHANNEL",
                            "DESCRIPTION": "Channel to log verification events"
                        },
                        "verification_questions": {
                            "TYPE": "TEXT_LIST",
                            "DESCRIPTION": "List of verification questions"
                        },
                        "unverified_role_ids": {
                            "TYPE": "ROLE_LIST",
                            "DESCRIPTION": "Roles assigned to unverified users"
                        },
                        "verified_role_ids": {
                            "TYPE": "ROLE_LIST",
                            "DESCRIPTION": "Roles assigned to verified users"
                        },
                        "verification_instructions": {
                            "TYPE": "MESSAGE",
                            "DESCRIPTION": "Instructions for the verification process"
                        },
                        "pending_verifications_channel_id": {
                            "TYPE": "CHANNEL",
                            "DESCRIPTION": "Channel for pending verifications"
                        },
                        "auto_verify_on_rejoin": {
                            "TYPE": "BOOLEAN",
                            "DESCRIPTION": "Automatically verify users who rejoin"
                        }
                    },
                    "WELCOME": {
                        "TITLE": "Welcome",
                        "welcome_role_id": {
                            "TYPE": "ROLE",
                            "DESCRIPTION": "Role assigned to new members"
                        },
                        "welcome_channel_id": {
                            "TYPE": "CHANNEL",
                            "DESCRIPTION": "Channel to send welcome messages"
                        },
                        "welcome_message": {
                            "TYPE": "MESSAGE",
                            "DESCRIPTION": "Welcome message for new members"
                        },
                        "joining_message": {
                            "TYPE": "MESSAGE",
                            "DESCRIPTION": "Message sent when a user joins"
                        },
                        "welcome_message_banner_url": {
                            "TYPE": "MESSAGE",
                            "DESCRIPTION": "URL for the welcome message banner"
                        }
                    },
                    "STAFF": {
                        "TITLE": "Staff",
                        "staff_role_id": {
                            "TYPE": "ROLE",
                            "DESCRIPTION": "Role assigned to staff members"
                        }
                    }
                }
            }
        }
    }

# Retrieve the list of configuration categories
def get_config_categories() -> List[str]:
    categories_list = []
    config_data: Configuration = ConfigData()
    categories: Dict[str] = config_data['CONFIG_DATA']['CONFIGURATION']['CATEGORIES']  # type: ignore
    for category_name, category_properties in categories.items():
        categories_list.append(category_name)
    return categories_list

# Retrieve the settings for a specific category
def get_config_category(category_name: str) -> List[str]:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    if category_name in config:
        category_config = config[category_name]
        return [key for key in category_config.keys() if key != "TITLE"]
    else:
        return []

# Retrieve settings with descriptions
def get_config_category_with_description(category_name: str) -> Dict[str, str]:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    if category_name in config:
        category_config = config[category_name]
        return {key: category_config[key]["DESCRIPTION"] for key in category_config.keys() if key != "TITLE"}
    else:
        return {}

# Retrieve the type of a specific setting in a category
def get_config_category_setting_type(category_name: str, setting: str) -> str:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    return config[category_name][setting]["TYPE"]

# Retrieve the entire configuration data
def get_config_data() -> Dict[str, Union[str, Dict[str, Union[str, Dict[str, Category]]]]]:
    return ConfigData()

# Retrieve possible options for a setting if applicable
def get_config_category_setting_options(category_name: str, setting: str) -> Union[str, List[Any]]:
    config = ConfigData()["CONFIG_DATA"]["CONFIGURATION"]["CATEGORIES"]
    if category_name in config and setting in config[category_name]:
        setting_config = config[category_name][setting]
        if "OPTIONS" in setting_config:
            return setting_config["OPTIONS"]
    return []


async def get_guild_configurations(guild_id: str, session: AsyncSession) -> Dict[str, Any]:
    async with session.begin():
        stmt = select(VerificationGuild).filter_by(guild_id=guild_id)
        result = await session.execute(stmt)
        guild = result.scalar()
        if not guild:
            new_guild = VerificationGuild(guild_id=guild_id)
            session.add(new_guild)
            await session.commit()
            return new_guild
            
        return guild

async def set_guild_configuration(guild_id: str, session: AsyncSession, data: Dict[str, Any]) -> None:
    try:
        async with session.begin():
            stmt = select(VerificationGuild).filter_by(guild_id=guild_id)
            result = await session.execute(stmt)
            guild = result.scalar()

            if guild:
                for key, value in data.items():
                    if isinstance(value, list):
                        setattr(guild, key, value)
                        flag_modified(guild, key)
                    else:
                        setattr(guild, key, value)
            else:
                new_guild = VerificationGuild(guild_id=guild_id, **data)
                session.add(new_guild)

            await session.commit()
    except Exception as e:
        raise e