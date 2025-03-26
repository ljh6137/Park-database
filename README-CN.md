# Rent Your Car: A System for Managing Car Leasing and Delivering Exceptional Convenience to Users

本文件包含中山大学数据库系统课程的最终作业。在此作业中，我们设计了一个管理汽车租赁的系统，具有简单的用户界面，使用户能够以便利的方式租用汽车，并且具有用户信息保护功能和并发访问控制功能。

## 演示
**简洁**的界面、**便利**的使用体验和**丰富**的信息

<img src="./paper/pic/demo_censor.gif" style="width:100%; height:auto;" alt="图片描述" />

## 快速开始

由于环境限制，该系统仅支持本地运行。

### 环境准备

我们使用 Django 开发该系统。
``` shell
pip install Django
```

### 本地部署

我们提供了脚本 ``init.sh`` 来帮助您更轻松地构建此系统。在运行 ``bash init.sh`` 之前，您需要将脚本中的 ``DB_USER="your_username"`` 和 ``DB_PASSWORD="your_password"`` 更改为您自己的用户名和密码。

然后运行以下命令，并在浏览器中访问 http://127.0.0.1:8000/management/。
```shell
python manage.py runserver
```

>注意：``init.sh`` 中的路径在不同的系统中可能会略有不同。

>当无法在shell中使用psql语句时，可以直接在创建数据库和关系表后，使用文件``management.sql``导入数据。
