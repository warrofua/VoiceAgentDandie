"""Service for processing insurance queries."""
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.database_models import (
    Patient,
    Authorization,
    InsuranceQuery,
    Call
)
from src.insurance.rules_engine import ABAInsuranceRules


class InsuranceQueryService:
    """Service for handling insurance-related queries."""

    def __init__(self, db: Session):
        self.db = db
        self.rules_engine = ABAInsuranceRules(db)

    def verify_eligibility(
        self,
        member_id: str,
        date_of_birth: str,
        call_id: Optional[int] = None
    ) -> Dict:
        """
        Verify patient eligibility for ABA services.

        Args:
            member_id: Insurance member ID
            date_of_birth: Patient date of birth
            call_id: Associated call ID for logging

        Returns:
            Dictionary with eligibility information
        """
        try:
            # Find patient
            patient = self.db.query(Patient).filter(
                Patient.member_id == member_id
            ).first()

            if not patient:
                return {
                    "success": False,
                    "message": "Member not found in system",
                    "eligible": False
                }

            # Verify DOB matches (would need decryption in production)
            # For now, simplified check
            if patient.date_of_birth != date_of_birth:
                return {
                    "success": False,
                    "message": "Member information does not match",
                    "eligible": False
                }

            # Check for active authorization
            active_auth = self.db.query(Authorization).filter(
                Authorization.patient_id == patient.id,
                Authorization.status == "active"
            ).first()

            # Log query
            if call_id:
                self._log_query(
                    call_id=call_id,
                    patient_id=patient.id,
                    query_type="eligibility",
                    query_data={"member_id": member_id},
                    response_data={"eligible": True},
                    success=True
                )

            return {
                "success": True,
                "eligible": True,
                "member_name": f"{patient.first_name} {patient.last_name}",
                "insurance_carrier": patient.insurance_carrier,
                "has_active_authorization": active_auth is not None,
                "patient_id": patient.id
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error verifying eligibility: {str(e)}",
                "eligible": False
            }

    def check_authorization_status(
        self,
        patient_id: int,
        call_id: Optional[int] = None
    ) -> Dict:
        """
        Check authorization status for a patient.

        Args:
            patient_id: Patient ID
            call_id: Associated call ID for logging

        Returns:
            Dictionary with authorization details
        """
        try:
            # Get most recent authorization
            authorization = self.db.query(Authorization).filter(
                Authorization.patient_id == patient_id
            ).order_by(Authorization.created_at.desc()).first()

            if not authorization:
                return {
                    "success": True,
                    "has_authorization": False,
                    "message": "No authorization found for this patient"
                }

            # Check status using rules engine
            status_info = self.rules_engine.check_authorization_status(
                authorization
            )

            # Get approved services
            approved_services = authorization.approved_services or {}

            # Log query
            if call_id:
                self._log_query(
                    call_id=call_id,
                    patient_id=patient_id,
                    query_type="authorization",
                    query_data={"auth_number": authorization.auth_number},
                    response_data=status_info,
                    success=True
                )

            return {
                "success": True,
                "has_authorization": True,
                "auth_number": authorization.auth_number,
                "status": status_info["status"],
                "valid": status_info["valid"],
                "message": status_info["message"],
                "start_date": authorization.start_date.isoformat() if authorization.start_date else None,
                "end_date": authorization.end_date.isoformat() if authorization.end_date else None,
                "approved_services": approved_services,
                "provider": authorization.provider_name
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error checking authorization: {str(e)}"
            }

    def get_benefits_information(
        self,
        patient_id: int,
        cpt_codes: Optional[List[str]] = None,
        call_id: Optional[int] = None
    ) -> Dict:
        """
        Get benefits information for ABA services.

        Args:
            patient_id: Patient ID
            cpt_codes: Specific CPT codes to check
            call_id: Associated call ID for logging

        Returns:
            Dictionary with benefits information
        """
        try:
            patient = self.db.query(Patient).filter(
                Patient.id == patient_id
            ).first()

            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found"
                }

            carrier = patient.insurance_carrier or "default"

            # Get authorization requirements
            auth_requirements = self.rules_engine.get_authorization_requirements(
                carrier
            )

            # Get session limits for requested codes
            if not cpt_codes:
                cpt_codes = list(self.rules_engine.CPT_CODES.keys())

            limits = {}
            for code in cpt_codes:
                limit = self.rules_engine.get_session_limits(carrier, code)
                if limit:
                    limits[code] = {
                        "description": self.rules_engine.CPT_CODES[code],
                        "limit": limit
                    }

            # Log query
            if call_id:
                self._log_query(
                    call_id=call_id,
                    patient_id=patient_id,
                    query_type="benefits",
                    query_data={"cpt_codes": cpt_codes},
                    response_data={"limits": limits},
                    success=True
                )

            return {
                "success": True,
                "carrier": carrier,
                "authorization_requirements": auth_requirements,
                "service_limits": limits
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving benefits: {str(e)}"
            }

    def submit_prior_authorization(
        self,
        patient_id: int,
        diagnosis_codes: List[str],
        requested_services: Dict,
        provider_info: Dict,
        assessment_date: str,
        call_id: Optional[int] = None
    ) -> Dict:
        """
        Submit a prior authorization request.

        Args:
            patient_id: Patient ID
            diagnosis_codes: List of diagnosis codes
            requested_services: Services being requested
            provider_info: Provider information
            assessment_date: Date of assessment
            call_id: Associated call ID for logging

        Returns:
            Dictionary with submission results
        """
        try:
            patient = self.db.query(Patient).filter(
                Patient.id == patient_id
            ).first()

            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found"
                }

            # Validate medical necessity
            assessment_dt = datetime.fromisoformat(assessment_date)
            validation = self.rules_engine.validate_medical_necessity(
                diagnosis_codes=diagnosis_codes,
                assessment_date=assessment_dt,
                treatment_plan_exists=True  # Would check actual existence
            )

            if not validation["valid"]:
                return {
                    "success": False,
                    "message": "Medical necessity validation failed",
                    "issues": validation["issues"]
                }

            # Create authorization record
            auth_number = f"PA-{datetime.now().year}-{patient_id:06d}"

            authorization = Authorization(
                patient_id=patient_id,
                auth_number=auth_number,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=180),  # 6 months
                status="pending",
                diagnosis_codes=diagnosis_codes,
                approved_services=requested_services,
                assessment_date=assessment_dt,
                next_reassessment=self.rules_engine.calculate_next_reassessment_date(
                    assessment_dt
                ),
                provider_name=provider_info.get("name"),
                provider_npi=provider_info.get("npi"),
                provider_credential=provider_info.get("credential")
            )

            self.db.add(authorization)
            self.db.commit()

            # Log query
            if call_id:
                self._log_query(
                    call_id=call_id,
                    patient_id=patient_id,
                    query_type="prior_authorization",
                    query_data={
                        "diagnosis_codes": diagnosis_codes,
                        "services": requested_services
                    },
                    response_data={"auth_number": auth_number},
                    success=True
                )

            return {
                "success": True,
                "message": "Prior authorization submitted successfully",
                "auth_number": auth_number,
                "expected_turnaround": "5-7 business days",
                "status": "pending"
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error submitting authorization: {str(e)}"
            }

    def _log_query(
        self,
        call_id: int,
        patient_id: int,
        query_type: str,
        query_data: Dict,
        response_data: Dict,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Log insurance query for audit trail."""
        query_log = InsuranceQuery(
            call_id=call_id,
            patient_id=patient_id,
            query_type=query_type,
            query_data=query_data,
            response_data=response_data,
            success=success,
            error_message=error_message
        )
        self.db.add(query_log)
        self.db.commit()
