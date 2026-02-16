"""Script to seed database with sample data."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.database.connection import SessionLocal
from src.models.database_models import (
    Patient,
    Authorization,
    InsuranceRule
)


def seed_insurance_rules(db):
    """Seed insurance rules for common carriers."""
    print("Seeding insurance rules...")

    rules = [
        # Blue Cross Blue Shield
        InsuranceRule(
            carrier_name="Blue Cross Blue Shield",
            rule_type="authorization",
            rule_data={
                "initial_auth_period": "6 months",
                "renewal_notice_days": 30,
                "requires_prior_auth": True
            },
            is_active=True
        ),
        InsuranceRule(
            carrier_name="Blue Cross Blue Shield",
            rule_type="session_limit",
            cpt_code="97153",
            rule_data={
                "max_units": 160,
                "frequency": "per month",
                "requires_supervision": True
            },
            is_active=True
        ),
        InsuranceRule(
            carrier_name="Blue Cross Blue Shield",
            rule_type="session_limit",
            cpt_code="97155",
            rule_data={
                "max_units": 8,
                "frequency": "per month"
            },
            is_active=True
        ),

        # Aetna
        InsuranceRule(
            carrier_name="Aetna",
            rule_type="authorization",
            rule_data={
                "initial_auth_period": "6 months",
                "renewal_notice_days": 45,
                "requires_prior_auth": True
            },
            is_active=True
        ),
        InsuranceRule(
            carrier_name="Aetna",
            rule_type="session_limit",
            cpt_code="97153",
            rule_data={
                "max_units": 120,
                "frequency": "per month"
            },
            is_active=True
        ),

        # UnitedHealthcare
        InsuranceRule(
            carrier_name="UnitedHealthcare",
            rule_type="authorization",
            rule_data={
                "initial_auth_period": "3 months",
                "renewal_notice_days": 30,
                "requires_prior_auth": True,
                "reassessment_frequency": "every 3 months"
            },
            is_active=True
        ),
        InsuranceRule(
            carrier_name="UnitedHealthcare",
            rule_type="session_limit",
            cpt_code="97153",
            rule_data={
                "max_units": 200,
                "frequency": "per month"
            },
            is_active=True
        ),
    ]

    for rule in rules:
        db.add(rule)

    db.commit()
    print(f"Added {len(rules)} insurance rules")


def seed_sample_patients(db):
    """Seed sample patient data."""
    print("Seeding sample patients...")

    patients = [
        Patient(
            member_id="BCBS123456",
            date_of_birth="2018-03-15",  # Would be encrypted in production
            first_name="John",  # Would be encrypted in production
            last_name="Doe",  # Would be encrypted in production
            insurance_carrier="Blue Cross Blue Shield",
            policy_number="POL-12345"
        ),
        Patient(
            member_id="AETNA789012",
            date_of_birth="2019-07-22",
            first_name="Jane",
            last_name="Smith",
            insurance_carrier="Aetna",
            policy_number="POL-67890"
        ),
        Patient(
            member_id="UHC345678",
            date_of_birth="2020-01-10",
            first_name="Michael",
            last_name="Johnson",
            insurance_carrier="UnitedHealthcare",
            policy_number="POL-34567"
        ),
    ]

    for patient in patients:
        db.add(patient)

    db.commit()
    print(f"Added {len(patients)} sample patients")

    return patients


def seed_sample_authorizations(db, patients):
    """Seed sample authorizations."""
    print("Seeding sample authorizations...")

    now = datetime.now()

    authorizations = [
        # Active authorization
        Authorization(
            patient_id=patients[0].id,
            auth_number="AUTH-2024-001234",
            start_date=now - timedelta(days=60),
            end_date=now + timedelta(days=120),
            status="active",
            diagnosis_codes=["F84.0"],
            approved_services={
                "97153": {"units": 160, "frequency": "monthly"},
                "97155": {"units": 8, "frequency": "monthly"},
                "97156": {"units": 4, "frequency": "monthly"}
            },
            assessment_date=now - timedelta(days=90),
            next_reassessment=now + timedelta(days=90),
            provider_name="Dr. Sarah Williams",
            provider_npi="1234567890",
            provider_credential="BCBA"
        ),

        # Expiring soon authorization
        Authorization(
            patient_id=patients[1].id,
            auth_number="AUTH-2024-005678",
            start_date=now - timedelta(days=150),
            end_date=now + timedelta(days=20),
            status="active",
            diagnosis_codes=["F84.0", "F84.5"],
            approved_services={
                "97153": {"units": 120, "frequency": "monthly"},
                "97155": {"units": 8, "frequency": "monthly"}
            },
            assessment_date=now - timedelta(days=180),
            next_reassessment=now + timedelta(days=10),
            provider_name="Dr. Michael Chen",
            provider_npi="0987654321",
            provider_credential="LBA"
        ),

        # Pending authorization
        Authorization(
            patient_id=patients[2].id,
            auth_number="AUTH-2024-009012",
            start_date=now,
            end_date=now + timedelta(days=90),
            status="pending",
            diagnosis_codes=["F84.9"],
            approved_services={
                "97153": {"units": 200, "frequency": "monthly"},
                "97155": {"units": 8, "frequency": "monthly"}
            },
            assessment_date=now - timedelta(days=30),
            next_reassessment=now + timedelta(days=60),
            provider_name="Dr. Emily Rodriguez",
            provider_npi="5555555555",
            provider_credential="BCBA"
        ),
    ]

    for auth in authorizations:
        db.add(auth)

    db.commit()
    print(f"Added {len(authorizations)} sample authorizations")


def main():
    """Run all seed functions."""
    print("Starting database seeding...")

    db = SessionLocal()

    try:
        seed_insurance_rules(db)
        patients = seed_sample_patients(db)
        seed_sample_authorizations(db, patients)

        print("\n✅ Database seeding completed successfully!")

    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
