from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

from django import forms
from .models import Comment

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)


    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは既に使われています。")
        return email

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="メールアドレス")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["url", "content"]
        widgets = {
            "url": forms.URLInput(attrs={"placeholder": "参考動画URL（任意）"}),
            "content": forms.Textarea(attrs={"rows":3, "placeholder": "コメント"}),
        }

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = get_user_model().objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("このメールアドレスは既に使われています。")
        return email
