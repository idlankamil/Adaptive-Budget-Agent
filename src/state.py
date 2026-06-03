from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    BELIEFS (Knowledge Base) - BDI Architecture Component
    =====================================================
    Represents the agent's internal model of the student's financial world.
    This aligns with Phase 2 "Perception Layer" design.
    
    In Malaysian context:
    - All amounts are in Ringgit Malaysia (RM)
    - Categories use Bahasa terms (Makanan, Pengangkutan, etc.)
    - Budget limits reflect typical PTPTN/parental allowance amounts
    """
    
    # Static configuration (loaded from JSON)
    budget_rules: Dict[str, Any]  # Category limits and types
    
    # Dynamic beliefs (perceived from transactions)
    current_expenses: Dict[str, float]  # Actual spending per category
    transaction_count: int  # Number of transactions processed
    
    # DESIRES (Goals Assessment) - BDI Architecture Component
    # The agent's evaluation of whether goals are being met
    status: str  # "on_track", "warning", "critical"
    overspent_categories: List[str]  # Which categories violated limits
    
    # INTENTIONS (Action Plans) - BDI Architecture Component
    # Concrete plans formulated to address critical situations
    reallocation_plan: List[str]  # Steps to rebalance budget
    
    # EFFECTOR OUTPUT - BDI Architecture Component
    # Final communication to the user
    final_message: str
    summary_report: Dict[str, Any]  # Detailed breakdown for logging
