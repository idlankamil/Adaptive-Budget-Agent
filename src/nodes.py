"""
BDI Agent Implementation - Node Functions
==========================================
This module implements the four core components of the BDI architecture:
1. PERCEPTION: Sensing the environment (CSV transaction data)
2. REASONING: Evaluating beliefs against desires (budget goals)
3. PLANNING: Formulating intentions (re-optimization strategies)
4. EFFECTOR: Executing actions (generating user guidance)

Designed for Malaysian student budget management context.
"""

import pandas as pd
import google.generativeai as genai
from typing import Dict
import os

# ============================================================================
# 1. PERCEPTION LAYER - BDI Component
# ============================================================================
def monitor_spending(state: Dict) -> Dict:
    """
    PERCEPTION: Senses the financial environment.
    
    Function: Reads transaction data from CSV (simulated bank feed) and
    aggregates spending by category. This updates the agent's BELIEFS
    about the current state of the student's budget.
    
    Malaysian Context:
    - Reads local transaction descriptions (Mamak, Grab, GSC, etc.)
    - Processes amounts in RM
    - Handles common Malaysian spending categories
    
    Returns:
        Updated state with current_expenses and transaction_count
    """
    print("\n" + "="*60)
    print("🔍 [PERCEPTION LAYER] Monitoring Student Spending")
    print("="*60)
    
    try:
        # Load transaction data
        df = pd.read_csv("data/transactions.csv")
        print(f"📄 Loaded {len(df)} transactions from bank feed")
        
        # Aggregate spending by category
        spending_summary = df.groupby("category")["amount"].sum().to_dict()
        
        # Ensure all defined categories exist (even if RM 0 spending)
        for category in state["budget_rules"]:
            if category not in spending_summary:
                spending_summary[category] = 0.0
        
        # Display perception results
        print("\n📊 Detected Spending Pattern:")
        for cat, amount in spending_summary.items():
            print(f"   • {cat}: RM {amount:.2f}")
        
        return {
            "current_expenses": spending_summary,
            "transaction_count": len(df)
        }
        
    except FileNotFoundError:
        print("❌ ERROR: transactions.csv not found!")
        return {"current_expenses": {}, "transaction_count": 0}


# ============================================================================
# 2. REASONING ENGINE - BDI Component (DESIRES)
# ============================================================================
def evaluate_status(state: Dict) -> Dict:
    """
    REASONING: Evaluates BELIEFS against DESIRES (goals).
    
    Function: Checks if current spending (beliefs) aligns with budget goals
    (desires). Uses Malaysian student budget thresholds:
    - Critical: Spending > 100% of limit (immediate action needed)
    - Warning: Spending > 80% of limit (caution advised)
    - On Track: Within safe spending range
    
    This implements the "Reasoning Engine" from Phase 2 design.
    
    Returns:
        Updated state with status and overspent_categories
    """
    print("\n" + "="*60)
    print("🧠 [REASONING ENGINE] Evaluating Budget Status")
    print("="*60)
    
    rules = state["budget_rules"]
    expenses = state["current_expenses"]
    
    overall_status = "on_track"
    overspent_cats = []
    
    print("\n📋 Category Analysis:")
    for cat, rule in rules.items():
        limit = rule["limit"]
        spent = expenses.get(cat, 0)
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        # Evaluate against thresholds
        if spent > limit:
            status_icon = "🔴"
            status_text = "CRITICAL - OVER BUDGET"
            overall_status = "critical"
            overspent_cats.append(cat)
        elif spent >= (limit * 0.8):
            status_icon = "🟡"
            status_text = "WARNING - APPROACHING LIMIT"
            if overall_status != "critical":
                overall_status = "warning"
        else:
            status_icon = "🟢"
            status_text = "On Track"
        
        print(f"\n   {status_icon} {cat} ({rule['type'].upper()})")
        print(f"      Spent: RM {spent:.2f} / RM {limit:.2f} ({percentage:.1f}%)")
        print(f"      Status: {status_text}")
    
    print(f"\n🎯 Overall Assessment: {overall_status.upper()}")
    if overspent_cats:
        print(f"⚠️  Overspent Categories: {', '.join(overspent_cats)}")
    
    return {
        "status": overall_status,
        "overspent_categories": overspent_cats
    }


