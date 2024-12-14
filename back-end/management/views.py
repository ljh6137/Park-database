from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
# from .models import 

# Create your views here.


# def detail(request, question_id):
#     return HttpResponse()



# management/views.py
from django.shortcuts import render

# def register(request):
#     if request.method == 'GET':
#         return render(request, 'management/register.html')
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         # print(1)
#         # create user
        
#         messages.success(request, 'Registration successful!')
#         return render(request, 'management/register.html')
#         # return redirect('login')
#     # return render(request, 'management/register.html')  # 渲染登录模板



from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

def register(request):
    if request.method == 'GET':
        return render(request, 'management/register.html')
    
    if request.method == 'POST':
        # 获取提交的用户名和密码
        username = request.POST['username']
        password = request.POST['password']
        
        # 检查用户名是否已经存在
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another one.')
            return render(request, 'management/register.html')
        
        # 创建用户并加密密码
        user = User.objects.create_user(username=username, password=password)
        
        # 提示用户注册成功
        messages.success(request, 'Registration successful! Please log in.')
        
        # 注册成功后，跳转到登录页面
        return redirect('login')
    
    return render(request, 'management/register.html')



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # 登录成功后跳转到用户仪表盘
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'management/login.html')

def dashboard(request):
    return render(request, 'management/dashboard.html')