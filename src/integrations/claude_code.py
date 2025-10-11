from typing import Any

from claude_agent_sdk import query
from claude_agent_sdk.types import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
)


def format_requirement(req: dict[str, Any], idx: int) -> str:
    """Format a Requirement document into readable text.

    Args:
        req: Requirement document from the database
        idx: Index/number for this requirement

    Returns:
        Formatted string representation of the requirement
    """
    text = f"\n## Requirement {idx}:\n"
    text += f"- Priority: {req.get('priority', 'N/A')}\n"
    text += f"- Component: {req.get('component', 'N/A')}\n"
    text += f"- User Story: {req.get('user_story', 'N/A')}\n"
    text += f"- Acceptance Criteria: {req.get('acceptance', 'N/A')}\n"
    return text


def format_adr(adr: dict[str, Any]) -> str:
    """Format an ADR (Architecture Decision Record) into readable text.

    Args:
        adr: ADR section from a Plan document

    Returns:
        Formatted string representation of the ADR
    """
    text = "\n### Architecture Decision Record (ADR):\n"
    text += f"- Status: {adr.get('status', 'N/A')}\n"
    text += f"- Date: {adr.get('date', 'N/A')}\n"
    text += f"- Decision: {adr.get('decision', 'N/A')}\n"
    text += f"- Context: {adr.get('context', 'N/A')}\n"
    text += f"- Consequences: {adr.get('consequences', 'N/A')}\n"
    return text


def format_design_high(design_high: dict[str, Any]) -> str:
    """Format a DesignHigh section into readable text.

    Args:
        design_high: DesignHigh section from a Plan document

    Returns:
        Formatted string representation of the high-level design
    """
    text = "\n### High-Level Design:\n"
    text += f"- Components: {', '.join(design_high.get('components', []))}\n"
    text += f"- Dependencies: {', '.join(design_high.get('dependencies', []))}\n"
    return text


def format_design_low(design_low: dict[str, Any]) -> str:
    """Format a DesignLow section into readable text.

    Args:
        design_low: DesignLow section from a Plan document

    Returns:
        Formatted string representation of the low-level design
    """
    text = "\n### Low-Level Design:\n"
    text += f"- Module: {design_low.get('module', 'N/A')}\n"
    text += f"- Interface: {design_low.get('interface', 'N/A')}\n"
    text += f"- Data Flows: {design_low.get('data_flows', 'N/A')}\n"
    return text


def format_threat(threat: dict[str, Any]) -> str:
    """Format a Threat section into readable text.

    Args:
        threat: Threat section from a Plan document

    Returns:
        Formatted string representation of the threat analysis
    """
    text = "\n### Security/Reliability Threats:\n"
    text += f"- Risk Level: {threat.get('risk_level', 'N/A')}\n"
    text += f"- Component: {threat.get('component', 'N/A')}\n"
    text += f"- Mitigation: {threat.get('mitigation', 'N/A')}\n"
    return text


def format_plan(plan: dict[str, Any], idx: int) -> str:
    """Format a Plan document into readable text.

    Args:
        plan: Plan document from the database
        idx: Index/number for this plan

    Returns:
        Formatted string representation of the plan
    """
    text = f"\n## Plan {idx}:\n"

    if "adr" in plan:
        text += format_adr(plan["adr"])

    if "design_high" in plan:
        text += format_design_high(plan["design_high"])

    if "design_low" in plan:
        text += format_design_low(plan["design_low"])

    if "threat" in plan:
        text += format_threat(plan["threat"])

    return text


def format_test_case(test_case: dict[str, Any]) -> str:
    """Format a TestCase into readable text.

    Args:
        test_case: TestCase from a TestSpec

    Returns:
        Formatted string representation of the test case
    """
    text = f"  - {test_case.get('name', 'N/A')}\n"
    text += f"    Description: {test_case.get('description', 'N/A')}\n"
    text += f"    Type: {test_case.get('type', 'N/A')}\n"
    text += f"    Priority: {test_case.get('priority', 'N/A')}\n"
    return text


