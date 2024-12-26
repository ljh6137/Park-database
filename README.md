## Rent Your Car: A System for Managing Car Leasing and Delivering Exceptional Convenience to Users

This repository contains the final assignment for the Database Systems course in SYSU. In this assignment, we design a system to manage car leasing with simple UI, enabling users to rent cars in a convenient way.

### Demo
**Convenient** to register and login.
![](paper\pic\login.png)
**Concise** page to manage the car you rent.
![](paper\pic\ui.png)
**Abundant** cars and **Convenient** for leasing.
![](paper\pic\homepage.png)

### Getting Started

Due to environmental constraints, the system can only be run locally. 

#### Environment Preparation

We use Django to develop this system.
``` shell
pip install Django
```

#### Lauch Demo Locally

We provide a script ``init.sh`` to help you build this system more easily. Before your ``bash init.sh``. You should change ``DB_USER="your_username"`` and ``DB_PASSWORD="your_password" `` to your own.

Then, run command and enter url http://127.0.0.1:8000/management/ in your browser.
```shell
python manage.py runserver
```

NOTICE: The path in ``init.sh`` may be subtly different in different systems.

### Acknowledgement

[GLM4](https://github.com/THUDM/GLM-4) generates some images used in the UI.

[ChatGPT-4o](https://openai.com/index/hello-gpt-4o/) collaborate on some codes.

### License