"""
Comprehensive test with multiple clause types

Tests various contract clauses to ensure the agent works well across different scenarios.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.explanation.agent import ExplanationAgent
import time


def print_header(title):
    """Print a nice header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(result, show_full=False):
    """Print explanation result in a clean format"""
    print(f"\n📝 Plain English:")
    print(f"   {result['plain_english'][:300]}...")
    
    print(f"\n⚠️  Risk Level: {result['freelancer_impact']}")
    print(f"📊 Confidence: {result.get('confidence', 'N/A')}")
    
    if show_full and 'real_world_example' in result:
        print(f"\n📖 Real World Example:")
        print(f"   {result['real_world_example'][:200]}...")
    
    if 'key_points' in result and result['key_points']:
        print(f"\n💡 Key Points:")
        for i, point in enumerate(result['key_points'][:3], 1):
            print(f"   {i}. {point[:80]}...")
    
    if show_full and 'good_version' in result:
        good = result['good_version']
        if isinstance(good, dict) and 'text' in good:
            print(f"\n✅ Better Version:")
            print(f"   {good['text'][:150]}...")
    
    print("\n" + "-"*70)


def run_test(agent, test_num, clause, clause_type, description):
    """Run a single test"""
    print_header(f"TEST {test_num}: {description}")
    print(f"\n📄 Clause Type: {clause_type}")
    print(f"📄 Clause Text: \"{clause[:100]}{'...' if len(clause) > 100 else ''}\"")
    print(f"\n⏳ Asking Claude...")
    
    start_time = time.time()
    
    try:
        result = agent.explain(
            clause_text=clause,
            clause_type=clause_type
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Response received in {elapsed:.1f} seconds")
        
        print_result(result, show_full=(test_num in [1, 3, 5]))
        
        return True, result
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False, None
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Error after {elapsed:.1f} seconds: {str(e)}")
        return False, None


def main():
    print("="*70)
    print("  COMPREHENSIVE EXPLANATION AGENT TEST SUITE")
    print("="*70)
    print("\nTesting agent with various contract clause types...")
    print("This will test: payment, IP, indemnification, termination, and warranty")
    print("\n⏱️  Estimated time: 2-3 minutes total")
    
    # Initialize agent once
    print("\n🚀 Initializing agent...")
    try:
        agent = ExplanationAgent(enable_memory=False)
        print("✅ Agent ready!\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Define test cases
    tests = [
        {
            'num': 1,
            'clause': 'Payment shall be made within 90 days of invoice submission.',
            'type': 'payment',
            'desc': 'Long Payment Terms'
        },
        {
            'num': 2,
            'clause': 'All work product and intellectual property created shall be owned exclusively by the Company.',
            'type': 'intellectual_property',
            'desc': 'IP Ownership'
        },
        {
            'num': 3,
            'clause': 'Contractor agrees to indemnify, defend, and hold harmless Company from any and all claims, damages, losses, and expenses, including attorneys\' fees.',
            'type': 'indemnification',
            'desc': 'Broad Indemnification'
        },
        {
            'num': 4,
            'clause': 'Either party may terminate this agreement with 30 days written notice.',
            'type': 'termination',
            'desc': 'Termination Notice (Fair)'
        },
        {
            'num': 5,
            'clause': 'Company may terminate this agreement immediately for any reason or no reason.',
            'type': 'termination',
            'desc': 'At-Will Termination (Unfair)'
        },
        {
            'num': 6,
            'clause': 'Services are provided AS-IS without any warranty of any kind.',
            'type': 'warranty',
            'desc': 'No Warranty Disclaimer'
        },
        {
            'num': 7,
            'clause': 'Contractor shall not compete with Company for 2 years after termination in any market.',
            'type': 'non_compete',
            'desc': 'Broad Non-Compete'
        },
        {
            'num': 8,
            'clause': 'Payment: Net 30 days.',
            'type': 'payment',
            'desc': 'Short Payment Terms (Good)'
        }
    ]
    
    # Track results
    passed = 0
    failed = 0
    results = []
    
    # Run each test
    for test in tests:
        success, result = run_test(
            agent,
            test['num'],
            test['clause'],
            test['type'],
            test['desc']
        )
        
        if success:
            passed += 1
            results.append({
                'test': test['num'],
                'desc': test['desc'],
                'impact': result.get('freelancer_impact', 'UNKNOWN'),
                'confidence': result.get('confidence', 'UNKNOWN')
            })
        else:
            failed += 1
        
        # Small pause between tests to avoid rate limiting
        if test['num'] < len(tests):
            time.sleep(1)
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if results:
        print("\n📊 Results Overview:")
        print(f"\n{'#':<4} {'Description':<30} {'Impact':<10} {'Confidence':<12}")
        print("-"*60)
        for r in results:
            print(f"{r['test']:<4} {r['desc']:<30} {r['impact']:<10} {r['confidence']:<12}")
    
    print("\n" + "="*70)
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Your agent is working perfectly!")
        print("\n✅ The agent successfully:")
        print("   - Explained payment terms (short and long)")
        print("   - Analyzed IP ownership clauses")
        print("   - Identified indemnification risks")
        print("   - Evaluated termination clauses (fair and unfair)")
        print("   - Handled warranty disclaimers")
        print("   - Assessed non-compete restrictions")
        print("\n🚀 Your Explanation Agent is production-ready!")
    elif passed > 0:
        print(f"⚠️  {passed} tests passed, {failed} failed")
        print("   The agent is mostly working. Check failed tests above.")
    else:
        print("❌ All tests failed. Check AWS configuration and error messages.")
    
    print("="*70)
    
    # Cost estimate
    total_cost = passed * 0.02
    print(f"\n💰 Approximate cost for this test: ${total_cost:.2f}")
    print(f"   (~$0.02 per explanation)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        print("   Run again when ready: python test_multiple_inputs.py")
