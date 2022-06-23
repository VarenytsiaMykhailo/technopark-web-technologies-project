from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       UserCreationForm)

from app.models import (Answer, AnswerLike, CommentToAnswer,
                        CommentToQuestion, Question, QuestionLike, User)


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['first_name'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['last_name'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['username'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['password1'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['password2'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['avatar'].widget.attrs = {
            'class': 'form-control-file'
        }

    class Meta:
        fields = ('avatar', 'email', 'username', 'first_name', 'last_name')
        labels = {
            'avatar': 'Аватар',
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Логин'
        }
        model = User


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['username'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['password'].widget.attrs = {
            'class': 'form-control'
        }

    class Meta:
        fields = ('username', 'password')
        labels = {
            'password': 'Пароль',
            'username': 'Логин'
        }
        model = User


class EditProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs = self.fields['first_name'].widget.attrs = \
            self.fields['last_name'].widget.attrs = self.fields['username'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['avatar'].widget.attrs = {
            'class': 'form-control-file'
        }

    class Meta(SignupForm.Meta):
        pass


class EditPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs = self.fields['new_password1'].widget.attrs = \
            self.fields['new_password2'].widget.attrs = {
            'class': 'form-control'
        }


class AskQuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs = self.fields['text'].widget.attrs = self.fields['tags'].widget.attrs = {
            'class': 'form-control'
        }

    class Meta:
        fields = ('title', 'text', 'tags')
        labels = {
            'tags': 'Теги',
            'text': 'Тело',
            'title': 'Заголовок',
        }
        model = Question


class QuestionRatingForm(forms.ModelForm):
    rated = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['like'].widget.attrs = {
            'id': 'question_rating_like'
        }
        self.fields['rated'].widget.attrs = {
            'id': 'question_rating_rated'
        }

    class Meta:
        fields = ('like',)
        model = QuestionLike

    def save(self, commit=True):
        if self.cleaned_data['rated']:
            if 'like' in self.changed_data:  # заменить лайк/дизлайк на дизлайк/лайк
                like = super().save()
                like.obj.recount_rating()
                return like
            else:  # убрать лайк/дизлайк
                self.instance.delete()
                self.instance.obj.recount_rating()
                return None
        else:  # поставить новый лайк/дизлайк
            like = super().save()
            like.obj.recount_rating()
            return like


class AnswerRatingForm(QuestionRatingForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['like'].widget.attrs = {
            'id': 'answer_rating_like'
        }
        self.fields['rated'].widget.attrs = {
            'id': 'answer_rating_rated'
        }

    class Meta:
        fields = ('like',)
        model = AnswerLike


class AnswerTheQuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {
            'class': 'form-control',
            'rows': '6'
        }

    class Meta:
        fields = ('text',)
        labels = {
            'text': 'Ответ'
        }
        model = Answer


class CommentToQuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {
            'class': 'form-control',
            'rows': '3'
        }

    class Meta:
        fields = ('text',)
        model = CommentToQuestion


class CommentToAnswerForm(CommentToQuestionForm):
    class Meta:
        fields = ('text',)
        model = CommentToAnswer


class QuestionsPaginationForm(forms.Form):
    order = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'pagination_order',
        'onchange': 'this.form.submit()'
    }), choices=[('-pub_date', 'дате (по убыванию)'), ('pub_date', 'дате (по возрастанию)'),
                 ('-rating', 'рейтингу (по убыванию)'), ('rating', 'рейтингу (по возрастанию)'),
                 ('-title', 'заголовку (по убыванию)'), ('title', 'заголовку (по возрастанию)')],
        initial='-pub_date', label='Сортировать по', required=False)
    limit = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'pagination_limit',
        'onchange': 'this.form.submit()'
    }), choices=[('3', '3'), ('10', '10'), ('20', '20')], initial='3', label='Кол-во на страницу', required=True)
    page = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'id': 'pagination_page',
        'onchange': 'this.form.submit()'
    }), initial=1, label='Номер страницы', min_value=1, required=False)

    def clean_order(self):
        order = self.cleaned_data['order']
        if order:
            return order
        else:
            return self.fields['order'].initial

    def clean_limit(self):
        limit = self.cleaned_data['limit']
        if limit:
            return limit
        else:
            return self.fields['limit'].initial

    def clean_page(self):
        page = self.cleaned_data['page']
        if page:
            return page
        else:
            return self.fields['page'].initial


class AnswersPaginationForm(QuestionsPaginationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].choices = [('-pub_date', 'дате (по убыванию)'), ('pub_date', 'дате (по возрастанию)'),
                                        ('-rating', 'рейтингу (по убыванию)'), ('rating', 'рейтингу (по возрастанию)')]
        self.fields['order'].initial = '-rating'


class UsersPaginationForm(QuestionsPaginationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].choices = [('-answers_count', 'популярности (по кол-ву ответов)'),
                                        ('username', 'имени (по возрастанию)'), ('-username', 'имени (по убыванию)')]
        self.fields['order'].initial = '-answers_count'
        self.fields['limit'].choices = [('10', '10'), ('30', '30'), ('50', '50')]
        self.fields['limit'].initial = '30'
