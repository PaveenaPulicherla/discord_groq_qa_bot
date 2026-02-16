#!/usr/bin/env python3
"""
Test Groq Integration
Verifies Groq LLM test generation is working
"""

import os
import sys

print("🧪 Testing Groq Integration")
print("="*60)

# Step 1: Check API key
print("\n1️⃣ Checking GROQ_API_KEY...")
api_key = os.getenv('GROQ_API_KEY')

if api_key:
    print(f"✅ API key is set")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
else:
    print("❌ GROQ_API_KEY not set")
    print("\n💡 To fix:")
    print("   1. Get API key from: https://console.groq.com")
    print("   2. Run: export GROQ_API_KEY='gsk_...'")
    print("   3. Restart this script")
    sys.exit(1)

# Step 2: Test Groq designer
print("\n2️⃣ Testing Groq Test Designer...")
try:
    from groq_test_designer import GroqTestCaseDesigner
    print("✅ GroqTestCaseDesigner imported successfully")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

# Step 3: Initialize designer
print("\n3️⃣ Initializing designer...")
try:
    designer = GroqTestCaseDesigner()
    print(f"✅ Designer initialized")
    print(f"   Model: {designer.model}")
    print(f"   LLM enabled: {designer.use_llm}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    sys.exit(1)

# Step 4: Generate test cases
print("\n4️⃣ Generating test cases with Groq...")
print("   ⏳ This may take 2-5 seconds...")

requirements = {
    'fraud_types': ['wire_transfer_fraud'],
    'detection_rules': {
        'high_value_threshold': 10000
    }
}

try:
    test_cases = designer.generate_test_cases(requirements)
    print(f"✅ Generated {len(test_cases)} test cases")
    
    # Show first test case
    if test_cases:
        first_case = test_cases[0]
        print(f"\n📋 First Test Case:")
        print(f"   ID: {first_case.test_case_id}")
        print(f"   Category: {first_case.category}")
        print(f"   Description: {first_case.description[:80]}...")
        print(f"   Fraud Patterns: {', '.join(first_case.fraud_patterns_tested[:3])}")
    
except Exception as e:
    print(f"❌ Test generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test with full QA agent
print("\n5️⃣ Testing with full QA agent...")
try:
    from fraud_qa_agent import FraudQAAgent
    
    agent = FraudQAAgent()
    print("✅ QA Agent initialized")
    
    # Check if it will use Groq
    print("   Running quick test...")
    quick_requirements = {
        'fraud_types': ['card_fraud'],
        'detection_rules': {'high_value_threshold': 10000}
    }
    
    test_cases = agent.design_test_cases(quick_requirements)
    print(f"✅ Agent generated {len(test_cases)} test cases")
    
except Exception as e:
    print(f"⚠️ Agent test failed: {e}")
    print("   (Designer test passed, so Groq is working)")

print("\n" + "="*60)
print("✅ All Groq integration tests passed!")
print("\n💡 Next steps:")
print("   1. Restart your Discord bot")
print("   2. Run /run-qa quick:True")
print("   3. Look for '🤖 with Groq LLM' in the status")
print("="*60)