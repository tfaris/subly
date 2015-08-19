from django import forms

from .models import VideoFilter


# TODO: Make this a normal (non-ModelForm) form and build form manually. Find
# TODO: a way to make a bunch of filter forms fit on one page. Probably pull down
# TODO: with ajax instead.

class EditVideoFilterForm(forms.ModelForm):
    class Meta:
        model = VideoFilter
        fields = ['string', 'field', 'channel_title', 'ignore_case', 'is_regex', 'exact', 'exclusion']
