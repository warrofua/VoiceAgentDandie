"""GPT-4 powered conversation agent for insurance calls."""
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from src.config import get_settings
from src.insurance.query_service import InsuranceQueryService

settings = get_settings()


class ConversationAgent:
    """AI agent for handling insurance conversations."""

    SYSTEM_PROMPT = """You are a professional and helpful insurance assistant for ABA (Applied Behavior Analysis) therapy services. Your role is to:

1. Verify caller information and patient eligibility
2. Answer questions about insurance coverage and benefits
3. Check authorization status and explain coverage details
4. Help with prior authorization submissions
5. Provide clear, accurate information about ABA therapy CPT codes and requirements
6. Maintain HIPAA compliance by protecting patient information
7. Transfer to human agent when necessary

Important guidelines:
- Always verify caller identity before discussing patient information
- Be professional, empathetic, and patient
- Explain insurance terms in simple language
- Never make guarantees about coverage - provide information based on current authorization
- If you're unsure, offer to transfer to a human representative
- Keep responses concise and clear for phone conversations

Available CPT codes:
- 97151: Behavior identification assessment
- 97152: Behavior identification supporting assessment
- 97153: Adaptive behavior treatment by technician
- 97154: Group adaptive behavior treatment by technician
- 97155: Adaptive behavior treatment with protocol modification (BCBA supervision)
- 97156: Family adaptive behavior treatment guidance
- 97157: Multiple family group adaptive behavior treatment
- 97158: Group adaptive behavior treatment

Common diagnosis codes for ABA coverage:
- F84.0: Autistic disorder
- F84.5: Asperger's syndrome
- F84.8: Other pervasive developmental disorders
- F84.9: Pervasive developmental disorder, unspecified"""

    def __init__(self, query_service: InsuranceQueryService):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.gpt_model
        self.query_service = query_service
        self.conversation_history: List[Dict] = []

    async def start_conversation(self) -> str:
        """
        Start a new conversation.

        Returns:
            Welcome message
        """
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

        welcome_message = (
            "Hello, thank you for calling ABA Therapy Insurance Services. "
            "I'm here to help you with insurance verification, authorizations, "
            "and benefit inquiries. How may I assist you today?"
        )

        self.conversation_history.append({
            "role": "assistant",
            "content": welcome_message
        })

        return welcome_message

    async def process_user_input(
        self,
        user_input: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user input and generate response.

        Args:
            user_input: User's spoken text
            context: Additional context (verified patient info, etc.)

        Returns:
            Dictionary with response and any actions needed
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Add context if available
        if context:
            context_message = self._format_context(context)
            self.conversation_history.append({
                "role": "system",
                "content": context_message
            })

        # Detect intent and extract entities
        intent_info = await self._detect_intent(user_input)

        # Execute any needed queries
        query_results = await self._execute_queries(intent_info, context)

        # Generate response with query results
        response_text = await self._generate_response(query_results)

        return {
            "response": response_text,
            "intent": intent_info["intent"],
            "entities": intent_info["entities"],
            "requires_action": intent_info.get("requires_action", False),
            "query_results": query_results
        }

    async def _detect_intent(self, user_input: str) -> Dict:
        """
        Detect user intent and extract entities.

        Args:
            user_input: User's message

        Returns:
            Dictionary with intent and entities
        """
        detection_prompt = f"""Analyze this user message and identify:
1. Primary intent (eligibility_check, authorization_status, benefits_inquiry,
   prior_auth_submission, general_question, transfer_request)
2. Any entities mentioned (member_id, date_of_birth, cpt_codes, etc.)
3. Whether this requires taking an action (database query, transfer, etc.)

User message: "{user_input}"

Respond in this exact JSON format:
{{
    "intent": "intent_name",
    "entities": {{"entity_type": "value"}},
    "requires_action": true/false,
    "confidence": 0.0-1.0
}}"""

        messages = [
            {"role": "system", "content": "You are an intent detection system."},
            {"role": "user", "content": detection_prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def _execute_queries(
        self,
        intent_info: Dict,
        context: Optional[Dict]
    ) -> Dict:
        """
        Execute database queries based on detected intent.

        Args:
            intent_info: Detected intent information
            context: Current conversation context

        Returns:
            Query results
        """
        intent = intent_info.get("intent")
        entities = intent_info.get("entities", {})
        results = {}

        if not context or not context.get("patient_id"):
            return results

        patient_id = context["patient_id"]
        call_id = context.get("call_id")

        try:
            if intent == "authorization_status":
                results["authorization"] = (
                    self.query_service.check_authorization_status(
                        patient_id=patient_id,
                        call_id=call_id
                    )
                )

            elif intent == "benefits_inquiry":
                cpt_codes = entities.get("cpt_codes")
                results["benefits"] = (
                    self.query_service.get_benefits_information(
                        patient_id=patient_id,
                        cpt_codes=cpt_codes,
                        call_id=call_id
                    )
                )

            elif intent == "eligibility_check":
                # Already verified in context, just confirm
                results["eligibility"] = {"verified": True}

        except Exception as e:
            results["error"] = str(e)

        return results

    async def _generate_response(self, query_results: Dict) -> str:
        """
        Generate natural language response.

        Args:
            query_results: Results from database queries

        Returns:
            Response text
        """
        # Add query results to context if available
        if query_results:
            results_context = f"Database query results: {query_results}"
            self.conversation_history.append({
                "role": "system",
                "content": results_context
            })

        # Generate response
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            temperature=0.7,
            max_tokens=200  # Keep responses concise for phone
        )

        assistant_message = response.choices[0].message.content

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def _format_context(self, context: Dict) -> str:
        """Format context information for the agent."""
        context_parts = []

        if context.get("patient_verified"):
            context_parts.append(
                f"Patient verified: {context.get('patient_name')}"
            )
            context_parts.append(
                f"Member ID: {context.get('member_id')}"
            )
            context_parts.append(
                f"Insurance: {context.get('insurance_carrier')}"
            )

        return " | ".join(context_parts)

    async def verify_patient_identity(
        self,
        member_id: str,
        date_of_birth: str,
        call_id: int
    ) -> Dict:
        """
        Verify patient identity before providing information.

        Args:
            member_id: Insurance member ID
            date_of_birth: Patient DOB for verification
            call_id: Current call ID

        Returns:
            Verification results
        """
        result = self.query_service.verify_eligibility(
            member_id=member_id,
            date_of_birth=date_of_birth,
            call_id=call_id
        )

        if result["success"] and result["eligible"]:
            return {
                "verified": True,
                "patient_id": result["patient_id"],
                "patient_name": result["member_name"],
                "insurance_carrier": result["insurance_carrier"],
                "has_active_auth": result["has_active_authorization"]
            }
        else:
            return {
                "verified": False,
                "message": result.get("message", "Unable to verify identity")
            }

    async def handle_transfer_request(self) -> str:
        """
        Handle request to transfer to human agent.

        Returns:
            Transfer message
        """
        return (
            "I understand you'd like to speak with a representative. "
            "Let me transfer you to someone who can better assist you. "
            "Please hold for a moment."
        )

    def get_conversation_summary(self) -> str:
        """
        Generate summary of conversation for handoff.

        Returns:
            Conversation summary
        """
        messages = [
            msg for msg in self.conversation_history
            if msg["role"] in ["user", "assistant"]
        ]

        summary_parts = []
        for msg in messages[-6:]:  # Last 3 exchanges
            role = "Caller" if msg["role"] == "user" else "Agent"
            summary_parts.append(f"{role}: {msg['content']}")

        return "\n".join(summary_parts)

    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
