import asyncio
import io
from typing import Optional
import disnake
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound
from .models import VerificationApp, VerificationGuild, VerificationStatus


async def has_verification_open(user_id: int, guild_id: int, session: AsyncSession) -> bool:
    result = await session.execute(select(VerificationApp).filter_by(user_id=user_id, guild_id=guild_id))
    checker = result.scalars().first()
    return checker is not None


async def get_guild_data(guild_id: int, session: AsyncSession) -> VerificationGuild:
    result = await session.execute(select(VerificationGuild).filter_by(guild_id=guild_id))
    return result.scalars().first()


async def get_verification(user_id: int, session: AsyncSession) -> VerificationApp:
    result = await session.execute(select(VerificationApp).filter_by(user_id=user_id))
    return result.scalars().first()


async def create_guilds_data(guilds: list[disnake.Guild], session: AsyncSession) -> int:
    new_guilds = 0
    for guild in guilds:
        try:
            result = await session.execute(select(VerificationGuild).filter_by(guild_id=guild.id))
            existing_guild = result.scalars().first()
            if not existing_guild:
                new_guild = VerificationGuild(guild_id=guild.id)
                session.add(new_guild)
                await session.commit()
                new_guilds += 1
        except NoResultFound:
            new_guild = VerificationGuild(guild_id=guild.id)
            session.add(new_guild)
            await session.commit()
            new_guilds += 1
    return new_guilds


async def ask_reason(interaction: disnake.Interaction, button: disnake.Button):
    await interaction.response.send_modal(
        title="Provide Reason",
        custom_id=f"reason_modal:{button.custom_id}",
        components=[
            disnake.ui.TextInput(
                label="Reason",
                placeholder="Brief Description.",
                custom_id="reason",
                style=disnake.TextInputStyle.long,
                max_length=1000,
            ),
        ])
    # Waits until the user submits the modal
    try:
        modal_inter: disnake.ModalInteraction = await interaction.bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == f"reason_modal:{button.custom_id}" and i.author.id == interaction.author.id,
            timeout=300,
        )
        # If Reason is cancel, Cancel
        if modal_inter.text_values['reason'] == "cancel":
            await modal_inter.response.send_message("Cancelled Request", ephemeral=True)
            return
        await modal_inter.response.send_message("Handled Application", ephemeral=True)
        return modal_inter
    except asyncio.TimeoutError:
        return


async def text_reason(message: disnake.Message, reason: str):
    if not reason:
        return await message.channel.send("Please provide a reason along with the command please.")
    return reason


async def get_verif_delete(inter: disnake.MessageInteraction, session: AsyncSession) -> VerificationApp | bool:
    if not inter.guild:
        return None
    try:
        result = await session.execute(select(VerificationApp).filter_by(pending_verification_id=inter.message.id, guild_id=inter.guild.id))
        data = result.scalars().first()
        if not data:
            raise NoResultFound
    except NoResultFound:
        guild_data_result = await session.execute(select(VerificationGuild).filter_by(guild_id=inter.guild.id))
        guild_data = guild_data_result.scalars().first()
        log = inter.guild.get_channel(guild_data.verification_logging_channel)  # type: ignore
        if log:
            await log.send(f"User {inter.author.mention} deleted a verification application that was not found in the database.", embed=inter.message.embeds[0])  # type: ignore
        await inter.response.send_message("Cannot find verification application attached to this message.", ephemeral=True)
        await inter.message.delete()
        return False
    return data


    
async def get_guild_data(bot, guild_id: int) -> VerificationGuild | None:
    async with bot.db_session() as session:
        select_query = select(VerificationGuild).where(VerificationGuild.guild_id == guild_id)
        result = await session.execute(select_query)
        return result.scalar_one_or_none()
    
async def get_application_qid(bot, channel_id: int, guild_id: int) -> VerificationApp | None:
    async with bot.db_session() as session:
        select_query = select(VerificationApp).where(VerificationApp.questioning_channel_id == channel_id, VerificationApp.questioning == True, VerificationApp.guild_id == guild_id, VerificationApp.active == True)
        result = await session.execute(select_query)
        return result.scalar_one_or_none()
    
async def get_application_uid(bot, user_id: int, guild_id: int) -> VerificationApp | None:
    async with bot.db_session() as session:
        select_query = select(VerificationApp).where(VerificationApp.user_id == user_id, VerificationApp.active == True, VerificationApp.guild_id == guild_id)
        result = await session.execute(select_query)
        return result.scalar_one_or_none()
    
async def get_application_uid_nogid(bot, user_id: int) -> VerificationApp | None:
    async with bot.db_session() as session:
        select_query = select(VerificationApp).where(VerificationApp.user_id == user_id, VerificationApp.active == True)
        result = await session.execute(select_query)
        return result.scalar_one_or_none()

async def get_application_uid_questioning(bot, user_id: int, guild_id: int) -> VerificationApp | None:
    async with bot.db_session() as session:
        select_query = select(VerificationApp).where(VerificationApp.user_id == user_id, VerificationApp.questioning == True, VerificationApp.active == True, VerificationApp.guild_id == guild_id)
        result = await session.execute(select_query)
        return result.scalar_one_or_none()
    
