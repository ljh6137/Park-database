
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, Repository, Lease, Customer, Info
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
# from .models import 
import json

# Create your views here.


# def detail(request, question_id):
#     return HttpResponse()



# management/views.py
from django.shortcuts import render



def register(request):
    if request.method == 'GET':
        return render(request, 'management/register.html')
    
    if request.method == 'POST':
        # print(1)
        # 获取提交的用户名和密码
        username = request.POST['username']
        password = request.POST['password']
        
        # 检查用户名是否已经存在
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another one.')
            return render(request, 'management/register.html')
        
        # 创建用户并加密密码
        user = User.objects.create_user(username=username, password=password)
        
        # 创建对应的 Customer 实例
        customer = Customer.objects.create(user=user, ID=username, name=username, contact="")  # 可以根据需要设置默认的 contact
        
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
            return redirect('homepage')  # 登录成功后跳转到用户仪表盘
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'management/login.html')

@login_required
def rent_car_view(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')

        try:
            # 获取当前登录的用户来查找关联的 Customer 实例
            customer = get_object_or_404(Customer, user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "You need to complete your customer profile before renting a car.")
            return redirect('profile')  # 重定向到用户个人资料页面或其他页面

        try:
            vehicle = Vehicle.objects.get(Model=vehicle_id)
        except Vehicle.DoesNotExist:
            messages.error(request, "Vehicle not found.")
            return redirect('rent_car')

        try:
            repository = Repository.objects.get(Car_ID=vehicle_id)
        except Repository.DoesNotExist:
            messages.error(request, "Repository entry for vehicle not found.")
            return redirect('rent_car')

        if repository.Is_leased:
            messages.error(request, "This vehicle is already leased!")
            return redirect('rent_car')

        Lease.objects.create(Car_ID=repository, ID=customer)
        repository.Is_leased = True
        repository.save()

        messages.success(request, "Vehicle leased successfully!")
        return redirect('rent_car')

    available_vehicles = Vehicle.objects.filter(info_model__Car_ID__Is_leased=False)
    return render(request, 'management/rent_car.html', {'vehicles': available_vehicles})

def ui(request):
    return render(request, 'management/UI.html')  # 创建并渲染一个主页模

@login_required
def rented_vehicles_view(request):
    # 获取当前登录的用户
    user = request.user

    try:
        # 获取该用户的 Customer 对象，假设用户模型和 Customer 一对一关联
        customer = Customer.objects.get(ID=user.username)  # 假设用户ID与Customer模型的ID字段匹配
    except Customer.DoesNotExist:
        customer = None

    if customer:
        # 获取该用户租赁的所有车辆
        leases = Lease.objects.filter(ID=customer)
        rented_vehicles = []
        for lease in leases:
            vehicle = lease.Car_ID.Model  # 获取租赁车辆的模型
            rented_vehicles.append(vehicle)
    else:
        rented_vehicles = []

    return render(request, 'management/rented_vehicles.html', {'rented_vehicles': rented_vehicles})

def home(request):
    return render(request, 'management/UI.html')

# def car_list(request):
#     # print(1)
#     vehicles = Vehicle.objects.all()  # 查询所有车辆信息
#     if vehicles.exists():
#         data = list(vehicles.values("Model"))  # 转换为 JSON 格式
#         return JsonResponse({"status": "success", "data": data})
#     else:
#         return JsonResponse({"status": "empty", "message": "暂无车辆信息"})
    
def get_repository_by_name(request):
    if request.method == "GET":
        name = request.GET.get("name")  # 获取点击的 name 参数
        try:
            # 查询 Vehicle 表中匹配的 name，并关联查询 Repository 表
            vehicle = Vehicle.objects.get(name=name)
            repositories = Repository.objects.filter(model=vehicle)
            # 构建返回数据
            data = list(repositories.values("id", "description", "created_at"))
            return JsonResponse({"status": "success", "data": data})
        except Vehicle.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Vehicle not found"})
        
# def get_vehicle_details(request):
#     """
#     查询车辆的详细信息：Car_ID、Is_leased 和 price。
#     """
#     if request.method == "GET":
#         car_name = request.GET.get("name")  # 获取车辆名称

#         if not car_name:
#             return JsonResponse({"status": "error", "message": "车辆名称不能为空"})

#         # 执行 SQL 查询
#         query = """
#             SELECT a.Car_ID, a.Is_leased, b.price
#             FROM Repository a, Vehicle b
#             JOIN info c ON b.Model = c.Model
#             WHERE a.Car_ID = c.Car_ID AND b.name = %s
#         """
#         with connection.cursor() as cursor:
#             cursor.execute(query, [car_name])
#             rows = cursor.fetchall()

#         # 将查询结果转换为 JSON 格式
#         data = [
#             {"Car_ID": row[0], "Is_leased": row[1], "price": row[2]}
#             for row in rows
#         ]

#         if data:
#             return JsonResponse({"status": "success", "data": data})
#         else:
#             return JsonResponse({"status": "empty", "message": "未找到相关车辆信息"})

def get_vehicles(request):
    vehicles = Vehicle.objects.all()
    if vehicles.exists():
        data = list(vehicles.values("Model"))
        return JsonResponse({"status": "success", "data": data})
    else:
        return JsonResponse({"status": "empty", "message": "暂无车辆信息"})

# 获取具体车辆的详细信息
def get_vehicle_details(request):
    if request.method == "GET":
        car_name = request.GET.get("name")
        if not car_name:
            return JsonResponse({"status": "error", "message": "车辆名称不能为空"})

        query = """
            SELECT a."Car_ID", a."Is_leased", b."Price"
            FROM management_repository a, management_vehicle b
            JOIN management_info c ON b."Model" = c."Model_id"
            WHERE a."Car_ID" = c."Car_ID_id" AND b."Model" = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [car_name])
            rows = cursor.fetchall()

        data = [
            {"Car_ID": row[0], "Is_leased": row[1], "Price": row[2]}
            for row in rows
        ]

        if data:
            return JsonResponse({"status": "success", "data": data})
        else:
            return JsonResponse({"status": "empty", "message": "未找到车辆详情"})
        
@login_required
# def homepage(request):
#     # 假设租赁车辆从数据库获取
#     rented_cars = [
#         {"license_plate": "ABC123", "model": "Toyota Camry", "price": 300},
#         {"license_plate": "XYZ456", "model": "Honda Accord", "price": 350},
#     ]
#     return render(request, 'management/homepage.html', {'rented_cars': rented_cars})
def homepage(request):
    # 检查用户是否已登录
    if request.user.is_authenticated:
        # 获取当前用户的租赁车辆信息
        rented_cars = Lease.objects.filter(ID__user=request.user).select_related('Car_ID')
        
        # 格式化租赁车辆数据
        rented_cars_data = [
            {
                "license_plate": lease.Car_ID.Model,  # 假设车型(Model)为车牌号
                "model": lease.Car_ID.Model,
                "price": lease.Car_ID.Price,
            }
            for lease in rented_cars
        ]
    else:
        rented_cars_data = []

    # 渲染模板并传递租赁车辆数据
    return render(request, 'management/homepage.html', {'rented_cars': rented_cars_data})

@login_required
def lease_vehicle(request):
    """
    租赁车辆视图：更新车辆状态并创建租赁记录
    """
    if request.method == "POST":
        try:
            # 接收 JSON 数据
            data = json.loads(request.body)
            car_id = data.get("car_id")  # 获取车牌号
            user_id = request.user.username  # 获取当前用户ID
            if not car_id:
                return JsonResponse({"status": "error", "message": "车辆ID不能为空"})

            # 更新车辆租赁状态
            update_query = """
                UPDATE management_repository
                SET "Is_leased" = TRUE
                WHERE "Car_ID" = %s
            """
            # 插入租赁记录
            insert_query = """
                INSERT INTO management_lease ("ID_id","Car_ID_id")
                VALUES (%s, %s)
            """
            
            print(car_id)
            with connection.cursor() as cursor:
                cursor.execute(update_query, [car_id])  # 更新车辆状态
                cursor.execute(insert_query, [user_id, car_id])  # 插入租赁记录
            
            # print(1)
            return JsonResponse({"status": "success", "message": "车辆租赁成功！"})

        except Exception as e:
            print(f"Error leasing vehicle: {e}")
            return JsonResponse({"status": "error", "message": "租赁失败，请稍后再试。"})

    return JsonResponse({"status": "error", "message": "无效的请求方法"})