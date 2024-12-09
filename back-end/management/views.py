from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# from .models import 

# Create your views here.


def detail(request, question_id):
    return HttpResponse()




def login(request):
    # latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("login.html")
    return HttpResponse(template.render(None, request))