def format_test_spec(test_spec: dict[str, Any]) -> str:
    """Format a TestSpec section into readable text.

    Args:
        test_spec: TestSpec section from a Tasks document

    Returns:
        Formatted string representation of the test specification
    """
    text = "\n### Test Specification:\n"
    text += f"- Scope: {test_spec.get('scope', 'N/A')}\n"
    text += f"- Method: {test_spec.get('method', 'N/A')}\n"
    text += f"- Coverage Target: {test_spec.get('coverage_target', 'N/A')}\n"

    if test_spec.get("tools"):
        text += f"- Tools: {', '.join(test_spec['tools'])}\n"

    if test_spec.get("preconditions"):
        text += f"- Preconditions:\n"
        for precond in test_spec["preconditions"]:
            text += f"  - {precond}\n"

    if test_spec.get("success_criteria"):
        text += f"- Success Criteria:\n"
        for criteria in test_spec["success_criteria"]:
            text += f"  - {criteria}\n"

    if test_spec.get("test_cases"):
        text += f"- Test Cases:\n"
        for test_case in test_spec["test_cases"]:
            text += format_test_case(test_case)

    return text


def format_exec_spec(exec_spec: dict[str, Any]) -> str:
    """Format an ExecSpec section into readable text.

    Args:
        exec_spec: ExecSpec section from a Task

    Returns:
        Formatted string representation of the execution specification
    """
    text = "\n  Execution Specification:\n"
    text += f"  - Working Directory: {exec_spec.get('working_dir', 'N/A')}\n"
    text += f"  - Approval Required: {exec_spec.get('approval_required', 'N/A')}\n"

    if exec_spec.get("commands"):
        text += f"  - Allowed Commands:\n"
        for cmd in exec_spec["commands"]:
            text += f"    - {cmd}\n"

    if exec_spec.get("artifacts"):
        text += f"  - Expected Artifacts:\n"
        for artifact in exec_spec["artifacts"]:
            text += f"    - {artifact}\n"

    if exec_spec.get("env"):
        text += f"  - Required Environment Variables:\n"
        for env_var in exec_spec["env"]:
            text += f"    - {env_var}\n"

    if exec_spec.get("entry_task"):
        text += f"  - Entry Task: {exec_spec['entry_task']}\n"

    if exec_spec.get("constraints"):
        text += f"  - Constraints:\n"
        for constraint in exec_spec["constraints"]:
            text += f"    - {constraint}\n"

    return text


def format_task(task: dict[str, Any]) -> str:
    """Format a Task section into readable text.

    Args:
        task: Task section from a Tasks document

    Returns:
        Formatted string representation of the task
    """
    text = "\n### Task:\n"
    text += f"- Status: {task.get('status', 'N/A')}\n"
    text += f"- Component: {task.get('component', 'N/A')}\n"
    text += f"- Estimated Time: {task.get('est_time', 'N/A')}\n"

    if task.get("priority"):
        text += f"- Priority: {task['priority']}\n"

    if task.get("executor"):
        text += f"- Executor: {task['executor']}\n"

    if task.get("assignee"):
        text += f"- Assignee: {task['assignee']}\n"

    if task.get("dependencies"):
        text += f"- Dependencies: {', '.join(task['dependencies'])}\n"

    if task.get("blockers"):
        text += f"- Blockers:\n"
        for blocker in task["blockers"]:
            text += f"  - {blocker}\n"

    if task.get("acceptance_criteria"):
        text += f"- Acceptance Criteria:\n"
        for criteria in task["acceptance_criteria"]:
            text += f"  - {criteria}\n"

    if task.get("exec_spec"):
        text += format_exec_spec(task["exec_spec"])

    return text


def format_tasks(tasks: dict[str, Any], idx: int) -> str:
    """Format a Tasks document into readable text.

    Args:
        tasks: Tasks document from the database
        idx: Index/number for this tasks document

    Returns:
        Formatted string representation of the tasks document
    """
    text = f"\n## Tasks Document {idx}:\n"

    if "test_spec" in tasks:
        text += format_test_spec(tasks["test_spec"])

    if "task" in tasks:
        text += format_task(tasks["task"])

    return text


