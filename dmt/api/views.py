from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from rest_framework import filters, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from simpleduration import Duration, InvalidDuration
from datetime import datetime, timedelta
from dateutil import parser

from dmt.main.models import (
    Client, Item, Milestone, Notify, Project, UserProfile
)
from dmt.main.utils import new_duration

from dmt.api.auth import SafeOriginAuthentication, SafeOriginPermission
from dmt.api.serializers import (
    ClientSerializer, ItemSerializer, MilestoneSerializer, NotifySerializer,
    ProjectSerializer, UserSerializer,
)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    paginate_by = 10


class ItemHoursView(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        item = get_object_or_404(Item, iid=pk)
        user = request.user.userprofile
        d = new_duration(request.POST.get('time', '1 hour'))
        td = d.timedelta()
        item.add_resolve_time(user, td)
        return HttpResponse("ok")


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    paginate_by = 20


class ExternalAddItemView(APIView):
    """An endpoint to add an action item from outside the PMT.

    For Mediathread, Edblogs, etc.
    """
    authentication_classes = (SafeOriginAuthentication,)
    permission_classes = (SafeOriginPermission,)

    def redirect_or_return_item(self, request, item, redirect_url, append_iid):
        if redirect_url:
            if append_iid:
                redirect_url += 'iid=' + unicode(item.pk)
            return redirect(redirect_url)
        else:
            data = ItemSerializer(item, context={'request': request}).data
            return Response(data)

    @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        pid = request.data.get('pid')
        mid = request.data.get('mid')
        title = request.data.get('title', 'External issue report')
        description = request.data.get('description', 'No description')
        email = request.data.get('email', 'No email')
        name = request.data.get('name', 'Anonymous')
        item_type = request.data.get('type', 'bug')
        assignee_username = request.data.get('assigned_to')
        owner_username = request.data.get('owner')
        priority = request.data.get('priority', '1')
        target_date = request.data.get('target_date', '')
        estimated_time = request.data.get('estimated_time', '1 hour')
        debug_info = request.data.get('debug_info', '')
        redirect_url = request.data.get('redirect_url', '')
        append_iid = request.data.get('append_iid', '')

        if debug_info:
            description += '\n-----\n\nDEBUG INFO:\n' + debug_info + '\n'

        description += '\n-----\n\nSubmitted by ' \
            + name + ' <' + email + '>\n'
        project = get_object_or_404(Project, pid=pid)

        try:
            assignee = UserProfile.objects.get(username=assignee_username)
        except UserProfile.DoesNotExist:
            assignee = project.caretaker

        try:
            owner = UserProfile.objects.get(username=owner_username)
        except UserProfile.DoesNotExist:
            owner = project.caretaker

        try:
            milestone = Milestone.objects.get(mid=mid)
        except Milestone.DoesNotExist:
            milestone = project.upcoming_milestone()

        item = project.add_item(
            type=item_type,
            milestone=milestone,
            title=title,
            assigned_to=assignee,
            owner=owner,
            priority=priority,
            target_date=parser.parse(target_date).date(),
            description=description,
            estimated_time=estimated_time
        )

        return self.redirect_or_return_item(
            request, item, redirect_url, append_iid)


def normalize_email(email):
    if '@' not in email:
        return email + "@columbia.edu"
    return email


class GitUpdateView(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        iid = request.POST.get('iid', None)
        item = get_object_or_404(Item, iid=iid)
        email = request.POST.get('email', None)
        email = normalize_email(email)
        user = get_object_or_404(UserProfile, email=email)
        status = request.POST.get('status', '')
        resolve_time = request.POST.get('resolve_time', '')
        comment = request.POST.get('comment', '')
        if status == 'FIXED':
            item.status = 'RESOLVED'
            item.r_status = 'FIXED'
            item.add_event("RESOLVED", user, comment)
            item.save()
            item.update_email(
                "%s $%d %s updated\n%s\n" % (
                    item.type, item.iid, item.title, comment),
                user)
        elif comment != "":
            item.add_comment(user, comment)
            item.update_email(
                "comment added to %s $%d %s updated\n%s\n" % (
                    item.type, item.iid, item.title, comment),
                user)
        if resolve_time != "":
            try:
                d = Duration(resolve_time)
                td = d.timedelta()
                item.add_resolve_time(user, td)
            except InvalidDuration:
                # eventually, this needs to get back to the user
                # via form validation, but for now
                # we just deal with it...
                pass
        item.touch()
        return HttpResponse("ok")


class MilestoneItemList(generics.ListCreateAPIView):
    model = Item
    serializer_class = ItemSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Item.objects.filter(
            milestone__pk=pk).prefetch_related(
            'owner', 'assigned_to',
            'milestone')


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    paginate_by = 20


class NotifyView(APIView):
    """
    View to update a user's notification status on an action item.

    This is a standalone resource not related to /item/ because
    django-rest-framework doesn't support writable nested resources yet. See
    the github issue here for the status of this:
    https://github.com/tomchristie/django-rest-framework/issues/395
    """
    model = Notify
    serializer_class = NotifySerializer
    permission_classes = ()

    def delete(self, request, pk, **kwargs):
        if request.user.is_authenticated():
            item = get_object_or_404(Item, iid=pk)
            user = request.user.userprofile
            Notify.objects.get(username=user, item=item).delete()
            return Response(status=204)
        else:
            return Response(status=403)

    def get(self, request, pk):
        if request.user.is_authenticated():
            user = request.user.userprofile
            pmt_username = user.username
            get_object_or_404(Notify,
                              item_id=pk,
                              username=pmt_username)
            data = {'notify': pmt_username}
            return Response(data)
        else:
            return Response(status=404)

    def post(self, request, pk):
        if not request.user.is_authenticated():
            return Response(status=403)

        item = get_object_or_404(Item, iid=pk)
        user = request.user.userprofile
        n, _ = Notify.objects.get_or_create(username=user, item=item)
        n.user = request.user
        n.save()
        return Response(status=201)

    def put(self, request, pk):
        if not request.user.is_authenticated():
            return Response(status=403)

        item = get_object_or_404(Item, iid=pk)
        user = request.user.userprofile
        n, _ = Notify.objects.get_or_create(username=user, item=item)
        n.user = request.user
        n.save()
        return Response(status=201)


class ProjectMilestoneList(generics.ListCreateAPIView):
    model = Milestone
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Milestone.objects.filter(project__pk=pk)


def process_completed(completed=None):
    if completed == 'last':
        return datetime.now() - timedelta(days=7)
    if completed == 'before_last':
        return datetime.now() - timedelta(days=14)
    return completed


class AddTrackerView(View):
    @method_decorator(login_required)
    def post(self, request):
        pid = request.POST.get('pid', None)
        task = request.POST.get('task', None)
        d = new_duration(request.POST.get('time', '1 hour'))
        client_uni = request.POST.get('client', '')
        completed = process_completed(request.POST.get('completed', ''))
        td = d.timedelta()
        # two required fields
        if None in [pid, task]:
            return HttpResponse("bad request")

        project = get_object_or_404(Project, pid=pid)
        user = request.user.userprofile
        milestone = project.upcoming_milestone()
        item = Item.objects.create(
            milestone=milestone,
            type='action item',
            owner=user, assigned_to=user,
            owner_user=user.user, assigned_user=user.user,
            title=task, status='VERIFIED',
            priority=1, target_date=milestone.target_date,
            last_mod=datetime.now(),
            estimated_time=td)
        if client_uni != '':
            r = Client.objects.filter(
                email=client_uni + "@columbia.edu")
            if r.count() > 0:
                item.add_clients([r[0]])
            else:
                pass
        item.add_resolve_time(user, td, completed)
        return HttpResponse("ok")


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    paginate_by = 20


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
