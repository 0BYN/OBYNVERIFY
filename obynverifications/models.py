from enum import Enum
import io
from typing import Optional, Literal
from uuid import uuid4

import disnake
from sqlalchemy import BigInteger, Boolean, Column, String, ARRAY, Text, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from obynutils.setup_database import Base


class VerificationStatus(Enum):
    ACCEPTED = 'accepted'
    DENIED = 'denied'
    BANNED = 'banned'
    KICKED = 'kicked'
    LEFT = 'left'
    PENDING = 'pending'


class VerificationGuild(Base):
    __tablename__ = 'verification_guild'

    guild_id = Column(BigInteger, primary_key=True)
    # Verification Configuration
    verification_logging_channel = Column(BigInteger, default=None)
    verification_questions = Column(ARRAY(Text), default=[])
    unverified_role_ids = Column(ARRAY(BigInteger), default=[])
    verified_role_ids = Column(ARRAY(BigInteger), default=[])
    verification_instructions = Column(Text, default=None)
    pending_verifications_channel_id = Column(BigInteger, default=None)
    auto_verify_on_rejoin = Column(Boolean, default=False)

    # Welcome Configuration
    welcome_role_id = Column(BigInteger, default=None)
    welcome_channel_id = Column(BigInteger, default=None)
    welcome_message = Column(Text, default=None)
    joining_message = Column(Text, default=None)
    welcome_message_banner_url = Column(Text, default=None)

    staff_role_id = Column(BigInteger, default=None)
    
    @classmethod
    async def fetch(cls, guild_id: int, session: AsyncSession):
        query = select(cls).filter_by(guild_id=guild_id)
        result = await session.execute(query)
        return result.scalars().first()


class VerificationApp(Base):
    __tablename__ = 'verification_applications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # Way to identify the verification application
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    pending_verification_id = Column(BigInteger, nullable=False)
    # Verification Status
    questioning = Column(Boolean, default=False)
    questioning_channel_id = Column(BigInteger, nullable=True)
    active = Column(Boolean, default=True)
    status = Column(String, default=VerificationStatus.PENDING.value)
    
