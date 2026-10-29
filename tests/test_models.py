import pytest

from scrollforme.models import digest_from_dict, digest_to_dict, parse_source_digest


def _item(**overrides):
	return {"title": "Post", "url": "https://example.com/p/1", "summary": "A post.", **overrides}


def test_output_is_capped_at_max_items():
	data = {"items": [_item(title=str(n)) for n in range(5)]}
	digest = parse_source_digest("src", "https://example.com", data, max_items=2)
	assert [item.title for item in digest.items] == ["0", "1"]


def test_non_http_urls_are_dropped():
	data = {"items": [_item(url="javascript:alert(1)")]}
	digest = parse_source_digest("src", "https://example.com", data, max_items=5)
	assert digest.items[0].url == ""


def test_output_without_items_list_is_rejected():
	with pytest.raises(ValueError):
		parse_source_digest("src", "https://example.com", {"posts": []}, max_items=5)


def test_digest_round_trips_through_dict():
	digest = parse_source_digest("src", "https://example.com", {"items": [_item()]}, max_items=5)
	assert digest_from_dict(digest_to_dict(digest)) == digest
