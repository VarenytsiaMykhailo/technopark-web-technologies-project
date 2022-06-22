from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import RedirectView

from app.forms import (AnswerTheQuestionForm, AskQuestionForm,
                         CommentToAnswerForm, CommentToQuestionForm,
                         EditPasswordForm, EditProfileForm, LoginForm,
                         QuestionRatingForm, QuestionsPaginationForm,
                         SignupForm, UsersPaginationForm)
from app.models import (Answer, CommentToAnswer, CommentToQuestion, Question,
                          QuestionLike, QuestionTag, User)

# Create your views here.

QUESTIONS = [
    {
        "title": f"Title {i}",
        "text": f"This is text for question #{i}",
        "number": i
    } for i in range(10)
]


class BaseView(View):
    template_name = 'index.html'

    def get(self, request, **kwargs):
        kwargs['top_tags'] = cache.get('top_tags')
        kwargs['top_users'] = cache.get('top_users')
        return render(request, self.template_name, kwargs)


class PaginationView(BaseView):
    template_name = 'index.html'

    def get(self, request, **kwargs):
        pagination = kwargs.get('pagination', Question.objects.all())
        pagination_form = kwargs.get('pagination_form', QuestionsPaginationForm(request.GET or None))
        if pagination_form.is_valid():
            pagination = Paginator(pagination.order_by(pagination_form.cleaned_data['order']),
                                   pagination_form.cleaned_data['limit'])
            page = pagination_form.cleaned_data['page']
        else:
            pagination = Paginator(pagination, pagination_form.fields['limit'].initial)
            page = pagination_form.fields['page'].initial
        try:
            pagination = pagination.page(page)
        except PageNotAnInteger:
            return HttpResponseNotFound()
        except EmptyPage:
            pagination = pagination.page(pagination.num_pages)
        kwargs['pagination'] = pagination
        kwargs['pagination_form'] = pagination_form
        return super().get(request, **kwargs)


class SignupView(BaseView):
    template_name = 'signup.html'

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('app:index')
        kwargs['form'] = SignupForm()
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('app:index')
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            if not User.objects.filter(username=form.cleaned_data['username']).exists():
                user = form.save()
                login(request, user)
                return redirect(request.GET.get('next', reverse('app:index')))
        kwargs['form'] = form
        return super().get(request, **kwargs)


class LoginView(BaseView):
    template_name = 'login.html'

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('app:index')
        kwargs['form'] = LoginForm()
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('app:index')
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect(request.GET.get('next', reverse('app:index')))
        kwargs['form'] = form
        return super().get(request, **kwargs)


class UserView(BaseView):
    template_name = 'profile.html'

    def get(self, request, **kwargs):
        if request.user.id == kwargs['id']:
            kwargs['edit_profile_form'] = EditProfileForm(instance=request.user)
            kwargs['edit_password_form'] = EditPasswordForm(user=request.user)
        else:
            self.template_name = 'user.html'
            kwargs['user'] = get_object_or_404(User, id=kwargs['id'])
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        if not request.user.id == kwargs['id']:
            return HttpResponseForbidden()
        edit_profile_form = EditProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        edit_password_form = EditPasswordForm(data=request.POST, user=request.user)
        if edit_profile_form.is_valid():
            edit_profile_form.save()
        elif edit_password_form.is_valid():
            edit_password_form.save()
        kwargs['edit_profile_form'] = edit_profile_form
        kwargs['edit_password_form'] = edit_password_form
        return super().get(request, **kwargs)


class LogoutView(RedirectView):
    url = reverse_lazy('app:index')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class UsersView(PaginationView):
    template_name = 'users.html'

    def get(self, request, **kwargs):
        kwargs['pagination'] = User.objects.all()
        kwargs['pagination_form'] = UsersPaginationForm(request.GET or None)
        return super().get(request, **kwargs)


class AskQuestionView(BaseView):
    template_name = 'ask.html'

    def get(self, request, **kwargs):
        kwargs['form'] = AskQuestionForm()
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        form = AskQuestionForm(data=request.POST, instance=Question(author=request.user))
        if form.is_valid():
            question = form.save()
            return redirect('app:question', question_id=question.id)
        kwargs['form'] = form
        return super().get(request, **kwargs)


