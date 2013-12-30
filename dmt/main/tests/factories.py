import factory
from datetime import datetime, timedelta
from django.utils.timezone import utc
from dmt.main.models import User, Project, Milestone, Item
from dmt.main.models import Comment, Events, Node, ActualTime


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    fullname = factory.Sequence(lambda n: 'User {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@columbia.edu'.format(n))
    grp = False
    password = ""


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project
    pid = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Test Project {0}'.format(n))
    pub_view = True
    caretaker = factory.SubFactory(UserFactory)


class MilestoneFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Milestone
    mid = factory.Sequence(lambda n: n)
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: 'Test Milestone {0}'.format(n))
    target_date = "2020-12-01"
    status = "OPEN"


class ItemFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Item
    iid = factory.Sequence(lambda n: n)
    type = "bug"
    owner = factory.SubFactory(UserFactory)
    assigned_to = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: 'Test Item {0}'.format(n))
    milestone = factory.SubFactory(MilestoneFactory)
    status = "OPEN"


class EventFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Events
    eid = factory.Sequence(lambda n: n)
    status = "OPEN"
    event_date_time = datetime(2020, 12, 1).replace(tzinfo=utc)
    item = factory.SubFactory(ItemFactory)


class CommentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Comment
    cid = factory.Sequence(lambda n: n)
    comment = "a comment"
    add_date_time = datetime(2020, 12, 1).replace(tzinfo=utc)
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    item = factory.SubFactory(ItemFactory)
    event = factory.SubFactory(EventFactory)


class NodeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Node
    nid = factory.Sequence(lambda n: n)
    added = datetime(2020, 12, 1).replace(tzinfo=utc)
    modified = datetime(2020, 12, 1).replace(tzinfo=utc)
    author = factory.SubFactory(UserFactory)


class ActualTimeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ActualTime
    item = factory.SubFactory(ItemFactory)
    resolver = factory.SubFactory(UserFactory)
    actual_time = timedelta(hours=1).total_seconds()
    completed = datetime(2013, 12, 20).replace(tzinfo=utc)
