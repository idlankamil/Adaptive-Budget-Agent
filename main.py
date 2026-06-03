"""
Adaptive Budget Optimization Agent - Phase 3 Implementation
=============================================================
BAXI 3113 - Intelligent Agent
Group Project - Phase 3

PROJECT: Adaptive Budget Optimization Agent for Malaysian Students
FRAMEWORK: LangGraph (Stateful Graph-Based Agent Workflow)
ARCHITECTURE: Hybrid BDI (Belief-Desire-Intention) Model

This implementation demonstrates autonomous budget monitoring and
optimization for university students in Malaysia, addressing the
problem identified in Phase 1: students struggling with limited
budgets across academic, daily, and social expenses.

The agent uses LangGraph's state management to track spending over
time and makes intelligent reallocation decisions when overspending
occurs, preventing "budget fatigue" and maintaining financial health.
"""

import os

# REPLACE 'AIzaSy...' WITH YOUR ACTUAL LONG KEY
os.environ["GEMINI_API_KEY"] = "INSERT API KEY"


import json
from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import (
    monitor_spending,
    evaluate_status,
    reoptimize_budget,
    generate_guidance
)


def load_initial_config():
    """
    Helper function to load static budget rules from JSON configuration.
    
    This represents the "initial desires" of the agent - the budget
    goals that the student wants to achieve each month.
    
    Returns:
        dict: Budget rules with limits and category types
    """
    try:
        with open("data/budget_rules.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: budget_rules.json not found in data folder!")
        return {}


def build_agent_workflow():
    """
    Constructs the LangGraph workflow implementing the BDI architecture.
    
    WORKFLOW STRUCTURE:
    -------------------
    1. PERCEPTION NODE → Senses environment (reads transactions)
    2. REASONING NODE → Evaluates beliefs vs desires (checks budget status)
    3. CONDITIONAL ROUTING:
       - If CRITICAL → Go to PLANNING NODE (re-optimize)
       - If WARNING/ON_TRACK → Skip to EFFECTOR NODE (just inform)
    4. PLANNING NODE → Formulates intentions (reallocation plan)
    5. EFFECTOR NODE → Executes actions (generates guidance)
    6. END
    
    This structure directly implements the "Behavior Flowchart" and
    "Information Module Flow Diagram" from Phase 2 design.
    
    Returns:
        Compiled LangGraph application
    """
    # Initialize StateGraph with our BDI state structure
    workflow = StateGraph(AgentState)
    
    # === ADD NODES (BDI Components) ===
    workflow.add_node("perception", monitor_spending)
    workflow.add_node("reasoning", evaluate_status)
    workflow.add_node("planning", reoptimize_budget)
    workflow.add_node("effector", generate_guidance)
    
    # === DEFINE WORKFLOW EDGES ===
    # Set entry point (agent always starts by perceiving environment)
    workflow.set_entry_point("perception")
    
    # Linear flow: Perception → Reasoning
    workflow.add_edge("perception", "reasoning")
    
    # === CONDITIONAL ROUTING (The "Intelligence") ===
    # This is where the agent makes decisions based on reasoning results
    def route_based_on_status(state):
        """
        Decision function implementing intelligent routing.
        
        Logic:
        - CRITICAL status triggers re-optimization (PLANNING node)
        - WARNING/ON_TRACK status skips to communication (EFFECTOR node)
        
        This prevents unnecessary computation and implements the
        "Re-optimize" vs "Just Alert" logic from Phase 2.
        """
        if state["status"] == "critical":
            return "planning"  # Fix the problem
        else:
            return "effector"   # Just inform the user
    
    # Add conditional edge with routing logic
    workflow.add_conditional_edges(
        "reasoning",
        route_based_on_status,
        {
            "planning": "planning",
            "effector": "effector"
        }
    )
    
    # Complete the workflow
    workflow.add_edge("planning", "effector")  # After planning, communicate plan
    workflow.add_edge("effector", END)         # After communication, done
    
    # Compile the graph into executable application
    return workflow.compile()


def run_agent():
    """
    Main execution function - runs the complete agent cycle.
    
    This function:
    1. Loads initial budget configuration
    2. Builds the LangGraph workflow
    3. Initializes the agent state (empty beliefs)
    4. Executes the workflow (perception → reasoning → planning → effector)
    5. Displays final results
    """
    print("\n" + "="*60)
    print("🤖 ADAPTIVE BUDGET OPTIMIZATION AGENT")
    print("    Malaysian Student Financial Assistant")
    print("="*60)
    print("\nInitializing agent system...")
    
    # Load budget rules (the agent's "desires"/goals)
    budget_rules = load_initial_config()
    
    if not budget_rules:
        print("❌ Failed to load configuration. Exiting.")
        return
    
    # Build the LangGraph workflow
    agent_app = build_agent_workflow()
    print("✅ Agent workflow compiled successfully")
    
    # Initialize agent state (empty beliefs at start)
    initial_state = {
        "budget_rules": budget_rules,
        "current_expenses": {},
        "transaction_count": 0,
        "status": "unknown",
        "overspent_categories": [],
        "reallocation_plan": [],
        "final_message": "",
        "summary_report": {}
    }
    
    print("\n🚀 Starting agent execution...\n")
    
    # === EXECUTE THE AGENT ===
    # This runs the complete BDI cycle
    try:
        final_state = agent_app.invoke(initial_state)
        
        # === DISPLAY FINAL RESULTS ===
        print("\n" + "="*60)
        print("📊 AGENT EXECUTION COMPLETE")
        print("="*60)
        
        # Display summary statistics
        summary = final_state["summary_report"]
        print(f"\n📈 Budget Summary:")
        print(f"   • Total Budget: RM {summary['total_budget']:.2f}")
        print(f"   • Total Spent: RM {summary['total_spent']:.2f}")
        print(f"   • Remaining: RM {summary['remaining']:.2f}")
        print(f"   • Status: {summary['status'].upper()}")
        print(f"   • Transactions Analyzed: {summary['transactions_analyzed']}")
        
        # Display final message to user
        print(f"\n💬 Message to Student:")
        print("-" * 60)
        print(final_state["final_message"])
        print("-" * 60)
        
        # Display action plan if any
        if final_state["reallocation_plan"]:
            print(f"\n🔧 Actions Taken:")
            for i, step in enumerate(final_state["reallocation_plan"], 1):
                print(f"   {i}. {step}")
        
        print("\n✅ Agent execution successful!\n")
        
    except Exception as e:
        print(f"\n❌ ERROR during agent execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    Entry point for the application.
    
    To run this agent:
    1. Ensure all dependencies are installed: pip install -r requirements.txt
    2. Place your transaction data in data/transactions.csv
    3. (Optional) Set GEMINI_API_KEY environment variable for AI guidance
    4. Run: python main.py
    """
    run_agent()
