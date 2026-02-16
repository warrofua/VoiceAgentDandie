"""
Demo script showing a simulated conversation flow.
This demonstrates how the voice agent processes insurance inquiries.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.connection import SessionLocal
from src.insurance.query_service import InsuranceQueryService
from src.insurance.conversation_agent import ConversationAgent


async def simulate_authorization_check():
    """Simulate a caller checking authorization status."""
    print("\n" + "="*60)
    print("DEMO: Authorization Status Check")
    print("="*60 + "\n")

    db = SessionLocal()

    try:
        # Initialize services
        query_service = InsuranceQueryService(db)
        agent = ConversationAgent(query_service)

        # Start conversation
        welcome = await agent.start_conversation()
        print(f"🤖 Agent: {welcome}\n")

        # Simulate conversation turns
        turns = [
            {
                "caller": "Hi, I need to check on an authorization for my son.",
                "context": None
            },
            {
                "caller": "The member ID is BCBS123456 and date of birth is March 15, 2018",
                "context": None
            },
            {
                "caller": "Can you tell me what services are covered?",
                "context": {
                    "patient_verified": True,
                    "patient_id": 1,
                    "patient_name": "John Doe",
                    "member_id": "BCBS123456",
                    "insurance_carrier": "Blue Cross Blue Shield",
                    "call_id": 999
                }
            },
            {
                "caller": "When does it expire?",
                "context": {
                    "patient_verified": True,
                    "patient_id": 1,
                    "patient_name": "John Doe",
                    "member_id": "BCBS123456",
                    "insurance_carrier": "Blue Cross Blue Shield",
                    "call_id": 999
                }
            },
            {
                "caller": "Thank you, that's all I needed!",
                "context": {
                    "patient_verified": True,
                    "patient_id": 1,
                    "call_id": 999
                }
            }
        ]

        for i, turn in enumerate(turns, 1):
            print(f"👤 Caller: {turn['caller']}\n")

            # Process input
            response = await agent.process_user_input(
                user_input=turn['caller'],
                context=turn['context']
            )

            print(f"🤖 Agent: {response['response']}\n")
            print(f"   [Intent: {response['intent']}]")

            if response.get('query_results'):
                print(f"   [Query Results: {list(response['query_results'].keys())}]")

            print()
            await asyncio.sleep(1)  # Simulate natural pace

        print("="*60)
        print("✅ Conversation completed successfully!")
        print("="*60)

    finally:
        db.close()


async def simulate_benefits_inquiry():
    """Simulate a caller asking about benefits."""
    print("\n" + "="*60)
    print("DEMO: Benefits Inquiry")
    print("="*60 + "\n")

    db = SessionLocal()

    try:
        query_service = InsuranceQueryService(db)
        agent = ConversationAgent(query_service)

        # Start conversation
        welcome = await agent.start_conversation()
        print(f"🤖 Agent: {welcome}\n")

        # Quick verification then benefits question
        turns = [
            "I want to know what ABA services are covered",
            "Member ID AETNA789012, DOB July 22, 2019",
            "What's the limit for technician services?",
            "And how many hours of BCBA supervision?"
        ]

        context = None

        for turn in turns:
            print(f"👤 Caller: {turn}\n")

            # Update context after verification
            if "AETNA" in turn:
                context = {
                    "patient_verified": True,
                    "patient_id": 2,
                    "patient_name": "Jane Smith",
                    "insurance_carrier": "Aetna",
                    "call_id": 1000
                }

            response = await agent.process_user_input(
                user_input=turn,
                context=context
            )

            print(f"🤖 Agent: {response['response']}\n")
            await asyncio.sleep(1)

    finally:
        db.close()


async def demonstrate_rules_engine():
    """Demonstrate the insurance rules engine directly."""
    print("\n" + "="*60)
    print("DEMO: Insurance Rules Engine")
    print("="*60 + "\n")

    db = SessionLocal()

    try:
        from src.insurance.rules_engine import ABAInsuranceRules

        rules = ABAInsuranceRules(db)

        # Show CPT codes
        print("📋 ABA Therapy CPT Codes:")
        for code, desc in rules.CPT_CODES.items():
            print(f"   {code}: {desc}")

        print("\n📋 Valid Diagnosis Codes:")
        for code, desc in rules.DIAGNOSIS_CODES.items():
            print(f"   {code}: {desc}")

        # Test validations
        print("\n🔍 Testing CPT Code Validation:")
        test_codes = ["97153", "97155", "99999"]
        for code in test_codes:
            valid = rules.validate_cpt_code(code)
            status = "✅ Valid" if valid else "❌ Invalid"
            print(f"   {code}: {status}")

        # Show session limits
        print("\n📊 Session Limits (Blue Cross Blue Shield):")
        for code in ["97153", "97155", "97156"]:
            limits = rules.get_session_limits("Blue Cross Blue Shield", code)
            if limits:
                print(f"   {code}: {limits}")

        # Test provider credentials
        print("\n👨‍⚕️ Provider Credential Validation:")
        tests = [
            ("BCBA", "97155", "Protocol modification"),
            ("RBT", "97153", "Technician services"),
            ("RBT", "97155", "Protocol modification")
        ]

        for credential, cpt, service in tests:
            result = rules.check_provider_credentials(credential, cpt)
            status = "✅" if result["valid"] else "❌"
            print(f"   {status} {credential} for {service} ({cpt})")

    finally:
        db.close()


async def main():
    """Run all demos."""
    print("\n" + "🎭 "*20)
    print("   ABA VOICE AGENT - SYSTEM DEMONSTRATION")
    print("🎭 "*20)

    demos = [
        ("Insurance Rules Engine", demonstrate_rules_engine),
        ("Authorization Check Conversation", simulate_authorization_check),
        ("Benefits Inquiry Conversation", simulate_benefits_inquiry)
    ]

    for name, demo_func in demos:
        try:
            await demo_func()
            print("\n" + "-"*60 + "\n")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}\n")

    print("\n" + "🎉 "*20)
    print("   DEMONSTRATION COMPLETE")
    print("🎉 "*20 + "\n")


if __name__ == "__main__":
    # Check if database is seeded
    print("\n📝 Make sure you've run: python scripts/seed_data.py\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {str(e)}\n")