async def get_application_msg(bot, msg: int, guild_id: int) -> VerificationApp | None:
    async with bot.db_session() as session:
        select_query = select(VerificationApp).where(VerificationApp.pending_verification_id == msg, VerificationApp.guild_id == guild_id, VerificationApp.active == True)
        result = await session.execute(select_query)
        return result.scalar_one_or_none()
    
async def close_verification(
    responder: disnake.Member,
    bot: disnake.Client,
    guild: disnake.Guild,
    status: VerificationStatus,
    message: Optional[disnake.Message] = None,
    channel_id: Optional[int] = None,
    reason: str = "No Reason Provided.",
    notified: bool = False
):
    bot.logger.info("Closing Application...")
    verification = None
    if message:
        bot.logger.info("Message found")
        verification = await get_application_msg(bot, message.id, guild.id)
    elif channel_id:
        bot.logger.info("Channel found instead")
        verification = await get_application_qid(bot, channel_id, guild.id)
    else:
        bot.logger.info("No Message/Channel ID Provided")
        return
    
    if not verification:
        bot.logger.error("Verification not found")
        return
    
    # Get Guild Data
    bot.logger.info("Getting Guild Data")
    guild_data = await get_guild_data(bot, guild.id)
    if not guild_data or guild_data.pending_verifications_channel_id is None:
        bot.logger.info("There is no verification channel ID...")
        return

    pending_channel = guild.get_channel(guild_data.pending_verifications_channel_id)
    if not isinstance(pending_channel, disnake.TextChannel):
        bot.logger.info("Pending Verification Channel is not set up. Skipping...")
        return

    if not message:
        message = await pending_channel.fetch_message(verification.pending_verification_id)

    # Modify the message embed
    embed = message.embeds[0]
    embed.description = "This verification has been closed by a staff member."
    embed.add_field(name="Status", value=f"**{status.name}**")
    embed.add_field(name="Responsible:", value=f"{responder.mention}")

    # Set embed colors and additional information based on status
    embed.color = {
        VerificationStatus.ACCEPTED: 0x00ff00,
        VerificationStatus.DENIED: 0xff0000,
        VerificationStatus.BANNED: 0xffff00,
        VerificationStatus.KICKED: 0x00ffff,
        VerificationStatus.LEFT: 0x00ffff
    }.get(status, 0x000000)

    if status in [VerificationStatus.DENIED, VerificationStatus.BANNED, VerificationStatus.KICKED]:
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Notified:", value="User was never notified (Blocked DMs)" if not notified else "User is notified.", inline=False)

    # Logging
    if guild_data.verification_logging_channel is None:
        bot.logger.info("Logging Channel Not set up")
        return

    logging_channel = guild.get_channel(guild_data.verification_logging_channel)
    if not isinstance(logging_channel, disnake.TextChannel):
        bot.logger.info("Logging channel is not a text channel")
        return

    # Delete Verification Message
    await message.delete()

    # Handle questioning process, if applicable
    if verification.questioning:
        questioning_channel = guild.get_channel(verification.questioning_channel_id)
        if isinstance(questioning_channel, disnake.TextChannel):
            transcript = await create_transcript(questioning_channel)
            await questioning_channel.delete()
            try:
                await logging_channel.send(file=disnake.File(transcript, "transcript.txt"), embed=embed)
            except:
                bot.logger.info("Failed to send transcript")
                await logging_channel.send(embed=embed)
            finally:
                transcript.close()
        else:
            bot.logger.info("Cannot find questioning channel")
            await logging_channel.send(embed=embed)
    else:
        await logging_channel.send(embed=embed)
        
        

    # Mark the application as close
    async with bot.db_session() as session:
        # Update the application
        app = select(VerificationApp).where(VerificationApp.user_id == responder.id, VerificationApp.guild_id == guild.id)
        await session.execute(update(VerificationApp).where(VerificationApp.user_id == responder.id, VerificationApp.guild_id == guild.id).values(active=False, status=status.value))
        await session.commit()
        

async def create_transcript(channel: disnake.TextChannel) -> io.BytesIO:
    transcript = io.BytesIO()
    transcript_wrapper = io.TextIOWrapper(transcript, encoding="utf-8", write_through=True)
    messages = await channel.history(limit=250).flatten()
    for msg in reversed(messages):
        transcript_wrapper.write(f"{msg.author}: {msg.content} (Sent {msg.created_at})\n")
    transcript_wrapper.seek(0)
    return transcript

async def check_user_left(message: disnake.Message, bot, user_id: int) -> bool:
    guild = message.guild
    if guild is None:
        raise ValueError("Message is not from a guild!")

    user = guild.get_member(user_id)
    if user is None:
        verification = await get_application_uid(bot, user_id, guild.id)
        if verification:
            async with bot.db_session() as session:
                session.execute(update(VerificationApp).where(VerificationApp.user_id == user_id, VerificationApp.guild_id == guild.id).values(active=False, status=VerificationStatus.LEFT.value))
                await session.commit()
        return True
    return False