def _build_project_prompt(
    requirements: list[dict[str, Any]],
    plans: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    session_id: str,
) -> str:
    """Build a comprehensive prompt for Claude Code based on all documents.

    This is an internal function that formats the prompt text.

    Args:
        requirements: List of Requirement documents from the database
        plans: List of Plan documents from the database
        tasks: List of Tasks documents from the database
        session_id: The session ID linking all documents

    Returns:
        A formatted prompt string ready to be passed to Claude Code
    """
    prompt = f"""# Project Implementation Request

Session ID: {session_id}

You are tasked with implementing a complete project based on the requirements,
architectural plans, and task specifications provided below. Please implement
all the components, features, and tests as specified.

"""

    # Add Requirements section
    if requirements:
        prompt += "# Requirements\n"
        prompt += f"\nThis project has {len(requirements)} requirement(s):\n"
        for idx, req in enumerate(requirements, 1):
            prompt += format_requirement(req, idx)
    else:
        prompt += "# Requirements\n\nNo requirements specified.\n"

    # Add Plans section
    if plans:
        prompt += "\n\n# Architecture & Design Plans\n"
        prompt += f"\nThis project has {len(plans)} plan(s):\n"
        for idx, plan in enumerate(plans, 1):
            prompt += format_plan(plan, idx)
    else:
        prompt += "\n\n# Architecture & Design Plans\n\nNo plans specified.\n"

    # Add Tasks section
    if tasks:
        prompt += "\n\n# Implementation Tasks & Test Specifications\n"
        prompt += f"\nThis project has {len(tasks)} task set(s):\n"
        for idx, task_doc in enumerate(tasks, 1):
            prompt += format_tasks(task_doc, idx)
    else:
        prompt += (
            "\n\n# Implementation Tasks & Test Specifications\n\nNo tasks specified.\n"
        )

    # Add implementation instructions
    prompt += """

# Implementation Instructions

Based on the above requirements, architecture decisions, designs, and tasks:

1. Create all necessary project files and directory structure
2. Implement all components according to the design specifications
3. Follow the architecture decisions (ADRs) outlined in the plans
4. Address all security threats with the specified mitigations
5. Ensure all acceptance criteria are met
6. Follow the execution specifications provided in the tasks

Please proceed with the implementation, creating only the necessary application code
and configuration files as specified in the documents above.

If you need clarification on any requirements or design decisions, please ask
before proceeding with that particular component.
"""

    return prompt


async def generate_code(
    requirements: list[dict[str, Any]],
    plans: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    session_id: str,
    working_dir: str | None = None,
    cli_path: str | None = None,
) -> dict[str, Any]:
    """Generate code using Claude Agent SDK based on all documents.

    This function takes all the documents from a session (requirements, plans,
    and tasks), formats them into a comprehensive prompt, and then sends it
    to Claude Code for implementation using the Claude Agent SDK.

    The SDK connects to your local Claude Code CLI installation and uses your
    existing authentication. No API key is required.

    Args:
        requirements: List of Requirement documents from the database
        plans: List of Plan documents from the database
        tasks: List of Tasks documents from the database
        session_id: The session ID linking all documents
        working_dir: Optional working directory for the project
        cli_path: Optional path to the Claude Code CLI executable

    Returns:
        A dictionary containing the results:
        - "success": bool indicating if the operation was successful
        - "messages": list of all messages exchanged
        - "cost_usd": total cost in USD
        - "error": error message if any
        - "prompt": the generated prompt text
    """
    # Build the prompt
    prompt_text = _build_project_prompt(requirements, plans, tasks, session_id)

    # Set the system prompt for the agent
    system_prompt = """You are an agentic software engineer. Use the bash and text-editor tools to iteratively:
1) plan the minimal next change,
2) edit files,
3) run tests,
4) repeat until tests pass or budgets are exhausted.

Rules:
Keep diffs small and explain each step briefly.
Do not touch files outside the allowed paths.
Prefer adding/adjusting tests if they are clearly incorrect; otherwise make code comply.
Stop immediately when the success criterion is satisfied."""

    # Configure the options
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        permission_mode="acceptEdits",  # Auto-accept file edits
        cwd=working_dir,
    )

    # Store messages and results
    messages: list[dict[str, Any]] = []
    total_cost = 0.0
    success = False
    error_msg = None

    try:
        # Query Claude Code
        async for message in query(prompt=prompt_text, options=options):
            try:
                # Handle assistant messages
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            messages.append(
                                {"role": "assistant", "type": "text", "content": block.text}
                            )

                # Handle result message
                elif isinstance(message, ResultMessage):
                    total_cost = message.total_cost_usd
                    success = True
                    # ResultMessage has 'result' attribute, not 'stop_reason'
                    stop_reason = getattr(message.result, "stop_reason", "unknown") if hasattr(message, "result") else "unknown"
                    messages.append(
                        {
                            "role": "system",
                            "type": "result",
                            "cost_usd": total_cost,
                            "stop_reason": stop_reason,
                        }
                    )
            except Exception as inner_e:
                # Log individual message processing errors but continue
                error_msg = f"Error processing message: {str(inner_e)}"
                messages.append(
                    {"role": "system", "type": "error", "content": error_msg}
                )

    except Exception as e:
        error_msg = str(e)
        success = False

    return {
        "success": success,
        "messages": messages,
        "cost_usd": total_cost,
        "error": error_msg,
        "prompt": prompt_text,
    }
