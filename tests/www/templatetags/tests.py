from django import forms
from django.template import Context, Template
from django.test import TestCase


class UtilsTemplateTagTests(TestCase):
    def test_is_radioselect(self):
        class SelectForm(forms.Form):
            radio = forms.TypedChoiceField(widget=forms.Select)
            notradio = forms.CharField()

        out = Template(
            "{% load form_fields %}" "{% for field in form.visible_fields %}" "{{ field|is_select }}," "{% endfor %}"
        ).render(
            Context(
                {
                    "form": SelectForm(),
                }
            )
        )
        self.assertEqual(out.strip(), "True,False,")

    def test_is_dateinput(self):
        class DateInputForm(forms.Form):
            radio = forms.DateField(widget=forms.DateInput)
            notradio = forms.CharField()

        out = Template(
            "{% load form_fields %}"
            "{% for field in form.visible_fields %}"
            "{{ field|is_dateinput }},"
            "{% endfor %}"
        ).render(
            Context(
                {
                    "form": DateInputForm(),
                }
            )
        )
        self.assertEqual(out.strip(), "True,False,")

    def test_is_textarea(self):
        class TextareaForm(forms.Form):
            radio = forms.CharField(widget=forms.Textarea)
            notradio = forms.CharField()

        out = Template(
            "{% load form_fields %}" "{% for field in form.visible_fields %}" "{{ field|is_textarea }}," "{% endfor %}"
        ).render(
            Context(
                {
                    "form": TextareaForm(),
                }
            )
        )
        self.assertEqual(out.strip(), "True,False,")
