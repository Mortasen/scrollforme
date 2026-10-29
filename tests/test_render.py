from datetime import datetime

from scrollforme.render import render_digest
from scrollforme.models import Item, SourceDigest

GENERATED_AT = datetime(2026, 10, 29, 8, 30)


def test_feed_text_is_escaped():
	item = Item(title="<script>alert(1)</script>", url="https://example.com", summary="<b>hi</b>")
	html = render_digest([SourceDigest("src", "https://example.com", [item])], GENERATED_AT)
	assert "<script>alert" not in html
	assert "&lt;script&gt;" in html
	assert "<b>hi</b>" not in html


def test_page_lists_items_and_failed_sources():
	ok = SourceDigest("Reddit", "https://reddit.com", [Item("T", "https://reddit.com/x", "S")])
	failed = SourceDigest("Instagram", "https://instagram.com", [], error="timed out")
	html = render_digest([ok, failed], GENERATED_AT)
	assert "1 items from 2 sources" in html
	assert 'href="https://reddit.com/x"' in html
	assert "Could not read this source: timed out" in html
