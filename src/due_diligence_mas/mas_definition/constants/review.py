ANALYSIS_REVIEW_CRITERIA = (
    "Review the aggregated analysis below, built from the analysts' reports, as the completeness gate before the debate. Give a completeness score from 0 to 10:\n"
    "- 0 = nothing usable, 10 = every area fully covered and source-backed;\n"
    "- check the analysis covers all the topics of each area (no skipped topics), is grounded in the profile facts and cites sources;\n"
    "- check that gaps and open questions are declared explicitly, not hidden;\n"
    "- penalize generic, unsupported or off-target statements;\n"
    "- give ONE overall score for the whole analysis, not one per analyst, and list the concrete missing items."
)

TASK_CREATION_INSTRUCTIONS = (
    "Decide autonomously whether follow-up work is needed:\n"
    "- create a task only for concrete missing items that a team member must resolve; do not create tasks if the analysis is complete;\n"
    "- create AT MOST ONE task per topic (tech, commercial), so at most 2 tasks in total: group all the missing items of a topic in that single task; team gaps are not a topic, mention them in the review only;\n"
    "- call get_users first and assign each task to the user whose role matches its topic;\n"
    "- priority is the highest of the grouped items: HIGH for gaps that block the decision, MEDIUM for important ones, LOW for minor ones;\n"
    "- the description must name the company, the topic and list every missing item of the task.\n"
    "When done, return the review."
)
