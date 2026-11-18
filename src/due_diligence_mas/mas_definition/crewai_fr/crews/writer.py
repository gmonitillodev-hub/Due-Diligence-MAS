from due_diligence_mas.mas_definition.agents.writer.memo_writer import MemoWriter_Agent
from due_diligence_mas.mas_definition.crewai_fr.crews.base import BaseCrew


class MemoWriterCrew(BaseCrew):
    """
    Crew that writes the final memo.
    """

    name = "Memo writer Crew"

    def __init__(self, args: dict | None = None):
        self.topic = args or {}
        super().__init__()

    def _setup(self):
        self.memo_writer = self.add(MemoWriter_Agent(), self.topic, key="memo")
