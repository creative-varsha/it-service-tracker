from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Ticket


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'category', 'priority', 'description')

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters.')
        return title

    def clean_description(self):
        desc = self.cleaned_data['description'].strip()
        if len(desc) < 10:
            raise forms.ValidationError('Please describe the issue in at least 10 characters.')
        return desc


class AssignForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('assigned_to', 'status')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(profile__role__in=['agent', 'admin'])
        self.fields['assigned_to'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows': 3})}

    def clean_body(self):
        body = self.cleaned_data['body'].strip()
        if not body:
            raise forms.ValidationError('Comment cannot be empty.')
        return body
