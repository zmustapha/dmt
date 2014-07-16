from datetime import datetime, timedelta
from django.views.generic import View


class PrevNextWeekMixin(View):
    def __init__(self):
        self.calc_weeks(datetime.today())

    def get_context_data(self, **kwargs):
        if self.request.GET.get('date', None):
            (y, m, d) = self.request.GET['date'].split('-')
            now = datetime(year=int(y), month=int(m), day=int(d))
            self.calc_weeks(now)

        context = super(PrevNextWeekMixin, self).get_context_data(**kwargs)
        return context

    def calc_weeks(self, now):
        self.now = now
        self.week_start = now + timedelta(days=-now.weekday())
        self.week_end = self.week_start + timedelta(days=6)
        self.prev_week = self.week_start - timedelta(weeks=1)
        self.next_week = self.week_start + timedelta(weeks=1)