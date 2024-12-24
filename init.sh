#!/bin/bash

# 设置数据库相关变量
DB_NAME="demo"
DB_USER="your_username"  # 修改为创建数据库的用户
DB_PASSWORD="your_password"  # 修改为数据库的密码
DATA_FILE="/path/to/your/data.sql"  # 数据文件路径，假设为 SQL 文件

# 创建数据库并赋予权限
echo "创建数据库 $DB_NAME..."
psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

echo "赋予 $DB_USER 对数据库 $DB_NAME 的所有权限..."
psql -U $DB_USER -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 导入数据
echo "开始导入数据..."
psql -U $DB_USER -d $DB_NAME -f $DATA_FILE

echo "数据库 $DB_NAME 创建和数据导入完成！"