class QuestionView(PaginationView):
    template_name = 'question.html'

    def get(self, request, **kwargs):
        id_ = kwargs['id']
        question = get_object_or_404(Question, id=id_)
        kwargs['answer_form'] = AnswerTheQuestionForm(initial={
            'question': id_
        })
        return self.get_(request, id_, question, **kwargs)

    def get_(self, request, id_, question, **kwargs):
        kwargs['comment_to_answer_form'] = CommentToAnswerForm()
        kwargs['comment_to_question_form'] = CommentToQuestionForm()
        kwargs['pagination'] = question.get_answers()
        kwargs['question'] = question
        if request.user.is_authenticated:
            try:
                question_like = QuestionLike.objects.get(author=request.user, obj_id=id_)
                kwargs['question_rating_form'] = QuestionRatingForm(initial={
                    'rated': True
                }, instance=question_like)
            except QuestionLike.DoesNotExist:
                kwargs['question_rating_form'] = QuestionRatingForm()
        else:
            kwargs['question_rating_form'] = QuestionRatingForm()
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        id_ = kwargs['id']
        if request.is_ajax():
            return ajax_question(request, **kwargs)
        if not request.user.is_authenticated:
            response = redirect('app:login')
            response['Location'] += '?next=' + reverse('app:question', kwargs={
                'id': id_
            })
            return response
        question = get_object_or_404(Question, id=id_)
        answer_form = AnswerTheQuestionForm(data=request.POST, instance=Answer(author=request.user, question_id=id_))
        if answer_form.is_valid():
            answer = answer_form.save()
            answer.author.answer_added(question)
        kwargs['answer_form'] = answer_form
        return self.get_(request, id_, question, **kwargs)


class TopQuestionsView(PaginationView):
    template_name = 'top.html'

    def get(self, request, **kwargs):
        kwargs['pagination'] = cache.get('top_questions')
        return super().get(request, **kwargs)


class TagQuestionsView(PaginationView):
    template_name = 'tag.html'

    def get(self, request, **kwargs):
        kwargs['pagination'] = Question.objects.get_by_tag(get_object_or_404(QuestionTag, name=kwargs['name']))
        return super().get(request, **kwargs)


# AJAX.


def ajax_question(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Не авторизован.')
    id_ = kwargs['id']
    if request.POST.get('text'):
        if request.POST.get('answer_id'):  # комментарий к ответу
            comment_to_answer_form = CommentToAnswerForm(
                data=request.POST,
                instance=CommentToAnswer(answer_id=request.POST['answer_id'], author=request.user))
            if comment_to_answer_form.is_valid():
                comment_to_answer_form.save()
            else:
                return HttpResponseForbidden(comment_to_answer_form.errors.as_text())
        else:  # комментарий к вопросу
            comment_to_question_form = CommentToQuestionForm(
                data=request.POST,
                instance=CommentToQuestion(author=request.user, question_id=id_))
            if comment_to_question_form.is_valid():
                comment_to_question_form.save()
            else:
                return HttpResponseForbidden(comment_to_question_form.errors.as_text())
    elif request.POST.get('answer_id'):  # лайк на ответ
        pass
    else:  # лайк на вопрос
        try:
            question_rating_form = QuestionRatingForm(data=request.POST, initial={
                'rated': True
            }, instance=QuestionLike.objects.get(author=request.user, obj_id=id_))
        except QuestionLike.DoesNotExist:
            question_rating_form = QuestionRatingForm(
                data=request.POST,
                instance=QuestionLike(author=request.user, obj_id=id_))
        if question_rating_form.is_valid():
            try:
                question_rating_form.save()
            except:
                return HttpResponseForbidden('Обнаружена попытка спама или ошибка на сервере.')
        else:
            return HttpResponseForbidden(question_rating_form.errors.as_text())
    return HttpResponse()

# class BaseView(View):
#     template_name = 'index.html'
#
#     def get(self, request, **kwargs):
#         return render(request, self.template_name, kwargs)
#
#
# class PaginationView(BaseView):
#     template_name = 'index.html'
#
#     def get(self, request, **kwargs):
#         return super().get(request, **kwargs)
#
#
# class AskQuestionView(BaseView):
#     template_name = 'ask.html'
#
#     def get(self, request, **kwargs):
#         return super().get(request, **kwargs)
#
#     def post(self, request, **kwargs):
#         return super().get(request, **kwargs)
#
#
# class QuestionView(PaginationView):
#     template_name = 'question.html'
#
#     def get(self, request, **kwargs):
#         return super().get(request, **kwargs)
#
#     def post(self, request, **kwargs):
#         return super().get(request, **kwargs)
#
#
# def index(request):
#     return render(request, "index.html", {"questions": QUESTIONS})
#
#
# def ask(request):
#     return render(request, "ask.html")
#
#
# def question(request, i: int):
#     return render(request, "question_page.html", {"question": QUESTIONS[i]})

