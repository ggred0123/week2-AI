# models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from database import Base

# Enum 클래스들
class Sex(str, PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class MadCampStatus(str, PyEnum):
    InCamp = "InCamp"
    OutCamp = "OutCamp"

class PreferredAlcohol(str, PyEnum):
    Beer = "Beer"
    Wine = "Wine"
    Cocktail = "Cocktail"
    Mixed = "Mixed"
    Soju = "Soju"
    SoftDrink = "SoftDrink"
    None_ = "None"

class RegistrationStatus(str, PyEnum):
    TEMPORARY = "TEMPORARY"
    COMPLETED = "COMPLETED"

# 모델 클래스들
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("university.id"))
    name = Column(String)
    major = Column(String)
    alcohol_level = Column(Integer, default=0)
    mad_camp_status = Column(Enum(MadCampStatus))
    email = Column(String, unique=True)
    sex = Column(Enum(Sex), default=Sex.MALE)
    mbti_id = Column(Integer, ForeignKey("mbti.id"))
    class_id = Column(Integer)
    image_url = Column(String, nullable=True)
    programming_level = Column(Integer, default=0)
    programming_field = Column(String)
    programming_language = Column(String)
    preferred_alcohol_id = Column(Integer, ForeignKey("alcohol.id"), default=1)
    leadership_level = Column(Integer, default=0)
    refresh_token = Column(String, nullable=True)
    birthday = Column(DateTime)
    registration_status = Column(Enum(RegistrationStatus), default=RegistrationStatus.TEMPORARY)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    meeting = relationship("Meeting", back_populates="host")
    meeting_join_user = relationship("MeetingJoinUser", back_populates="user")
    reply = relationship("Reply", back_populates="user")
    community_content = relationship("CommunityContent", back_populates="writed_user")
    caller_user_matching = relationship("UserMatching", foreign_keys="[UserMatching.caller_user_id]", back_populates="caller_user")
    callee_user_matching = relationship("UserMatching", foreign_keys="[UserMatching.callee_user_id]", back_populates="callee_user")
    preferred_alcohol = relationship("Alcohol", back_populates="user")
    university = relationship("University", back_populates="user")
    mbti = relationship("Mbti", back_populates="user")

class UserCodingInfo(Base):
    __tablename__ = "user_coding"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    coding_language_id = Column(Integer, ForeignKey("coding_language.id"))
    coding_field_id = Column(Integer, ForeignKey("coding_field.id"))
    coding_level = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    coding_language = relationship("CodingLanguage", back_populates="user")
    user = relationship("User")
    coding_field = relationship("CodingField", back_populates="user")

class CodingField(Base):
    __tablename__ = "coding_field"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    user = relationship("UserCodingInfo", back_populates="coding_field")

class CodingLanguage(Base):
    __tablename__ = "coding_language"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    user = relationship("UserCodingInfo", back_populates="coding_language")

class Mbti(Base):
    __tablename__ = "mbti"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="mbti")

class Alcohol(Base):
    __tablename__ = "alcohol"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="preferred_alcohol")

class University(Base):
    __tablename__ = "university"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="university")

class UserMatching(Base):
    __tablename__ = "user_matching"

    id = Column(Integer, primary_key=True, index=True)
    caller_user_id = Column(Integer, ForeignKey("user.id"))
    callee_user_id = Column(Integer, ForeignKey("user.id"))
    comment = Column(String)
    matching_category_id = Column(Integer, ForeignKey("matching_category.id"))
    created_at = Column(DateTime, default=func.now())

    caller_user = relationship("User", foreign_keys=[caller_user_id], back_populates="caller_user_matching")
    callee_user = relationship("User", foreign_keys=[callee_user_id], back_populates="callee_user_matching")
    matching_category = relationship("MatchingCategory", back_populates="user")

class MatchingCategory(Base):
    __tablename__ = "matching_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    user = relationship("UserMatching", back_populates="matching_category")

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    meeting = relationship("Meeting", back_populates="category")

class Meeting(Base):
    __tablename__ = "meeting"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("user.id"))
    category_id = Column(Integer, ForeignKey("category.id"))
    meeting_image_url = Column(String, nullable=True)
    location = Column(String)
    title = Column(String)
    keyword = Column(String)
    description = Column(String)
    max_people = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    meeting_join_user = relationship("MeetingJoinUser", back_populates="meeting")
    host = relationship("User", back_populates="meeting")
    category = relationship("Category", back_populates="meeting")

class MeetingJoinUser(Base):
    __tablename__ = "meeting_join_user"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meeting.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    meeting = relationship("Meeting", back_populates="meeting_join_user")
    user = relationship("User", back_populates="meeting_join_user")

    __table_args__ = (UniqueConstraint('meeting_id', 'user_id'),)

class Community(Base):
    __tablename__ = "community"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=func.now())

    community_content = relationship("CommunityContent", back_populates="community")

class CommunityContent(Base):
    __tablename__ = "community_content"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("community.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String)
    content = Column(String)
    like_count = Column(Integer, default=0)
    content_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    reply = relationship("Reply", back_populates="community_content")
    writed_user = relationship("User", back_populates="community_content")
    community = relationship("Community", back_populates="community_content")

class Reply(Base):
    __tablename__ = "reply"

    id = Column(Integer, primary_key=True, index=True)
    community_content_id = Column(Integer, ForeignKey("community_content.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    content = Column(String)
    created_at = Column(DateTime, default=func.now())

    community_content = relationship("CommunityContent", back_populates="reply")
    user = relationship("User", back_populates="reply")