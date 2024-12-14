from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
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





def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('rent_car')  # 登录成功后跳转到用户仪表盘
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'management/login.html')

from django.shortcuts import render, redirect
from .models import Vehicle, Repository, Lease, Customer, Info
from django.contrib import messages

# 租车页面视图
def rent_car_view(request):
    # 获取所有可供租赁的车辆，使用 Info 来查找关联的 Repository
    available_vehicles = Vehicle.objects.filter(info_model__Car_ID__Is_leased=False)

    if request.method == 'POST':
        # 获取客户ID和所选车辆ID
        customer_id = request.POST['customer_id']
        vehicle_id = request.POST['vehicle_id']
        
        # 查找客户和车辆对象
        customer = Customer.objects.get(ID=customer_id)
        vehicle = Vehicle.objects.get(Model=vehicle_id)
        
        # 找到对应的 Repository 条目
        repository = Repository.objects.get(Car_ID=vehicle_id)

        # 检查车辆是否已经租赁
        if repository.Is_leased:
            messages.error(request, "This vehicle is already leased!")
            return redirect('rent_car')

        # 创建租赁记录
        Lease.objects.create(Car_ID=repository, ID=customer)
        
        # 更新仓库中的租赁状态
        repository.Is_leased = True
        repository.save()
        
        messages.success(request, "Vehicle leased successfully!")
        return redirect('rent_car')
    
    return render(request, 'management/rent_car.html', {'vehicles': available_vehicles})
