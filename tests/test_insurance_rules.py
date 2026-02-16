"""Tests for insurance rules engine."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.connection import Base
from src.models.database_models import Authorization, InsuranceRule
from src.insurance.rules_engine import ABAInsuranceRules


@pytest.fixture
def db_session():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def rules_engine(db_session):
    """Create rules engine instance."""
    return ABAInsuranceRules(db_session)


def test_validate_cpt_code(rules_engine):
    """Test CPT code validation."""
    assert rules_engine.validate_cpt_code("97153") is True
    assert rules_engine.validate_cpt_code("97155") is True
    assert rules_engine.validate_cpt_code("99999") is False


def test_validate_diagnosis_code(rules_engine):
    """Test diagnosis code validation."""
    assert rules_engine.validate_diagnosis_code("F84.0") is True
    assert rules_engine.validate_diagnosis_code("F84.5") is True
    assert rules_engine.validate_diagnosis_code("Z99.9") is False


def test_check_authorization_status_active(rules_engine, db_session):
    """Test checking active authorization status."""
    now = datetime.now()

    auth = Authorization(
        patient_id=1,
        auth_number="TEST-001",
        start_date=now - timedelta(days=30),
        end_date=now + timedelta(days=150),
        status="active",
        diagnosis_codes=["F84.0"]
    )
    db_session.add(auth)
    db_session.commit()

    status = rules_engine.check_authorization_status(auth)

    assert status["status"] == "active"
    assert status["valid"] is True


def test_check_authorization_status_expired(rules_engine, db_session):
    """Test checking expired authorization status."""
    now = datetime.now()

    auth = Authorization(
        patient_id=1,
        auth_number="TEST-002",
        start_date=now - timedelta(days=200),
        end_date=now - timedelta(days=10),
        status="active",
        diagnosis_codes=["F84.0"]
    )
    db_session.add(auth)
    db_session.commit()

    status = rules_engine.check_authorization_status(auth)

    assert status["status"] == "expired"
    assert status["valid"] is False


def test_check_authorization_status_expiring_soon(rules_engine, db_session):
    """Test checking authorization expiring soon."""
    now = datetime.now()

    auth = Authorization(
        patient_id=1,
        auth_number="TEST-003",
        start_date=now - timedelta(days=150),
        end_date=now + timedelta(days=20),
        status="active",
        diagnosis_codes=["F84.0"]
    )
    db_session.add(auth)
    db_session.commit()

    status = rules_engine.check_authorization_status(auth)

    assert status["status"] == "expiring_soon"
    assert status["valid"] is True
    assert status["days_remaining"] == 20


def test_validate_medical_necessity_valid(rules_engine):
    """Test valid medical necessity validation."""
    result = rules_engine.validate_medical_necessity(
        diagnosis_codes=["F84.0"],
        assessment_date=datetime.now() - timedelta(days=30),
        treatment_plan_exists=True
    )

    assert result["valid"] is True
    assert len(result["issues"]) == 0


def test_validate_medical_necessity_invalid(rules_engine):
    """Test invalid medical necessity validation."""
    result = rules_engine.validate_medical_necessity(
        diagnosis_codes=["Z99.9"],  # Invalid diagnosis
        assessment_date=None,
        treatment_plan_exists=False
    )

    assert result["valid"] is False
    assert len(result["issues"]) > 0


def test_check_provider_credentials_valid(rules_engine):
    """Test valid provider credentials."""
    result = rules_engine.check_provider_credentials(
        credential="BCBA",
        cpt_code="97155"
    )

    assert result["valid"] is True


def test_check_provider_credentials_invalid(rules_engine):
    """Test invalid provider credentials."""
    result = rules_engine.check_provider_credentials(
        credential="RBT",
        cpt_code="97155"  # RBT cannot do protocol modification
    )

    assert result["valid"] is False


def test_get_session_limits(rules_engine, db_session):
    """Test getting session limits."""
    # Add a rule
    rule = InsuranceRule(
        carrier_name="TestCarrier",
        rule_type="session_limit",
        cpt_code="97153",
        rule_data={"max_units": 100, "frequency": "per month"},
        is_active=True
    )
    db_session.add(rule)
    db_session.commit()

    limits = rules_engine.get_session_limits("TestCarrier", "97153")

    assert limits is not None
    assert limits["max_units"] == 100
    assert limits["frequency"] == "per month"
