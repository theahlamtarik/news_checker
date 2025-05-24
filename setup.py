#!/usr/bin/env python3
"""
Gaza Media Fact-Check Multi-Agent System Setup
Runs both the fact-checking agent and Twitter agent with A2A communication
"""

import subprocess
import time
import requests
import json
import threading
import sys
import os

def start_fact_check_agent():
    """Start the fact-checking agent on port 5000"""
    print("🚀 Starting Fact-Check Agent on port 5000...")
    return subprocess.Popen([
        sys.executable, "app.py"
    ], cwd=".")

def start_twitter_agent():
    """Start the Twitter agent on port 5001"""
    print("🐦 Starting Twitter Agent on port 5001...")
    return subprocess.Popen([
        sys.executable, "twitter_agent.py" 
    ], cwd=".")

def wait_for_service(url, service_name, max_retries=30):
    """Wait for a service to become available"""
    print(f"⏳ Waiting for {service_name} to start...")
    
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.Timeout:
            pass
        
        time.sleep(2)
        print(f"   Attempt {i+1}/{max_retries}...")
    
    print(f"❌ {service_name} failed to start after {max_retries * 2} seconds")
    return False

def test_a2a_communication():
    """Test A2A communication between agents"""
    print("\n🔗 Testing A2A Communication...")
    
    # Test fact-check agent status
    try:
        fact_check_status = requests.get("http://localhost:5000/a2a/status").json()
        print(f"✅ Fact-Check Agent: {fact_check_status['agent_name']} ({fact_check_status['status']})")
    except Exception as e:
        print(f"❌ Fact-Check Agent A2A test failed: {e}")
        return False
    
    # Test Twitter agent status
    try:
        twitter_status = requests.get("http://localhost:5001/a2a/status").json()
        print(f"✅ Twitter Agent: {twitter_status['agent_name']} ({twitter_status['status']})")
    except Exception as e:
        print(f"❌ Twitter Agent A2A test failed: {e}")
        return False
    
    return True

def run_sample_analysis():
    """Run a sample analysis to demonstrate A2A communication"""
    print("\n📊 Running Sample Analysis with A2A Communication...")
    
    try:
        # Trigger analysis via A2A endpoint
        response = requests.post("http://localhost:5000/a2a/trigger_analysis", json={
            "western_query": "Gaza hospital strike",
            "arabic_query": "قصف مستشفى غزة"
        }, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis completed!")
            print(f"   Status: {result['status']}")
            print(f"   Contradictions found: {result.get('contradictions_found', 0)}")
            print(f"   Twitter notified: {result.get('twitter_notified', False)}")
            
            if result.get('contradictions_found', 0) > 0:
                print("🚨 Contradictions detected - Twitter agent should create threads!")
            
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Sample analysis failed: {e}")
        return False

def show_dashboard_info():
    """Show information about accessing the system"""
    print(f"""
🎯 SYSTEM READY! Your Multi-Agent Gaza Fact-Check System is running:

📊 FACT-CHECK AGENT (Port 5000):
   Web Dashboard: http://localhost:5000
   API Endpoint:  http://localhost:5000/api/analyze
   A2A Status:    http://localhost:5000/a2a/status
   Health Check:  http://localhost:5000/api/health

🐦 TWITTER AGENT (Port 5001):
   A2A Status:    http://localhost:5001/a2a/status
   Message Queue: http://localhost:5001/a2a/receive

🔗 A2A COMMUNICATION:
   ✅ Agents can communicate automatically
   ✅ Contradictions trigger Twitter threads
   ✅ Real-time fact-checking pipeline

🚀 USAGE:
   1. Visit http://localhost:5000 for the main dashboard
   2. Run analysis on Gaza media coverage
   3. When contradictions are found, Twitter agent auto-creates threads
   4. Check Twitter agent logs for thread creation status

⚠️  TWITTER SETUP REQUIRED:
   - Add your Twitter API keys to twitter_agent.py
   - Set dry_run=False to actually post tweets
   - Current mode: SIMULATION ONLY

Press Ctrl+C to stop both agents.
""")

def main():
    """Main setup function"""
    print("🚀 Gaza Media Fact-Check Multi-Agent System")
    print("=" * 50)
    
    processes = []
    
    try:
        # Start fact-check agent
        fact_check_process = start_fact_check_agent()
        processes.append(fact_check_process)
        
        # Wait for fact-check agent to be ready
        if not wait_for_service("http://localhost:5000/api/health", "Fact-Check Agent"):
            return
        
        # Start Twitter agent
        twitter_process = start_twitter_agent()
        processes.append(twitter_process)
        
        # Wait for Twitter agent to be ready
        if not wait_for_service("http://localhost:5001/a2a/status", "Twitter Agent"):
            return
        
        # Test A2A communication
        if not test_a2a_communication():
            print("⚠️ A2A communication test failed, but system may still work")
        
        # Run sample analysis
        print("\n🎯 System is ready! Running sample analysis...")
        time.sleep(2)
        run_sample_analysis()
        
        # Show dashboard information
        show_dashboard_info()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down agents...")
        
        for process in processes:
            process.terminate()
            
        # Wait for processes to end
        for process in processes:
            process.wait()
        
        print("✅ All agents stopped successfully")

if __name__ == "__main__":
    main()