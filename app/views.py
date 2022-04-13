from django.shortcuts import render

# Create your views here.

QUESTIONS = [
    {
        "title": f"Title {i}",
        "text": f"This is text for question #{i}",
        "number": i
    } for i in range(10)
]


def index(request):
    return render(request, "index.html", {"questions": QUESTIONS})


def ask(request):
    return render(request, "ask.html")


def question(request, i: int):
    return render(request, "question_page.html", {"question": QUESTIONS[i]})
