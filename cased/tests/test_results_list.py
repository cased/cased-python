from cased.api.abstract.results_list import ResultsList
from cased.api import Event
import cased


# Test data

results_1 = [
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-1",
        "action": "test.action",
        "actor": "test",
    },
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-2",
        "action": "test.action2",
        "actor": "test",
    },
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-3",
        "action": "test.action3",
        "actor": "test",
    },
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-4",
        "action": "test.action4",
        "actor": "test",
    },
]


results_2 = [
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-5",
        "action": "test.action5",
        "actor": "test",
    },
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-6",
        "action": "test.action6",
        "actor": "test",
    },
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-7",
        "action": "test.action7",
        "actor": "test",
    },
    {
        "audit_event_url": "https://api.cased.com/api/audit-trails/system/events/test-id-8",
        "action": "test.action4",
        "actor": "test",
    },
]


headers_1 = {
    "Date": "Thu, 04 Jun 2020 03:31:21 GMT",
    "Content-Type": "application/json; charset=utf-8",
    "Server": "nginx/1.17.10",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Link": '<https://api.cased.com.com/api/events?page=1>; rel="first", <https://api.cased.com.com/api/events?page=40>; rel="last", <https://api.cased.com.com/api/events?page=3>; rel="prev", <https://api.cased.com.com/api/events?page=5>; rel="next"',
}

headers_2 = {
    "Date": "Thu, 04 Jun 2020 03:31:21 GMT",
    "Content-Type": "application/json; charset=utf-8",
    "Server": "nginx/1.17.10",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Link": '<https://api.cased.com.com/api/events?page=1>; rel="first", <https://api.cased.com.com/api/events?page=40>; rel="last", <https://api.cased.com.com/api/events?page=4>; rel="prev", <https://api.cased.com.com/api/events?page=6>; rel="next"',
}

# Used for the page_iter() tests; reflects the actual test data length
headers_3 = {
    "Date": "Thu, 04 Jun 2020 03:31:21 GMT",
    "Content-Type": "application/json; charset=utf-8",
    "Server": "nginx/1.17.10",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Link": '<https://api.cased.com.com/api/events?page=1>; rel="first", <https://api.cased.com.com/api/events?page=2>; rel="last", <https://api.cased.com.com/api/events?page=2>; rel="next"',
}

# No next or previous
headers_4 = {
    "Date": "Thu, 04 Jun 2020 03:31:21 GMT",
    "Content-Type": "application/json; charset=utf-8",
    "Server": "nginx/1.17.10",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Link": '<https://api.cased.com.com/api/events?page=1>; rel="first", <https://api.cased.com.com/api/events?page=1>; rel="last"',
}


class MockInitialListResponse(object):
    @property
    def headers(self):
        return headers_1

    def json(self):
        data = {"total_pages": 40, "total_count": 500, "results": results_1}
        return data


class MockLimitedListResponse(object):
    @property
    def headers(self):
        return headers_4

    def json(self):
        data = {"total_pages": 1, "total_count": 5, "results": results_1}
        return data


response = MockInitialListResponse()
list_obj = ResultsList(response, Event)


response2 = MockLimitedListResponse()
list_obj2 = ResultsList(response2, Event)


class TestListObject(object):
    def test_results_list_can_be_created(self):
        assert list_obj.headers
        assert list_obj.json_response

    def test_results_list_has_first_page_url(self):
        assert list_obj.first_page_url == "https://api.cased.com.com/api/events?page=1"

    def test_results_list_has_first_page(self):
        assert list_obj.first_page == 1

    def test_results_list_has_last_page_url(self):
        assert list_obj.last_page_url == "https://api.cased.com.com/api/events?page=40"

    def test_results_list_has_last_page(self):
        assert list_obj.last_page == 40

    def test_results_list_has_next_page_url(self):
        assert list_obj.next_page_url == "https://api.cased.com.com/api/events?page=5"

    def test_results_list_has_next_page(self):
        assert list_obj.next_page == 5

    def test_results_list_has_prev_page_url(self):
        assert list_obj.prev_page_url == "https://api.cased.com.com/api/events?page=3"

    def test_results_list_has_prev_page(self):
        assert list_obj.prev_page == 3

    def test_results_list_has_results(self):
        assert list_obj.results == results_1

    def test_results_list_has_total_pages(self):
        assert list_obj.total_pages == 40

    def test_results_list_has_total_count(self):
        assert list_obj.total_count == 500

    def test_results_list_has_has_more_boolen(self):
        assert list_obj.has_more()

    def test_limited_results_list_has_first_page(self):
        assert list_obj2.first_page == 1

    def test_limited_results_list_has_last_page_url(self):
        assert list_obj2.last_page_url == "https://api.cased.com.com/api/events?page=1"

    def test_limited_results_list_has_last_page(self):
        assert list_obj2.last_page == 1

    def test_limited_results_list_has_no_next_page_url(self):
        assert list_obj2.next_page_url == None

    def test_limited_results_list_no_next_page(self):
        assert list_obj2.next_page == None

    def test_limited_results_list_has_no_prev_page_url(self):
        assert list_obj2.prev_page_url == None

    def test_limited_results_list_has_no_prev_page(self):
        assert list_obj2.prev_page == None

    def test_limited_results_list_has_results(self):
        assert list_obj2.results == results_1

    def test_limited_results_list_has_total_pages(self):
        assert list_obj2.total_pages == 1

    def test_limited_results_list_has_total_count(self):
        assert list_obj2.total_count == 5

    def test_limited_results_list_has_has_more_boolen(self):
        assert list_obj2.has_more() == False

    def test_fetch_next(self):
        from cased.tests.util import mock_response

        data = {"total_pages": 40, "total_count": 500, "results": results_2}

        with mock_response(headers=headers_2, json_data=data):
            cased.policy_key = "cs_test_001"
            assert list_obj.fetch_next().prev_page == 4
            assert list_obj.fetch_next().next_page == 6
            assert list_obj.fetch_next().results == results_2

    def test_page_iter_can_iterate_through_results(self):
        from cased.tests.util import mock_response

        data = {
            "total_pages": 2,
            "total_count": 8,
            "results": results_2,
        }  # use the actual test values here since we're testing the iterator

        with mock_response(headers=headers_3, json_data=data):
            cased.policy_key = "cs_test_001"

            iterator = list_obj.page_iter()
            next_result = iterator.__next__()

            assert next_result == results_2

    def test_page_iter_can_iterate_through_results_of_single_page(self):
        from cased.tests.util import mock_response

        data = {
            "total_pages": 1,
            "total_count": 4,
            "results": results_1,
        }  # use the actual test values here since we're testing the iterator

        with mock_response(headers=headers_4, json_data=data):
            cased.policy_key = "cs_test_001"

            iterator = list_obj.page_iter()
            next_result = iterator.__next__()

            assert next_result == results_1

    def test_page_iter_works_with_next(self):
        from cased.tests.util import mock_response

        data = {
            "total_pages": 2,
            "total_count": 8,
            "results": results_2,
        }  # use the actual test values here since we're testing the iterator

        with mock_response(headers=headers_3, json_data=data):
            cased.policy_key = "cs_test_001"

            iterator = list_obj.page_iter()
            next_result = next(iterator)

            assert next_result == results_2
