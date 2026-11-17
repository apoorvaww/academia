from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    degree = Column(String(100), nullable=True, default="B.Tech Computer Science")
    major = Column(String(100), nullable=True, default="Computer Science & Engineering")
    graduation_year = Column(Integer, nullable=True, default=2026)
    target_role = Column(String(100), nullable=True, default="Machine Learning Engineer")
    preferred_location = Column(String(100), nullable=True, default="Any")
    preferred_work_mode = Column(String(50), nullable=True, default="remote")  # remote, hybrid, onsite, any
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=True, default="Technical")

    student_associations = relationship("StudentSkill", back_populates="skill")

class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    evidence_source = Column(String(200), nullable=True)  # e.g. "Resume: Section 'Projects'", "User Input"
    confirmation_status = Column(String(50), default="confirmed")  # "confirmed", "candidate"
    proficiency = Column(String(50), default="intermediate")  # beginner, intermediate, advanced

    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill", back_populates="student_associations")

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    company = Column(String(100), nullable=False, index=True)
    location = Column(String(100), nullable=False, default="Remote")
    work_mode = Column(String(50), nullable=False, default="remote")  # remote, hybrid, onsite
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False)  # JSON-serialized list of canonical skill names
    preferred_skills = Column(Text, nullable=False)  # JSON-serialized list of canonical skill names
    status = Column(String(50), default="open")  # open, closed
    source_label = Column(String(50), default="[SAMPLE DATA]")
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    skill_tag = Column(String(100), nullable=False, index=True)  # canonical skill name
    resource_type = Column(String(50), default="Documentation")  # Documentation, Tutorial, Course, Interactive
    description = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=True)
