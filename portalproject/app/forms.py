from django import forms
from django.core.exceptions import ValidationError
from .models import Users, Interest

class SignUpForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(queryset=Interest.objects.all().distinct(), widget=forms.CheckboxSelectMultiple)
    # email_or_phone = forms.CharField(max_length=255, label='Email or Phone')
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ['full_name', 'email', 'phone', 'gender', 'country', 'password','interests']
        widgets = {
            'password': forms.PasswordInput(),
        }
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Add a common class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full mt-2 px-4 py-2 rounded-xl'


