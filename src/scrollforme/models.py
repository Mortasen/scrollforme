"""The digest data the agent must return, and its validation.

The agent never writes HTML. It returns JSON matching `SOURCE_DIGEST_SCHEMA`;
this module checks it and turns it into plain dataclasses that the template
renders. Feed content is untrusted, so nothing here interprets it.
"""

from dataclasses import asdict, dataclass

ITEM_SCHEMA = {
	"type": "object",
	"additionalProperties": False,
	"required": ["title", "url", "summary"],
	"properties": {
		"title": {"type": "string"},
		"url": {"type": "string"},
		"summary": {"type": "string"},
		"author": {"type": "string"},
		"posted_at": {"type": "string"},
	},
}

SOURCE_DIGEST_SCHEMA = {
	"type": "object",
	"additionalProperties": False,
	"required": ["items"],
	"properties": {
		"items": {"type": "array", "items": ITEM_SCHEMA},
		"notes": {"type": "string"},
	},
}


@dataclass(frozen=True)
class Item:
	"""One post, reduced to what helps the reader decide whether to open it."""

	title: str
	url: str
	summary: str
	author: str = ""
	posted_at: str = ""


@dataclass(frozen=True)
class SourceDigest:
	"""What the agent collected from one source, or why it collected nothing."""

	source_name: str
	source_url: str
	items: list[Item]
	notes: str = ""
	error: str = ""


def parse_source_digest(
	source_name: str, source_url: str, data: object, max_items: int
) -> SourceDigest:
	"""Validate the agent's structured output and cap it at `max_items`."""
	if not isinstance(data, dict) or not isinstance(data.get("items"), list):
		raise ValueError("agent output is not an object with an 'items' list")
	items = [_parse_item(raw) for raw in data["items"][:max_items]]
	return SourceDigest(source_name, source_url, items, notes=str(data.get("notes", "")))


def _parse_item(raw: object) -> Item:
	if not isinstance(raw, dict):
		raise ValueError(f"item is not an object: {raw!r}")
	fields = {key: str(raw.get(key, "")) for key in ITEM_SCHEMA["properties"]}
	if not fields["url"].startswith(("https://", "http://")):
		fields["url"] = ""
	return Item(**fields)


def digest_to_dict(digest: SourceDigest) -> dict:
	"""Serialise a digest for the run's JSON record."""
	return asdict(digest)


def digest_from_dict(data: dict) -> SourceDigest:
	"""Rebuild a digest from its JSON record."""
	items = [Item(**item) for item in data["items"]]
	return SourceDigest(**{**data, "items": items})
