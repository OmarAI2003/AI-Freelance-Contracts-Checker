"""Demo script to test Negotiation Agent functionality"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents.negotiation.agent import NegotiationAgent

def main():
    print("🤖 Initializing Contract Negotiation Agent...")
    agent = NegotiationAgent()
    
    while True:
        print("\n=== Contract Negotiation Agent ===")
        print("1. 📊 Analyze Contract")
        print("2. 📑 Explain Terms")
        print("3. 💼 Negotiate Terms")
        print("4. ⚖️ Legal Action")
        print("5. Exit")
        
        choice = input("\nChoose an option (1-5): ")
        
        if choice == "1":
            print("\n=== Contract Analysis ===")
            contract = input("Enter the contract text to analyze:\n")
            result = agent.analyze_contract(contract)
            print("\n📊 Analysis:")
            print(result["analysis"])
            
        elif choice == "2":
            print("\n=== Explain Terms ===")
            terms = input("Enter the legal terms you want explained:\n")
            explanation = agent.explain_terms(terms)
            print("\n📑 Explanation:")
            print(explanation)
            
        elif choice == "3":
            print("\n=== Negotiate Terms ===")
            current = input("Enter current terms:\n")
            print("\nWhat changes would you like? (enter one per line, blank line to finish)")
            changes = []
            while True:
                change = input()
                if not change:
                    break
                changes.append(change)
            
            context = {
                "experience": input("\nYears of experience: "),
                "role": input("Your role: "),
                "location": input("Your location: ")
            }
            
            result = agent.negotiate_terms(current, changes, context)
            print("\n💼 Negotiation Strategy:")
            print(result["strategy"])
            
        elif choice == "4":
            print("\n=== Legal Action ===")
            contract = input("Enter the contract text:\n")
            question = input("\nWhat legal question do you have?\n")
            advice = agent.get_legal_advice(contract, question)
            print("\n⚖️ Legal Analysis:")
            print(advice)
            
        elif choice == "5":
            print("\nThank you for using Contract Negotiation Agent!")
            break
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()