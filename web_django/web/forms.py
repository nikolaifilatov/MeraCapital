from django import forms


class PeriodForm(forms.Form):
    _widget = forms.DateTimeInput(format='%Y-%m-%dT%H:%M')
    _widget.input_type = 'datetime-local'

    start = forms.DateTimeField(widget=_widget)
    end = forms.DateTimeField(widget=_widget)
