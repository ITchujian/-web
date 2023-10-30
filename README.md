



# 基于 `Flask` 与 `xhsAPI` 开发的小红书自动跑 web 后端

## 功能特性

- 对接基于 `vue2` 开发的**小红书自动跑 web **前端；
- 提供一系列小红书自动化操作爬虫的`创建`、`删除`、`监控`等接口。

## 技术栈

- Python 3.10.10
- Flask、Flask_socketio
- MySQL Ver 14.14 Distrib 5.7.43
- NodeJS v18.17.1

## 安装和运行

### 部署教程

- Git

  1. 安装 git

     ```bash
     yum update
     yum install -y git
     ```

  2. 克隆项目

     ```bash
     mkdir /projects
     cd /projects & mkdir xhsweb
     cd xhsweb
     git clone git@gitee.com:xiaogugyx/redbook-automation-flask.git
     ```

  3. 适当调整文件名称等

     ```bash
     mv redbook-automation-flask/ backend
     ```

- Python 3.10.10

  1. 安装 gcc

     ```bash
     yum install -y gcc
     ```
  
  2. 安装 openssl
  
     ```bash
     yum remove openssl
     cd /opt
     yum install -y wget
     wget https://www.openssl.org/source/openssl-1.1.1n.tar.gz --no-check-certificate
     tar -zxf openssl-1.1.1n.tar.gz
     cd openssl-1.1.1n
     ./config --prefix=/usr/local/openssl
     make -j 2
     make install
     ln -sf /usr/local/openssl/bin/openssl /usr/bin/openssl
     vim /etc/ld.so.conf  # 末尾添加 /usr/local/openssl/lib
     ldconfig -v
     openssl version
     ```
  
  3. 下载其他依赖
  
     ```bash
     yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
     yum install -y libffi-devel zlib1g-dev
     yum install zlib* -y
     ```
  
  4. 下载 Python 源码

     ```bash
     wget https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz
     ```

     当然，上述只是开个玩笑而已，我已经将 `Python 3.10.10` 的 `tgz` 包放置于仓库中，当使用 `git` 的 `clone` 命令后，将该包移动到其他地方进行下一步即可。
  
  5. 解压 & 编译 & 安装

     ```bash
     # 解压 tgz 包
     tar -zxf Python-3.10.10.tgz
     # 编译并安装
     cd Python-3.10.10
     sed -i 's/PKG_CONFIG openssl /PKG_CONFIG openssl11 /g' configure
     ./configure
     make
     make altinstall
     # 验证：提示相应版本即成功
     cd ..
     python3.10 --version
     # 删除解压后的文件夹
     rm -rf Python-3.10.10
     ```
  
- 安装 Python 的虚拟环境

  1. 安装
  
     ```bash
     pip install virtualenv
     ```
  
  2. 创建
  
     ```bash
     mkdir /envs
     virtualenv /envs/xhs --python=python3.10
     ```
  
  3. 激活方式
  
     ```bash
     source /envs/xhs/bin/activate
     ```
  
- 安装项目的依赖项

  ```bash
  # 先激活虚拟环境
  cd /projects/xhsweb/backend
  pip install -r requirements.txt  
  # 当然，xhsAPI 是我自己写的包，因此通过此途径无法直接安装，需要可以联系我，你可以先安装一下其他的
  pip install Flask==2.2.5 PyMySQL==1.1.0 DBUtils==3.0.3 flask_cors==4.0.0 flask_socketio==5.3.6
  pip insatll xhsAPI-2.0.0.tar.gz
  ```

- 安装 MySQL

  1. 安装 MySQL 的分支

     ```bash
     yum install -y mariadb-server
     ```

  2. 设置开机启动并启动服务

     ```bash
     systemctl enable mariadb
     systemctl start mariadb
     # 查看
     systemctl status mariadb
     # 出现 Active: active (running) 即可
     ```

  3. 账号初始化并执行sql

     ```sql
     cd /projects/xhsweb/backend
     mysql -u root -p
     # 导入项目数据库
     source redbook.sql;
     # 更新root密码
     UPDATE mysql.user SET password=password('<your-password>') WHERE mysql.user='root';
     FLUSH PRIVILEGES;
     # 创建用户
     INSERT INTO mysql.user(user, host, password) values ('normal', '%', password('<your-password>')); 
     FLUSH PRIVILEGES;
     # 赋予表权限
     GRANT ALL PRIVILEGES ON redbook.* to normal@'%';
     FLUSH PRIVILEGES;
     ```

     完成以上操作后你会发现，创建的用户 `normal` 在本地无需密码就能登录，为了安全性考虑，我们需要删除某些本地用户。

     ```sql
     SELECT User, Host, Password FROM mysql.user;
     """ input
     +--------+---------------+-------------------------------------------+
     | User   | Host          | Password                                  |
     +--------+---------------+-------------------------------------------+
     | root   | localhost     | *1880C4770E85923D54E015CA6FBCE031713FFC4A |
     | root   | vm-0-4-centos | *1880C4770E85923D54E015CA6FBCE031713FFC4A |
     | root   | 127.0.0.1     | *1880C4770E85923D54E015CA6FBCE031713FFC4A |
     | root   | ::1           | *1880C4770E85923D54E015CA6FBCE031713FFC4A |
     |        | localhost     |                                           |
     |        | vm-0-4-centos |                                           |
     | normal | %             | *1880C4770E85923D54E015CA6FBCE031713FFC4A |
     +--------+---------------+-------------------------------------------+
     """
     DELETE FROM mysql.user WHERE User='' and Password='';
     FLUSH PRIVILEGES;
     ```

- 安装 `uwsgi`
  
  1. 安装
  
     ```bash
     source /envs/xhs/bin/activate
     pip install uwsgi
     ```
  
  2. 基于 `uwsgi` 运行
  
     ```sh
     cd /projects/xhsweb/backend
     uwsgi --ini xhs_uwsgi.ini
     uwsgi --ini xhs_uwsgi.ini & # 后台运行
     ps -ef | grep xhs_uwsgi
     kill -9 <id>
     ```
  
     
  
  3. 
  
- 安装 `nginx`

  1. 安装

     ```sh
     yum install -y nginx
     ```

  2. 配置

     ```
     cd /etc/nginx/
     rm nginx.conf
     vim nginx.conf
     
     ```

     

  3. 

- 

### 运行步骤

提供运行项目的步骤，例如：

1. 执行数据库迁移：`python manage.py migrate`
2. 启动开发服务器：`python manage.py runserver`

## API 文档

如果项目提供 API 接口，可以在此处提供 API 文档的链接或说明。

## 贡献

说明如何贡献到项目中，例如：

- 提交 bug 报告
- 提交功能请求
- 提交修复补丁
- 其他贡献方式

## 版权和许可

指明项目的版权信息和许可证类型。

## 鸣谢

感谢对项目做出贡献的人员、组织或资源。

## 参考资料

提供与项目相关的参考资料链接或资源。