from datetime import date, datetime, timedelta


class PrevNextWeekMixin(object):
    """ A mixin for prev/next week params.

    This is meant to be attached to a View.
    """

    def __init__(self):
        self.calc_weeks(datetime.today())

    def get_params(self):
        if self.request.GET.get('date', None):
            (y, m, d) = self.request.GET.get('date').split('-')
            now = datetime(year=int(y), month=int(m), day=int(d))
            self.calc_weeks(now)

    def get_context_data(self, *args, **kwargs):
        self.get_params()
        context = super(PrevNextWeekMixin, self).get_context_data(
            *args, **kwargs)
        return context

    def calc_weeks(self, now):
        self.now = now
        self.week_start = now + timedelta(days=-now.weekday())
        self.week_end = self.week_start + timedelta(days=6)
        self.prev_week = self.week_start - timedelta(weeks=1)
        self.next_week = self.week_start + timedelta(weeks=1)

        fmt = '%Y-%m-%d'
        self.now_str = self.now.strftime(fmt)
        self.prev_week_str = self.prev_week.strftime(fmt)
        self.next_week_str = self.next_week.strftime(fmt)


class RangeOffsetMixin(object):
    """ A mixin for range/offset day params.

    This is meant to be attached to a View. The mixin calculates dates
    using two keyword arguments in the GET request:

    - range: how many days in the past to look
    - offset: how many days in the past to skip

    So, for example, using the default values of 31 and 0, the view will
    report on all data that occured 31 days ago, up to present time (0 days
    ago). If you wanted to look at the data for the previous month a year
    ago, you could leave range at 31 and set offset to 365.
    """

    # 'range' is a built-in function in python, so to avoid confusion call
    # this range_days.
    range_days = 31
    offset_days = 0

    def __init__(self):
        self.calc_interval()

    def calc_interval(self):
        self.interval_start = date.today() - timedelta(
            days=(self.range_days + self.offset_days))
        self.interval_end = date.today() - timedelta(days=self.offset_days)

    def get_params(self):
        self.range_days = int(
            self.request.GET.get('range', self.range_days))
        self.offset_days = int(
            self.request.GET.get('offset', self.offset_days))
        self.calc_interval()

    def get_context_data(self, *args, **kwargs):
        self.get_params()
        context = super(RangeOffsetMixin, self).get_context_data(
            *args, **kwargs)
        context.update({
            'range': self.range_days,
            'offset': self.offset_days,
            'interval_start': self.interval_start,
            'interval_end': self.interval_end,
        })
        return context
