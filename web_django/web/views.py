from typing import Optional

from django.shortcuts import render
from django.views import View
from django.http import HttpResponseServerError, JsonResponse

from domain.value_objects import Period
from main import get_resolver
from usecases import GetPnLForPeriod
from .forms import PeriodForm

#class GetPnLForPeriod(Query):
#    account_id: ID
#    period: Optional[Period]
#
#
#@dataclass
#class GetPnLForPeriodResult(QueryResult):
#    pnl: USD
#    pnl_percentage: str
#    pnl_index: PnLIndex
#    period: Period


class IndexView(View):
    form_class = PeriodForm
    template_name = 'web/index.html'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            self._get_query_result()
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return HttpResponseServerError()

        query_result = self._get_query_result(
            period=Period(
                start=form.cleaned_data['start'],
                end=form.cleaned_data['end']
            )
        )
        period = query_result.pop('period')
        query_result['start_period'] = period.data['start']
        query_result['end_period'] = period.data['end']
        return JsonResponse(query_result)
    
    def _get_query_result(self, period: Optional[Period] = None) -> dict:
        query = GetPnLForPeriod(period=period)
        query_handler = get_resolver().resolve(query)
        result = query_handler.execute(query)
        return {
            'account_balance': result.account_balance,
            'pnl': result.pnl,
            'pnl_percentage': result.pnl_percentage,
            'pnl_index': result.pnl_index,
            'period': self.form_class(
                {'start': result.period.start, 'end': result.period.end}
            )
        }
