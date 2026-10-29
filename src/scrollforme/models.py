"""What one site visit produced, as stored in a run's digest.json.

A module's browse() returns a free-form dict. It is kept as the agent wrote it;
feed content is untrusted, so it is only ever rendered as escaped text.
"""

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class SourceResult:
	"""The data a module returned for one configured source, or why it returned none."""

	module: str
	description: str
	data: dict = field(default_factory=dict)
	error: str = ""


def result_to_dict(result: SourceResult) -> dict:
	"""Serialise a result for the run's JSON record."""
	return asdict(result)


def result_from_dict(data: dict) -> SourceResult:
	"""Rebuild a result from its JSON record."""
	return SourceResult(**data)