# ============================================================================
# 3. PLANNING LAYER - BDI Component (INTENTIONS)
# ============================================================================
def reoptimize_budget(state: Dict) -> Dict:
    """
    INTENTIONS: Formulates concrete plans to address critical status.
    
    Function: Implements the "Re-optimization" strategy from Phase 2.
    When a NEED category exceeds its limit, the agent plans to shift
    funds from WANT categories that have surplus.
    
    Strategy: "Just Enough" reallocation
    - Calculate exact deficit in overspent category
    - Find WANT categories with available surplus
    - Transfer minimum necessary amount to cover deficit
    
    This prevents budget collapse and maintains student well-being by
    prioritizing needs (Makanan, Pengangkutan) over wants (Hiburan).
    
    Returns:
        Updated state with reallocation_plan
    """
    print("\n" + "="*60)
    print("🔧 [PLANNING LAYER] Formulating Re-optimization Plan")
    print("="*60)
    
    rules = state["budget_rules"]
    expenses = state["current_expenses"].copy()  # Work with copy
    overspent = state["overspent_categories"]
    plan = []
    
    print("\n🎯 Applying 'Just Enough' Reallocation Strategy:")
    
    for bad_cat in overspent:
        # Calculate exact deficit
        deficit = expenses[bad_cat] - rules[bad_cat]["limit"]
        print(f"\n   ⚠️  {bad_cat} deficit: RM {deficit:.2f}")
        
        # Search for surplus in WANT categories
        for donor_cat, rule in rules.items():
            if rule["type"] == "want" and deficit > 0:
                donor_spent = expenses.get(donor_cat, 0)
                donor_limit = rule["limit"]
                surplus = donor_limit - donor_spent
                
                if surplus > 0:
                    # Take only what's needed (or what's available)
                    amount_to_take = min(deficit, surplus)
                    
                    plan.append(
                        f"Transfer RM {amount_to_take:.2f} from "
                        f"{donor_cat} to {bad_cat}"
                    )
                    
                    print(f"   ✅ Found surplus in {donor_cat}: RM {surplus:.2f}")
                    print(f"      → Transferring RM {amount_to_take:.2f}")
                    
                    # Update virtual balances
                    deficit -= amount_to_take
                    expenses[donor_cat] += amount_to_take
        
        # If still can't cover deficit
        if deficit > 0.01:  # Small tolerance for floating point
            plan.append(
                f"⚠️  {bad_cat}: Unable to fully cover deficit. "
                f"Remaining: RM {deficit:.2f}. "
                f"Consider reducing spending in this category."
            )
            print(f"   ⚠️  Remaining uncovered: RM {deficit:.2f}")
    
    if not plan:
        plan.append("No reallocation needed - all wants have been spent.")
    
    return {"reallocation_plan": plan}


# ============================================================================
# 4. EFFECTOR LAYER - BDI Component
# ============================================================================
def generate_guidance(state: Dict) -> Dict:
    """
    EFFECTORS: Executes actions by communicating with the user.
    
    Function: Uses Google Gemini AI to generate natural, friendly advice
    in Malaysian English context. Converts technical budget data into
    conversational guidance that Malaysian students can understand.
    
    This implements the "Gemini Integration" feature from Phase 2 design,
    making financial advice accessible and non-intimidating.
    
    Returns:
        Updated state with final_message and summary_report
    """
    print("\n" + "="*60)
    print("💬 [EFFECTOR LAYER] Generating Student Guidance")
    print("="*60)
    
    status = state["status"]
    expenses = state["current_expenses"]
    rules = state["budget_rules"]
    plan = state.get("reallocation_plan", [])
    
    # Prepare summary report
    total_budget = sum(r["limit"] for r in rules.values())
    total_spent = sum(expenses.values())
    
    summary = {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": total_budget - total_spent,
        "status": status,
        "transactions_analyzed": state.get("transaction_count", 0)
    }
    
    # === GEMINI AI INTEGRATION ===
    # Configure Gemini (use environment variable for API key)
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Build prompt with Malaysian context
            prompt = f"""
You are a friendly budget assistant helping a Malaysian university student manage their money.

CURRENT SITUATION:
- Budget Status: {status.upper()}
- Total Monthly Budget: RM {total_budget:.2f}
- Total Spent So Far: RM {total_spent:.2f}
- Remaining: RM {summary['remaining']:.2f}

SPENDING BREAKDOWN:
{chr(10).join(f"- {cat}: RM {amt:.2f} / RM {rules[cat]['limit']:.2f}" for cat, amt in expenses.items())}

RE-OPTIMIZATION PLAN:
{chr(10).join(plan) if plan else "No plan needed."}

TASK: Write a short, friendly 3-4 sentence message in Malaysian English style. 
- Address the student directly ("you")
- Use casual but respectful tone
- If status is critical, explain the reallocation plan simply
- If status is warning, give gentle reminder
- If on track, give encouragement
- Use Malaysian context (mamak, Grab, etc. are normal terms)

Message:"""
            
            response = model.generate_content(prompt)
            message = response.text
            print(f"\n🤖 AI-Generated Advice:\n{message}")
            
        except Exception as e:
            print(f"\n⚠️  Gemini API Error: {e}")
            message = generate_fallback_message(status, summary, plan)
    else:
        # Fallback if no API key
        print("\n📝 Using fallback message (no Gemini API key detected)")
        message = generate_fallback_message(status, summary, plan)
    
    return {
        "final_message": message,
        "summary_report": summary
    }


def generate_fallback_message(status: str, summary: Dict, plan: list) -> str:
    """
    Fallback message generator if Gemini API is unavailable.
    Uses rule-based templates with Malaysian context.
    """
    if status == "critical":
        msg = (
            f"⚠️ Eh, you've overspent this month! You used RM {summary['total_spent']:.2f} "
            f"out of your RM {summary['total_budget']:.2f} budget. "
            f"I've adjusted your plan: {plan[0] if plan else 'No reallocation possible'}. "
            f"Try to control your spending for the rest of the month, okay?"
        )
    elif status == "warning":
        msg = (
            f"🟡 Careful ah! You're approaching your budget limit. "
            f"Spent RM {summary['total_spent']:.2f} / RM {summary['total_budget']:.2f} already. "
            f"Maybe skip that bubble tea for a few days? 😅"
        )
    else:
        msg = (
            f"🎉 Good job! You're managing your budget well so far. "
            f"Spent RM {summary['total_spent']:.2f} / RM {summary['total_budget']:.2f}. "
            f"Keep it up and you'll have money left for raya shopping! 💪"
        )
    
    return msg
