import sys
from agent.agent import PredictiveCybercrimeAgent

def main():
    print("==================================================")
    print("  Predictive Cybercrime Intelligence Agent CLI    ")
    print("==================================================")
    
    case_id = input("\nEnter Case ID [default: CASE-001]: ").strip()
    if not case_id:
        case_id = "CASE-001"
        
    print(f"\n[CASE]\n{case_id}\n")
    
    agent = PredictiveCybercrimeAgent()
    try:
        agent.run(case_id)
    except Exception as e:
        print(f"\n[ERROR] Investigation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
