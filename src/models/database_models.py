"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.connection import Base


class Call(Base):
    """Model for storing call information."""
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # inbound/outbound
    status = Column(String, nullable=False)  # in-progress, completed, failed
    duration = Column(Integer)  # in seconds
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))

    # Relationships
    transcripts = relationship("Transcript", back_populates="call", cascade="all, delete-orphan")
    insurance_queries = relationship("InsuranceQuery", back_populates="call")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Transcript(Base):
    """Model for storing call transcripts."""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    speaker = Column(String, nullable=False)  # caller/agent
    text = Column(Text, nullable=False)
    confidence = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Audio metadata
    audio_duration = Column(Float)
    language = Column(String, default="en")

    # Relationship
    call = relationship("Call", back_populates="transcripts")


class Patient(Base):
    """Model for patient information (HIPAA sensitive)."""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, index=True, nullable=False)
    date_of_birth = Column(String, nullable=False)  # Encrypted
    first_name = Column(String)  # Encrypted
    last_name = Column(String)  # Encrypted

    # Insurance information
    insurance_carrier = Column(String)
    policy_number = Column(String)

    # Relationships
    authorizations = relationship("Authorization", back_populates="patient")
    insurance_queries = relationship("InsuranceQuery", back_populates="patient")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Authorization(Base):
    """Model for ABA therapy authorizations."""
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    auth_number = Column(String, unique=True, index=True)

    # Authorization details
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String, nullable=False)  # active, expired, pending, denied

    # Diagnosis
    diagnosis_codes = Column(JSON)  # List of ICD-10 codes

    # Approved services (CPT codes and units)
    approved_services = Column(JSON)
    # Example: {"97153": {"units": 120, "frequency": "weekly"}}

    # Medical necessity
    assessment_date = Column(DateTime(timezone=True))
    next_reassessment = Column(DateTime(timezone=True))

    # Provider information
    provider_name = Column(String)
    provider_npi = Column(String)
    provider_credential = Column(String)  # BCBA, LBA, etc.

    # Relationship
    patient = relationship("Patient", back_populates="authorizations")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InsuranceRule(Base):
    """Model for insurance carrier rules."""
    __tablename__ = "insurance_rules"

    id = Column(Integer, primary_key=True, index=True)
    carrier_name = Column(String, nullable=False, index=True)
    rule_type = Column(String, nullable=False)  # authorization, session_limit, provider_req, etc.

    # Rule definition
    cpt_code = Column(String)
    rule_data = Column(JSON, nullable=False)
    # Example: {"max_units_per_week": 40, "requires_prior_auth": true}

    effective_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InsuranceQuery(Base):
    """Model for tracking insurance queries made during calls."""
    __tablename__ = "insurance_queries"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"))

    query_type = Column(String, nullable=False)  # eligibility, authorization, benefits, claim
    query_data = Column(JSON)
    response_data = Column(JSON)

    success = Column(Boolean)
    error_message = Column(Text)

    # Relationship
    call = relationship("Call", back_populates="insurance_queries")
    patient = relationship("Patient", back_populates="insurance_queries")

    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """Model for HIPAA compliance audit logging."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Action details
    action_type = Column(String, nullable=False)  # access, modify, delete, etc.
    resource_type = Column(String, nullable=False)  # patient, authorization, call, etc.
    resource_id = Column(Integer)

    # User/System details
    user_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)

    # Data accessed
    data_accessed = Column(JSON)

    # Result
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())
