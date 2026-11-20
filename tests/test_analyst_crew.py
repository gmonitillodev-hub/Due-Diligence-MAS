from crewai import Process

import pytest

from due_diligence_mas.mas_definition.classes import CompanyInfo
from due_diligence_mas.mas_definition.crewai_fr.crews import analyst
from due_diligence_mas.mas_definition.crewai_fr.crews.analyst import AnalystCrew


def test_analyst_crew_is_hierarchical_with_manager():
    crew = AnalystCrew(CompanyInfo(company_name="Acme"))
    crew.build_crew()

    assert crew.crew.process == Process.hierarchical
    assert crew.crew.manager_agent.role == "Analysis Manager"
    assert [a.role for a in crew.crew.agents] == ["Company Profiler", "Tech Reviewer", "Commercial Analyst", "Team Analyst", "Memo Writer"]
    assert crew.manager.get_tasks() == []


@pytest.mark.parametrize("use_async", [True, False])
def test_specialists_async_flag_and_manager_report_waits_for_all(monkeypatch, use_async):
    monkeypatch.setattr(analyst, "ANALYST_ASYNC", use_async)
    crew = AnalystCrew(CompanyInfo(company_name="Acme"))
    crew.build_crew()

    profile, *specialists, report = crew.crew.tasks
    assert not profile.async_execution
    assert len(specialists) == 3 and all(t.async_execution is use_async for t in specialists)
    assert not report.async_execution
    assert report.agent.role == "Memo Writer"
    assert len(report.context) == 4
