import unittest
from datetime import timedelta, datetime
from dmt.main.timeline import (
    TimeLineItem, TimeLineEvent, TimeLineComment, TimeLineActualTime,
    TimeLineStatus, TimeLinePost, TimeLineMilestone,
)


class Dummy(TimeLineItem):
    def __init__(self, n):
        self.n = n

    def timestamp(self):
        return self.n


class TimeLineItemTest(unittest.TestCase):
    def test_sort(self):
        a = [Dummy(3), Dummy(2)]
        a.sort()
        self.assertEqual(a[0].n, 2)
        self.assertEqual(a[1].n, 3)

    def test_base_methods(self):
        t = Dummy(1)
        self.assertEqual(t.user(), None)
        self.assertEqual(t.timestamp(), 1)
        self.assertEqual(t.project(), None)
        self.assertEqual(t.event_type(), None)
        self.assertEqual(t.title(), None)
        self.assertEqual(t.body(), None)
        self.assertEqual(t.label(), None)
        self.assertEqual(t.url(), None)


class DummyItem(object):
    def __init__(self):
        self.title = "dummy item"

    def get_absolute_url(self):
        return "item absolute url"


class DummyEvent(object):
    def __init__(self):
        self.event_date_time = "foo"
        self.item = DummyItem()


class DummyComment(object):
    def __init__(self):
        self.event = DummyEvent()
        self.comment = "Dummy Comment"
        self.add_date_time = "comment add_date_time"
        self.item = self.event.item

    def user(self):
        return "comment user"


class TestTimeLineEvent(unittest.TestCase):
    def test_basics(self):
        e = TimeLineEvent(DummyComment())
        self.assertEqual(e.label(), None)
        self.assertEqual(e.timestamp(), "foo")
        self.assertEqual(e.event_type(), "event")
        self.assertEqual(e.title(), "dummy item")
        self.assertEqual(e.body(), "Dummy Comment")
        self.assertEqual(e.user(), "comment user")
        self.assertEqual(e.url(), "item absolute url")


class TestTimeLineComment(unittest.TestCase):
    def test_basics(self):
        e = TimeLineComment(DummyComment())
        self.assertEqual(e.label(), "COMMENT ADDED")
        self.assertEqual(e.timestamp(), "comment add_date_time")
        self.assertEqual(e.event_type(), "comment")
        self.assertEqual(e.title(), "dummy item")
        self.assertEqual(e.body(), "Dummy Comment")
        self.assertEqual(e.user(), "comment user")
        self.assertEqual(e.url(), "item absolute url")


class DummyActualTime(object):
    def __init__(self):
        self.completed = "completed"
        self.resolver = "resolver"
        self.actual_time = timedelta(hours=1)
        self.item = DummyItem()


class TestTimeLineActualTime(unittest.TestCase):
    def test_basics(self):
        e = TimeLineActualTime(DummyActualTime())
        self.assertEqual(e.label(), "TIME LOGGED")
        self.assertEqual(e.timestamp(), "completed")
        self.assertEqual(e.event_type(), "actual_time")
        self.assertEqual(e.title(), "dummy item")
        self.assertEqual(e.body(), "1.00 hours")
        self.assertEqual(e.user(), "resolver")
        self.assertEqual(e.url(), "item absolute url")


class DummyStatus(object):
    def __init__(self):
        self.user = "status user"
        self.added = datetime.now().date()
        self.body = "body"


class TestTimeLineStatus(unittest.TestCase):
    def test_basics(self):
        e = TimeLineStatus(DummyStatus())
        self.assertEqual(e.label(), "STATUS UPDATE")
        self.assertEqual(e.event_type(), "status_update")
        self.assertEqual(e.title(), "status update")
        self.assertEqual(e.body(), "body")
        self.assertEqual(e.user(), "status user")
        self.assertEqual(e.url(), None)


class DummyPost(object):
    def __init__(self):
        self.added = "added"
        self.author = "author"
        self.subject = "subject"
        self.body = "body"

    def get_absolute_url(self):
        return "post absolute url"


class TestTimeLinePost(unittest.TestCase):
    def test_basics(self):
        e = TimeLinePost(DummyPost())
        self.assertEqual(e.label(), "FORUM POST")
        self.assertEqual(e.event_type(), "forum_post")
        self.assertEqual(e.title(), "subject")
        self.assertEqual(e.body(), "body")
        self.assertEqual(e.user(), "author")
        self.assertEqual(e.url(), "post absolute url")


class DummyMilestone(object):
    def __init__(self):
        self.target_date = datetime.now().date()
        self.name = "milestone name"

    def get_absolute_url(self):
        return "milestone url"


class TestTimeLineMilestone(unittest.TestCase):
    def test_basics(self):
        e = TimeLineMilestone(DummyMilestone())
        self.assertEqual(e.label(), "MILESTONE")
        self.assertEqual(e.event_type(), "milestone")
        self.assertEqual(e.title(), "milestone name")
        self.assertEqual(e.body(), None)
        self.assertEqual(e.user(), None)
        self.assertEqual(e.url(), "milestone url")
