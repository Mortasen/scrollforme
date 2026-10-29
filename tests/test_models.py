from scrollforme.models import SourceResult, result_from_dict, result_to_dict


def test_result_round_trips_through_dict():
	result = SourceResult("reddit.com", "news", data={"posts": [{"title": "T"}]})
	assert result_from_dict(result_to_dict(result)) == result


def test_failed_result_has_no_data():
	result = SourceResult("reddit.com", "news", error="timed out")
	assert result.data == {}
