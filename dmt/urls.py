from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

from dmt.main.views import (
    SearchView,
    AddCommentView, ResolveItemView,
    InProgressItemView, VerifyItemView, ReopenItemView,
    SplitItemView, ItemDetailView, IndexView, ClientListView,
    ClientDetailView, ForumView, GroupDetailView, GroupListView,
    NodeDetailView, MilestoneDetailView, ProjectListView, ProjectDetailView,
    UserListView, UserDetailView, NodeReplyView, ProjectAddTodoView,
    ProjectAddNodeView, TagItemView, RemoveTagFromItemView,
    TagNodeView, RemoveTagFromNodeView,
    TagDetailView, TagListView, ItemPriorityView, ReassignItemView,
    ChangeOwnerItemView, ProjectAddStatusUpdateView,
    StatusUpdateListView, StatusUpdateUpdateView, StatusUpdateDeleteView,
    NodeUpdateView, NodeDeleteView, UserUpdateView,
    ProjectCreateView, ProjectUpdateView, MilestoneUpdateView, ItemUpdateView,
    ProjectAddItemView, DashboardView, MilestoneListView,
    ProjectRemoveUserView, ProjectAddUserView, ProjectAddMilestoneView,
    ItemDeleteView, SignS3View, ItemAddAttachmentView,
    DeactivateUserView
)
from dmt.main.feeds import ForumFeed, StatusUpdateFeed, ProjectFeed

admin.autodiscover()

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (
    r'^accounts/logout/$',
    'django.contrib.auth.views.logout',
    {'next_page': redirect_after_logout})
if hasattr(settings, 'WIND_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (
        r'^accounts/logout/$',
        'djangowind.views.logout',
        {'next_page': redirect_after_logout})

urlpatterns = patterns(
    '',
    auth_urls,
    logout_page,
    (r'^$', IndexView.as_view()),
    (r'^admin/', include(admin.site.urls)),
    (r'^api/1.0/', include('dmt.api.urls')),
    (r'^drf/', include('dmt.api.urls')),
    (r'^claim/', include('dmt.claim.urls')),
    (r'^search/$', SearchView.as_view()),
    (r'^client/$', ClientListView.as_view()),
    url(r'^client/(?P<pk>\d+)/$', ClientDetailView.as_view(),
        name="client_detail"),
    (r'^sign_s3/$', SignS3View.as_view()),
    (r'^forum/$', ForumView.as_view()),
    (r'^forum/(?P<pk>\d+)/$', NodeDetailView.as_view()),
    (r'^forum/(?P<pk>\d+)/reply/$', NodeReplyView.as_view()),
    (r'^forum/(?P<pk>\d+)/tag/$', TagNodeView.as_view()),
    (r'^forum/(?P<pk>\d+)/remove_tag/(?P<slug>[^/]+)/$',
     RemoveTagFromNodeView.as_view()),
    (r'^forum/(?P<pk>\d+)/edit/$', NodeUpdateView.as_view()),
    (r'^forum/(?P<pk>\d+)/delete/$', NodeDeleteView.as_view()),
    url(r'^group/$', GroupListView.as_view(), name='group_list'),
    url(r'^group/(?P<pk>\w+)/$', GroupDetailView.as_view(),
        name='group_detail'),
    url(r'^item/(?P<pk>\d+)/$', ItemDetailView.as_view(), name='item_detail'),
    (r'^item/(?P<pk>\d+)/edit/$', ItemUpdateView.as_view()),
    (r'^item/(?P<pk>\d+)/comment/$', AddCommentView.as_view()),
    (r'^item/(?P<pk>\d+)/resolve/$', ResolveItemView.as_view()),
    (r'^item/(?P<pk>\d+)/inprogress/$', InProgressItemView.as_view()),
    (r'^item/(?P<pk>\d+)/verify/$', VerifyItemView.as_view()),
    (r'^item/(?P<pk>\d+)/reopen/$', ReopenItemView.as_view()),
    (r'^item/(?P<pk>\d+)/split/$', SplitItemView.as_view()),
    (r'^item/(?P<pk>\d+)/tag/$', TagItemView.as_view()),
    (r'^item/(?P<pk>\d+)/remove_tag/(?P<slug>[^/]+)/$',
     RemoveTagFromItemView.as_view()),
    (r'^item/(?P<pk>\d+)/priority/(?P<priority>\d)/$',
     ItemPriorityView.as_view()),
    (r'^item/(?P<pk>\d+)/assigned_to/$', ReassignItemView.as_view()),
    (r'^item/(?P<pk>\d+)/owner/$', ChangeOwnerItemView.as_view()),
    (r'^item/(?P<pk>\d+)/delete/$', ItemDeleteView.as_view()),
    (r'^item/(?P<pk>\d+)/add_attachment/$', ItemAddAttachmentView.as_view()),
    (r'^milestone/$', MilestoneListView.as_view()),
    (r'^milestone/(?P<pk>\d+)/$', MilestoneDetailView.as_view()),
    (r'^milestone/(?P<pk>\d+)/edit/$', MilestoneUpdateView.as_view()),
    url(r'^project/$', ProjectListView.as_view(), name='project_list'),
    url(r'^project/create/$', ProjectCreateView.as_view(),
        name='project_create'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(),
        name='project_detail'),
    (r'^project/(?P<pk>\d+)/add_bug/$',
     ProjectAddItemView.as_view(item_type='bug')),
    (r'^project/(?P<pk>\d+)/add_action_item/$',
     ProjectAddItemView.as_view(item_type='action item')),
    (r'^project/(?P<pk>\d+)/add_todo/$', ProjectAddTodoView.as_view()),
    (r'^project/(?P<pk>\d+)/add_node/$', ProjectAddNodeView.as_view()),
    (r'^project/(?P<pk>\d+)/add_milestone/$',
     ProjectAddMilestoneView.as_view()),
    (r'^project/(?P<pk>\d+)/add_update/$',
     ProjectAddStatusUpdateView.as_view()),
    (r'^project/(?P<pk>\d+)/edit/$', ProjectUpdateView.as_view()),
    (r'^project/(?P<pk>\d+)/remove_user/(?P<username>\w+)/$',
     ProjectRemoveUserView.as_view()),
    (r'^project/(?P<pk>\d+)/add_user/$', ProjectAddUserView.as_view()),
    (r'^status/$', StatusUpdateListView.as_view()),
    (r'^status/(?P<pk>\d+)/$', StatusUpdateUpdateView.as_view()),
    (r'^status/(?P<pk>\d+)/delete/$', StatusUpdateDeleteView.as_view()),
    (r'^report/', include('dmt.report.urls')),
    (r'^user/$', UserListView.as_view()),
    url(r'^user/(?P<pk>\w+)/$', UserDetailView.as_view(), name='user_detail'),
    url(r'^user/(?P<pk>\w+)/deactivate/$', DeactivateUserView.as_view(),
        name='user_deactivate'),
    (r'^user/(?P<pk>\w+)/edit/$', UserUpdateView.as_view()),
    (r'^tag/$', TagListView.as_view()),
    (r'^tag/(?P<slug>[^/]+)/$', TagDetailView.as_view()),
    (r'^dashboard/$', DashboardView.as_view()),
    (r'^feeds/forum/rss/$', ForumFeed()),
    (r'^feeds/status/$', StatusUpdateFeed()),
    (r'^feeds/project/(?P<pk>\d+)/$', ProjectFeed()),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'^smoketest/', include('smoketest.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
