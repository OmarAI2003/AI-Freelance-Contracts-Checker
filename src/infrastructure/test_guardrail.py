#!/usr/bin/env python3
"""
Test script for ContractGuard Guardrail System
"""

import json
import os
from typing import Dict, List, Any
from guardrail_integration import ContractGuardGuardrail, GuardrailAction

class GuardrailTester:
    def __init__(self):
        info_path = os.path.join(os.path.dirname(__file__), 'guardrail_info.json')
        if os.path.exists(info_path):
            with open(info_path) as f:
                info = json.load(f)
                self.guardrail_id = info['guardrail_id']
                self.version = info['version']
        else:
            self.guardrail_id = "test-guardrail-id"
            self.version = "1"
        
        self.guardrail = ContractGuardGuardrail(self.guardrail_id, self.version)
    
    def run_all_tests(self):
        print("ContractGuard Guardrail Test Suite")
        print("=" * 50)
        
        test_results = []
        test_results.extend(self.test_agent_specific_rules())
        test_results.extend(self.test_legal_disclaimers())
        
        self.print_test_summary(test_results)
        return test_results
    
    def test_agent_specific_rules(self) -> List[Dict[str, Any]]:
        print("\nTesting Agent-Specific Rules...")
        
        test_cases = [
            {
                "name": "Analysis agent - technical language OK",
                "input": "The indemnification clause creates potential liability exposure.",
                "expected": GuardrailAction.ALLOW,
                "agent_type": "analysis"
            },
            {
                "name": "Explanation agent - too technical",
                "input": "The aforementioned indemnification provisions notwithstanding heretofore established precedents.",
                "expected": GuardrailAction.FLAG,
                "agent_type": "explanation"
            },
            {
                "name": "Negotiation agent - collaborative language",
                "input": "We could explore alternative terms that work for both parties.",
                "expected": GuardrailAction.ALLOW,
                "agent_type": "negotiation"
            },
            {
                "name": "Negotiation agent - aggressive language",
                "input": "This is our final offer, take it or leave it.",
                "expected": GuardrailAction.BLOCK,
                "agent_type": "negotiation"
            }
        ]
        
        results = []
        for case in test_cases:
            try:
                result = self.guardrail._validate_agent_specific(case["input"], case["agent_type"])
                passed = result.action == case["expected"]
                
                results.append({
                    "test": case["name"],
                    "passed": passed,
                    "expected": case["expected"].value,
                    "actual": result.action.value
                })
                
                status = "PASS" if passed else "FAIL"
                print(f"  {status} {case['name']}")
                
            except Exception as e:
                results.append({
                    "test": case["name"],
                    "passed": False,
                    "error": str(e)
                })
                print(f"  ERROR {case['name']}: {e}")
        
        return results
    
    def test_legal_disclaimers(self) -> List[Dict[str, Any]]:
        print("\nTesting Legal Disclaimers...")
        
        test_cases = [
            {
                "name": "Legal content needs disclaimer",
                "input": "This contract clause may violate employment law in your jurisdiction.",
                "should_add_disclaimer": True,
                "agent_type": "explanation"
            },
            {
                "name": "Already has disclaimer",
                "input": "This analysis is for informational purposes only and does not constitute legal advice.",
                "should_add_disclaimer": False,
                "agent_type": "explanation"
            },
            {
                "name": "Non-legal content",
                "input": "The payment terms specify net 30 days from invoice date.",
                "should_add_disclaimer": False,
                "agent_type": "analysis"
            }
        ]
        
        results = []
        for case in test_cases:
            try:
                result = self.guardrail._validate_output_specific(case["input"], case["agent_type"])
                
                has_disclaimer = result.filtered_content and result.filtered_content != case["input"]
                passed = has_disclaimer == case["should_add_disclaimer"]
                
                results.append({
                    "test": case["name"],
                    "passed": passed,
                    "expected_disclaimer": case["should_add_disclaimer"],
                    "has_disclaimer": has_disclaimer,
                    "action": result.action.value
                })
                
                status = "PASS" if passed else "FAIL"
                print(f"  {status} {case['name']}")
                
            except Exception as e:
                results.append({
                    "test": case["name"],
                    "passed": False,
                    "error": str(e)
                })
                print(f"  ERROR {case['name']}: {e}")
        
        return results
    
    def print_test_summary(self, results: List[Dict[str, Any]]):
        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("passed", False))
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in results:
                if not result.get("passed", False):
                    print(f"  - {result['test']}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")

def main():
    tester = GuardrailTester()
    results = tester.run_all_tests()
    
    results_path = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to: {results_path}")

if __name__ == '__main__':
    main()