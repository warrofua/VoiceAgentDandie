"""Insurance rules engine for ABA therapy."""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.database_models import InsuranceRule, Authorization


class ABAInsuranceRules:
    """ABA therapy insurance rules and validation."""

    # Standard CPT codes for ABA therapy
    CPT_CODES = {
        "97151": "Behavior identification assessment",
        "97152": "Behavior identification supporting assessment",
        "97153": "Adaptive behavior treatment by technician",
        "97154": "Group adaptive behavior treatment by technician",
        "97155": "Adaptive behavior treatment with protocol modification",
        "97156": "Family adaptive behavior treatment guidance",
        "97157": "Multiple family group adaptive behavior treatment",
        "97158": "Group adaptive behavior treatment"
    }

    # Common autism diagnosis codes
    DIAGNOSIS_CODES = {
        "F84.0": "Autistic disorder",
        "F84.5": "Asperger's syndrome",
        "F84.8": "Other pervasive developmental disorders",
        "F84.9": "Pervasive developmental disorder, unspecified"
    }

    def __init__(self, db: Session):
        self.db = db

    def validate_cpt_code(self, cpt_code: str) -> bool:
        """Check if CPT code is valid for ABA therapy."""
        return cpt_code in self.CPT_CODES

    def validate_diagnosis_code(self, diagnosis_code: str) -> bool:
        """Check if diagnosis code is valid for ABA coverage."""
        return diagnosis_code in self.DIAGNOSIS_CODES

    def get_authorization_requirements(self, carrier_name: str) -> Dict:
        """
        Get authorization requirements for a specific carrier.

        Args:
            carrier_name: Insurance carrier name

        Returns:
            Dictionary with authorization requirements
        """
        rules = self.db.query(InsuranceRule).filter(
            InsuranceRule.carrier_name == carrier_name,
            InsuranceRule.rule_type == "authorization",
            InsuranceRule.is_active == True
        ).all()

        requirements = {
            "initial_auth_period": "6 months",
            "renewal_notice_days": 30,
            "required_documents": [
                "Comprehensive assessment",
                "Treatment plan",
                "Medical necessity documentation"
            ],
            "diagnosis_required": True,
            "provider_credentials": ["BCBA", "LBA"]
        }

        # Override with carrier-specific rules
        for rule in rules:
            requirements.update(rule.rule_data)

        return requirements

    def get_session_limits(
        self,
        carrier_name: str,
        cpt_code: str
    ) -> Optional[Dict]:
        """
        Get session limits for specific service.

        Args:
            carrier_name: Insurance carrier name
            cpt_code: CPT code for service

        Returns:
            Dictionary with limit information
        """
        rule = self.db.query(InsuranceRule).filter(
            InsuranceRule.carrier_name == carrier_name,
            InsuranceRule.rule_type == "session_limit",
            InsuranceRule.cpt_code == cpt_code,
            InsuranceRule.is_active == True
        ).first()

        if rule:
            return rule.rule_data

        # Default limits if no carrier-specific rule
        default_limits = {
            "97151": {"max_units": 1, "frequency": "per assessment"},
            "97152": {"max_units": 4, "frequency": "per assessment"},
            "97153": {"max_units": 160, "frequency": "per month"},
            "97154": {"max_units": 40, "frequency": "per month"},
            "97155": {"max_units": 8, "frequency": "per month"},
            "97156": {"max_units": 16, "frequency": "per month"},
            "97157": {"max_units": 8, "frequency": "per month"},
            "97158": {"max_units": 32, "frequency": "per month"}
        }

        return default_limits.get(cpt_code)

    def check_authorization_status(
        self,
        authorization: Authorization
    ) -> Dict:
        """
        Check current status of authorization.

        Args:
            authorization: Authorization object

        Returns:
            Dictionary with status information
        """
        now = datetime.now()

        # Check if expired
        if authorization.end_date and authorization.end_date < now:
            return {
                "status": "expired",
                "valid": False,
                "message": f"Authorization expired on {authorization.end_date.date()}"
            }

        # Check if approaching expiration
        if authorization.end_date:
            days_until_expiration = (authorization.end_date - now).days
            if days_until_expiration <= 30:
                return {
                    "status": "expiring_soon",
                    "valid": True,
                    "days_remaining": days_until_expiration,
                    "message": f"Authorization expires in {days_until_expiration} days"
                }

        # Check if reassessment needed
        if authorization.next_reassessment and authorization.next_reassessment < now:
            return {
                "status": "reassessment_needed",
                "valid": True,
                "message": "Reassessment is overdue"
            }

        return {
            "status": "active",
            "valid": True,
            "message": "Authorization is active"
        }

    def validate_medical_necessity(
        self,
        diagnosis_codes: List[str],
        assessment_date: Optional[datetime],
        treatment_plan_exists: bool
    ) -> Dict:
        """
        Validate medical necessity requirements.

        Args:
            diagnosis_codes: List of diagnosis codes
            assessment_date: Date of comprehensive assessment
            treatment_plan_exists: Whether treatment plan exists

        Returns:
            Dictionary with validation results
        """
        issues = []

        # Check diagnosis codes
        valid_diagnoses = [
            code for code in diagnosis_codes
            if self.validate_diagnosis_code(code)
        ]

        if not valid_diagnoses:
            issues.append("No valid autism spectrum diagnosis code provided")

        # Check assessment
        if not assessment_date:
            issues.append("Comprehensive assessment required")
        else:
            # Check if assessment is recent (within 6 months for initial)
            months_since_assessment = (
                datetime.now() - assessment_date
            ).days / 30

            if months_since_assessment > 6:
                issues.append("Assessment is more than 6 months old")

        # Check treatment plan
        if not treatment_plan_exists:
            issues.append("Treatment plan required")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "valid_diagnoses": valid_diagnoses
        }

    def calculate_next_reassessment_date(
        self,
        last_assessment_date: datetime,
        carrier_name: str = "default"
    ) -> datetime:
        """
        Calculate when next reassessment is due.

        Args:
            last_assessment_date: Date of last assessment
            carrier_name: Insurance carrier name

        Returns:
            Date of next reassessment
        """
        # Most carriers require reassessment every 6 months
        # This could be customized by carrier
        return last_assessment_date + timedelta(days=180)

    def check_provider_credentials(
        self,
        credential: str,
        cpt_code: str
    ) -> Dict:
        """
        Validate provider credentials for specific service.

        Args:
            credential: Provider credential (BCBA, LBA, RBT, etc.)
            cpt_code: CPT code being billed

        Returns:
            Dictionary with validation results
        """
        # Supervision requirements
        supervision_required = {
            "97151": ["BCBA", "LBA"],  # Assessment
            "97152": ["BCBA", "LBA"],  # Supporting assessment
            "97153": ["RBT", "BT"],    # Technician (requires supervision)
            "97154": ["RBT", "BT"],    # Group technician
            "97155": ["BCBA", "LBA"],  # Protocol modification
            "97156": ["BCBA", "LBA"],  # Family guidance
            "97157": ["BCBA", "LBA"],  # Multiple family group
            "97158": ["BCBA", "LBA"]   # Group treatment
        }

        allowed_credentials = supervision_required.get(cpt_code, [])

        if credential in allowed_credentials:
            return {
                "valid": True,
                "message": f"{credential} is qualified for {cpt_code}"
            }
        else:
            return {
                "valid": False,
                "message": f"{credential} not qualified for {cpt_code}",
                "required_credentials": allowed_credentials
            }

    def get_carrier_specific_rules(self, carrier_name: str) -> List[Dict]:
        """
        Get all rules for a specific carrier.

        Args:
            carrier_name: Insurance carrier name

        Returns:
            List of rules
        """
        rules = self.db.query(InsuranceRule).filter(
            InsuranceRule.carrier_name == carrier_name,
            InsuranceRule.is_active == True
        ).all()

        return [
            {
                "rule_type": rule.rule_type,
                "cpt_code": rule.cpt_code,
                "data": rule.rule_data,
                "effective_date": rule.effective_date
            }
            for rule in rules
        ]
