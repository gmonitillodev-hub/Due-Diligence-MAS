from pydantic import BaseModel

from due_diligence_mas.mas_definition.classes.company import CompanyProfile, ProfileReview
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.langgraph import DEBATE_FORMATTER_NODE, FAN_OUT_NODE, HUMAN_REVIEW_NODE, MAX_PROFILE_REVISIONS, OPPORTUNITY_ANALYST_NODE, PROFILER_NODE, SUPERVISOR_NODE, skip_debate_formatter
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State, SupervisionState
from due_diligence_mas.mas_definition.langgraph.node.analysis_review import review_analysis
from due_diligence_mas.utils.logger import log_node as _log
from due_diligence_mas.mas_definition.providers.llm_provider import LLM_PROVIDER
from due_diligence_mas.mas_definition.utils.backstory_builder import backstory_builder


MERGE_INSTRUCTIONS = (
    "Merge the profile iterations below into one profile. Rules:\n"
    "- keep EVERY fact of EVERY iteration: a later iteration completes the earlier ones, it never replaces them;\n"
    "- if the same fact appears more than once, keep a single entry, preferring the most complete one (source URL, access date, strongest status);\n"
    "- if iterations conflict on a fact, keep the better-sourced entry and note the conflict in the entry;\n"
    "- a gap declared in an earlier iteration is dropped only if a later iteration fills it;\n"
    "- do not invent, summarize or rewrite facts; keep the entry format: fact | source URL | access date | status."
)

REVIEW_CRITERIA = (
    "Review the company profile below as the quality gate before the specialists build on it. Approve only if:\n"
    "- generic, tech, commercial and team are all filled, with one entry per fact or declared gap;\n"
    "- every fact entry has a source URL (never only a publication name), an access date and a status;\n"
    "- the entries concern the target company (no homonyms) and are not generic or unsupported claims;\n"
    "- missing information is declared explicitly as a gap, not omitted.\n"
    "If not approved, list the concrete issues and give the profiler actionable feedback.\n"
    "Issues listed under ALREADY REQUESTED were sent to the profiler in a previous iteration: never report them again, even if still open. "
    "Report only NEW issues, and give feedback only for them. Approve if no new issue is left."
)


def debate_entry_node() -> str:
    """First node of the debate: the formatter, or the PRO analyst when the formatter is skipped."""
    return OPPORTUNITY_ANALYST_NODE if skip_debate_formatter() else DEBATE_FORMATTER_NODE


def _supervisor_llm_call(instructions: str, content: str, output_schema: type[BaseModel]):
    """Single LLM call of the supervisor: given the instructions, the content to work on and the expected output schema, return the structured output."""
    llm = LLM_PROVIDER().get_chat_model().with_structured_output(output_schema)
    return llm.invoke([
        {"role": "system", "content": backstory_builder(AgentName.ANALYST_SUPERVISOR.value)},
        {"role": "user", "content": f"{instructions}\n\n{content}"},
    ])


def _merge_iterations(iterations: list[CompanyProfile]) -> CompanyProfile:
    """Union of the profiles of all iterations into a single CompanyProfile."""
    runs = "\n\n".join(f"ITERATION {i}:\n{p.model_dump_json(indent=2)}" for i, p in enumerate(iterations, 1))
    merged = _supervisor_llm_call(MERGE_INSTRUCTIONS, runs, CompanyProfile)
    _log(SUPERVISOR_NODE, "merged", iterations=len(iterations), entries={f: len(getattr(merged, f) or []) for f in CompanyProfile.model_fields})
    return merged


def _review_profile(state: DueDiligence_State):
    """Profile gate: merges the iterations, then approves the profile or sends it back to the profiler with feedback. An issue already requested is never sent again; the gate closes when approved or when the revisions are exhausted."""
    profile = _merge_iterations(state.profile_iterations) if len(state.profile_iterations) > 1 else state.company_profile
    requested = "\n".join(f"- {i}" for i in state.supervision.requested_issues) or "- none"
    review = _supervisor_llm_call(REVIEW_CRITERIA, f"COMPANY: {state.describe()}\n\nALREADY REQUESTED:\n{requested}\n\nPROFILE:\n{profile.model_dump_json(indent=2)}", ProfileReview)
    seen = {i.strip().lower() for i in state.supervision.requested_issues}
    review.issues = [i for i in review.issues if i.strip().lower() not in seen]
    if not review.issues:
        review.approved, review.feedback = True, ""
    _log(SUPERVISOR_NODE, "profile review", approved=review.approved, new_issues=len(review.issues), already_requested=len(seen), revisions=state.supervision.profile_revisions)
    validated = review.approved or state.supervision.profile_revisions > MAX_PROFILE_REVISIONS
    return {"company_profile": profile, "supervision": SupervisionState(profile_review=review, profile_validated=validated, requested_issues=review.issues)}


def supervisor_node(state: DueDiligence_State):
    """Single supervisor node, guarantor of profiling quality and analysis completeness.

    First visit(s), after the profiler: profile gate. Visit after the aggregator: completeness score."""
    return review_analysis(state) if state.supervision.profile_validated else _review_profile(state)


def supervisor_router(state: DueDiligence_State):
    """After the analysis review go on to the human review; after the profile gate go back to the profiler or to the fan out node."""
    if state.supervision.analysis_review is not None:
        return HUMAN_REVIEW_NODE
    if not state.supervision.profile_validated:
        return PROFILER_NODE
    return FAN_OUT_NODE
