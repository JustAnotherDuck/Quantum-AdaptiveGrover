"""Schema and loader for verified quantum cryptanalysis literature database."""

import os
from typing import List, Optional

import yaml
from pydantic import BaseModel


class LiteratureRecord(BaseModel):
    """Structured record for published quantum resource estimates."""

    cipher: str
    key_size: int
    block_size: int
    paper_title: str
    authors: List[str]
    year: int
    venue: str
    doi: str
    logical_qubits: int
    t_depth: Optional[int] = None
    total_t_gates_per_oracle: Optional[int] = None
    grover_iterations: str
    verified: bool
    notes: str = ""

    def citation_str(self) -> str:
        author_str = f"{self.authors[0]} et al." if len(self.authors) > 1 else self.authors[0]
        return f"{author_str} ({self.year}), '{self.paper_title}', {self.venue}. DOI: {self.doi}"


def load_literature_database(
    verified_only: bool = True,
    yaml_path: Optional[str] = None,
) -> List[LiteratureRecord]:
    """Load and validate verified literature records from YAML.

    Args:
        verified_only: If True, exclude any records where verified is False.
        yaml_path: Optional custom path to literature.yaml.

    Returns:
        List of validated LiteratureRecord instances.
    """
    if yaml_path is None:
        yaml_path = os.path.join(os.path.dirname(__file__), "literature.yaml")

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    records = [LiteratureRecord(**item) for item in data]
    if verified_only:
        records = [r for r in records if r.verified]
    return records
