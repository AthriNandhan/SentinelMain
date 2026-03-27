from langgraph.graph import StateGraph, END
from app.models.state import RemediationState
from app.agents.red_agent import red_agent
from app.agents.blue_agent import blue_agent
from app.agents.green_agent import green_agent

def decide_next_node_after_red(state: RemediationState):
    """
    Decide whether to proceed to Blue Agent or end workflow based on exploit success checklist.
    """
    if any(state.vulnerability_checklist.values()):
        return "blue_agent"
    return END

def decide_next_node_after_green(state: RemediationState):
    """
    Decide whether to loop back to Blue Agent or end workflow based on verification status.
    """
    if state.verification_status == "PASS":
        return END
    
    if state.iteration_count < state.max_iterations:
        return "blue_agent"
    
    return END

# Initialize Graph
workflow = StateGraph(RemediationState)

# Add Nodes
workflow.add_node("red_agent", red_agent)
workflow.add_node("blue_agent", blue_agent)
workflow.add_node("green_agent", green_agent)

# Set Entry Point
workflow.set_entry_point("red_agent")

# Add Conditional Edges
workflow.add_conditional_edges(
    "red_agent",
    decide_next_node_after_red,
    {
        "blue_agent": "blue_agent",
        END: END
    }
)

workflow.add_edge("blue_agent", "green_agent")

workflow.add_conditional_edges(
    "green_agent",
    decide_next_node_after_green,
    {
        "blue_agent": "blue_agent",
        END: END
    }
)

# Compile Graph
app = workflow.compile()
