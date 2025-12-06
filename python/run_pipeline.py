"""
Complete pipeline orchestrator for Atomberg SOV Analysis
Runs all agents in sequence with proper error handling
"""

import subprocess
import sys
from pathlib import Path
import time

def run_agent(agent_path, agent_name):
    """Run a single agent and return success status"""
    print(f"\n{'='*60}")
    print(f"🚀 Running {agent_name}...")
    print(f"{'='*60}\n")
    
    # Get absolute path
    abs_path = Path.cwd() / agent_path
    
    try:
        result = subprocess.run(
            [sys.executable, str(abs_path)],
            cwd=abs_path.parent,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {agent_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {agent_name} failed with error!")
        return False
    except FileNotFoundError:
        print(f"\n❌ Agent file not found: {abs_path}")
        return False

def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     ATOMBERG SHARE OF VOICE ANALYTICS PIPELINE       ║
    ║              Multi-Agent System v2.0                  ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    start_time = time.time()
    
    # Define all agents
    agents = [
        {
            'path': Path('Search_retrieval/search_agents/search_agent.py'),
            'name': 'Search Agent (50 results/keyword)',
            'description': 'Fetches data from Google & YouTube'
        },
        {
            'path': Path('Brand/agents/brand_agent.py'),
            'name': 'Brand Classification Agent',
            'description': 'Identifies Atomberg vs competitors'
        },
        {
            'path': Path('sentiment/agents/sentiment_agent.py'),
            'name': 'Sentiment Analysis Agent',
            'description': 'Analyzes sentiment & engagement'
        },
        {
            'path': Path('SOV/metrics_agent.py'),
            'name': 'SOV Metrics Agent',
            'description': 'Calculates Share of Voice metrics'
        },
        {
            'path': Path('insights/agents/insights_agent.py'),
            'name': 'Insights Generator Agent',
            'description': 'Generates recommendations'
        }
    ]
    
    # Run all agents
    results = []
    for i, agent in enumerate(agents, 1):
        print(f"\n📍 Step {i}/{len(agents)}: {agent['description']}")
        
        if not agent['path'].exists():
            print(f"❌ Agent file not found: {agent['path']}")
            results.append(False)
            continue
        
        success = run_agent(agent['path'], agent['name'])
        results.append(success)
        
        if not success:
            print(f"\n⚠️  Pipeline stopped at {agent['name']}")
            print("   Please fix the error and run again.")
            return
        
        time.sleep(1)  # Brief pause between agents
    
    # Summary
    elapsed_time = time.time() - start_time
    print(f"\n{'='*60}")
    print("📊 PIPELINE EXECUTION SUMMARY")
    print(f"{'='*60}")
    
    for i, (agent, success) in enumerate(zip(agents, results), 1):
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{i}. {agent['name']}: {status}")
    
    print(f"\n⏱️  Total execution time: {elapsed_time:.2f} seconds")
    
    if all(results):
        print("\n🎉 All agents completed successfully!")
        print("\n📊 Next step: Run the dashboard")
        print("   Command: streamlit run dashboard.py")
    else:
        print("\n⚠️  Some agents failed. Please check the errors above.")

if __name__ == "__main__":
    main()
