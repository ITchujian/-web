



# 小红书自动跑 web 后端

## 一、功能特性

- 对接基于 `vue2` 开发的 **小红书自动跑 web** 前端；

- 提供一系列小红书自动化操作爬虫的`创建`、`删除`、`监控`等接口。

  ![责任链](https://gitee.com/xiaogugyx/drawing-bed/raw/master/%E8%B4%A3%E4%BB%BB%E9%93%BE.jpg)

## 二、技术栈

- Python 3.10.10
- Flask、Flask_socketio
- MySQL Ver 14.14 Distrib 5.7.43
- NodeJS v18.17.1

## 三、安装和运行

**部署环境**： 腾讯云轻量级应用服务器 + CentOS 7.6 64bit

**项目目录**：`/projects/xhsweb/frontend` 存放 vue 打包后的项目，`/projects/xhsweb/backend` 存放 Flask 项目（当前仓库）

### 3.1 安装 `Git`

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
   # 克隆后续需要的服务器应用安装的一些工具
   git clone git@gitee.com:xiaogugyx/server-deployment-kit.git
   ```

3. 适当调整文件名称等

   ```bash
   mv redbook-automation-flask/ backend
   mv server-deployment-kit/ serverkit
   ```

### 3.2 安装 `node.js`

  此处顶级大坑，无力吐槽~~

  1. 安装 nodejs

     ```bash
     cd /projects/serverkit/nodejs
     tar xvf node-v18.17.1-linux-x64.tar.xz 
     mv node-v18.17.1-linux-x64 ~
     ln -s /root/node-v18.17.1-linux-x64/bin/node /usr/local/bin/node
     ln -s /root/node-v18.17.1-linux-x64/bin/npm /usr/local/bin/npm
     # 以上来源于 腾讯云 官方的文档 https://cloud.tencent.com/document/product/213/38237
     # 不出意外的话就要出意外了
     node -v
     """ error：
     node: /lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)
     node: /lib64/libc.so.6: version `GLIBC_2.25' not found (required by node)
     node: /lib64/libc.so.6: version `GLIBC_2.28' not found (required by node)
     node: /lib64/libstdc++.so.6: version `CXXABI_1.3.9' not found (required by node)
     node: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by node)
     node: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by node)
     """
     ```

  2. 安装 gcc-8

     ```bash
     yum install centos-release-scl
     yum install -y devtoolset-8-gcc devtoolset-8-gcc-c++ devtoolset-8-binutils
     echo "source /opt/rh/devtoolset-8/enable" >> /etc/profile
     source /etc/profile
     ```

  3. 安装 make4.3

     ```bash
     cd /projects/serverkit/nodejs
     # 或者 wget https://ftp.gnu.org/gnu/make/make-4.3.tar.gz
     tar -xzvf make-4.3.tar.gz && cd make-4.3/
     ./configure  --prefix=/usr/local/make
     make && make install
     cd /usr/bin/ && mv make make.bak
     ln -sv /usr/local/make/bin/make /usr/bin/make
     ```

  4. 安装 glibc-2.28

     ```bash
     cd /projects/serverkit/nodejs
     # 或者 wget http://ftp.gnu.org/gnu/glibc/glibc-2.28.tar.gz
     tar xf glibc-2.28.tar.gz 
     cd glibc-2.28/ && mkdir build  && cd build
     ../configure --prefix=/usr --disable-profile --enable-add-ons --with-headers=/usr/include --with-binutils=/usr/bin
     ```

  5. 安装 libstdc++.so.6

     ```bash
     yum install libstdc++.so.6 -y
     cd /projects/serverkit/nodejs
     # 或者 wget http://ftp.de.debian.org/debian/pool/main/g/gcc-8/libstdc++6_8.3.0-6_amd64.deb
     ar -x libstdc++6_8.3.0-6_amd64.deb
     tar -xvf data.tar.xz
     cp usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25 /usr/lib64/
     rm -rf /usr/lib64/libstdc++.so.6
     ll /usr/lib64/libstd*
     ln -s /usr/lib64/libstdc++.so.6.0.25 /usr/lib64/libstdc++.so.6
     ```

  6. Done.

     ```bash
     node -v
     npm -v
     ```

     但是，压根没有必要照着上面的做，可以运行我提供的两个 .sh 文件，`setup-nodejs1.sh` 是利用了 nodejs 官方自动安装的脚本，`setup-nodejs2.sh` 则是上述手动安装补坑的脚本文件，执行 sh 文件前务必记得修改好权限。

     ```bash
     # 接下来不要忘记安装依赖哦
     cd /projects/serverkit/nodejs
     npm install jsdom
     ```

### 3.3 安装 `Python3.10`

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
   ./config --prefix=/usr/local/openssl shared zlib 
   make && make install
   echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/openssl/lib" >>  /etc/profile
   source /etc/profile
   ```
   
3. 下载其他依赖

   ```bash
   yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
   yum install -y libffi-devel zlib1g-dev
   yum install zlib* -y
   ```

4. 下载 Python 源码

   ```bash
   cd /projects/serverkit/python
   # 或者 wget https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz
   ```
   
5. 解压 & 编译 & 安装

   ```bash
   # 解压 tgz 包
   tar -zxf Python-3.10.10.tgz
   # 编译并安装
   cd Python-3.10.10
   ./configure --prefix=/usr/local//python3 --with-openssl=/usr/local//openssl 
   make && make install
   # 链接
   ln -s /usr/local/python3/bin/pip3  /usr/bin/pip
   ln -s /usr/local/python3/bin/python3  /usr/bin/python
   ln -s /usr/local/python3/bin/python3  /usr/bin/python3    
   # 验证
   cd ..
   python
   # 输入以下代码 无报错则完成
   import ssl
   import _ssl
   ```

### 3.4 安装虚拟环境

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
  # 当然，还有一个 xhsAPI 是我自己写的包，通过此途径无法直接安装，需要可以联系我
  pip insatll xhsAPI-2.0.0.tar.gz
  ```

### 3.5 安装 `MySQL`

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

### 3.6 安装 `uwsgi`

  1. 安装

     ```bash
     source /envs/xhs/bin/activate
     pip install uwsgi
     ```

  2. 基于 `uwsgi` 运行

     ```sh
     cd /projects/serverkit/
     chmod 777 uwsgi-tool.sh
     ./uwsgi-tool.sh start
     ```

  3. 重启和关闭

     ```bash
     ./uwsgi-tool.sh restart
     ./uwsgi-tool.sh stop
     ```

  ### 3.7 安装 `nginx`

  1. 安装 nginx

     ```sh
     yum install -y nginx
     ```

  2. 覆盖原有配置

     ```bash
     cp /projects/serverkit/nginx.conf /etc/nginx/nginx.conf
     ```

  3. 设置开机启动并启动

     ```bash
     systemctl enable nginx
     systemctl start nginx
     ```


## 四、API 文档

**base api prefix**: api/spider

### 4.1 获取二维码

- 请求方法：GET
- 路由：/qrcode
- 功能：获取登录二维码
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "获取二维码成功",
      "data": "二维码数据"
  }
  ```

### 4.2 获取二维码状态

- 请求方法：GET
- 路由：/qrcode/state
- 参数：
  - qrId：二维码ID
  - code：验证码
- 功能：获取登录二维码的状态
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "等待扫码",
      "data": "登录信息"
  }
  ```
  或
  ```json
  {
      "success": true,
      "msg": "登录成功",
      "data": "登录信息"
  }
  ```
  或
  ```json
  {
      "success": true,
      "msg": "二维码已过期",
      "data": {}
  }
  ```
  或
  ```json
  {
      "success": true,
      "msg": "未知错误呀",
      "data": {}
  }
  ```

### 4.3 创建机器爬虫

- 请求方法：POST
- 路由：/create
- 参数：表单数据包含机器爬虫的相关信息
- 功能：创建机器爬虫
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "机器爬虫创建成功",
      "data": {
          "机器爬虫的相关信息"
      }
  }
  ```

### 4.4 获取机器爬虫列表

- 请求方法：GET
- 路由：/load
- 功能：获取机器爬虫列表
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "机器爬虫列表获取成功",
      "data": [
          {
              "机器爬虫1的相关信息"
          },
          {
              "机器爬虫2的相关信息"
          },
          ...
      ]
  }
  ```

### 4.5 删除机器爬虫

- 请求方法：GET
- 路由：/delete
- 参数：sid（机器爬虫ID）
- 功能：删除指定ID的机器爬虫
- 返回结果：与获取机器爬虫列表的返回结果相同

### 4.6 设置机器爬虫状态

- 请求方法：POST
- 路由：/set_state
- 参数：
  - sid：机器爬虫ID
  - run：运行状态（true表示激活，false表示暂停）
- 功能：设置机器爬虫的运行状态
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "已激活",
      "data": {}
  }
  ```
  或
  ```json
  {
      "success": true,
      "msg": "已暂停",
      "data": {}
  }
  ```

### 4.7 获取敏感词列表

- 请求方法：GET
- 路由：/sensitive_words
- 功能：获取敏感词列表
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "获取敏感词成功",
      "data": [
          "敏感词1",
          "敏感词2",
          ...
      ]
  }
  ```

### 4.8 获取配置信息

- 请求方法：GET
- 路由：/configure/get
- 功能：获取机器爬虫的配置信息
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "获取配置成功",
      "data": {
          "配置字段1": "值1",
          "配置字段2": "值2",
          ...
      }
  }
  ```

### 4.9 保存配置信息

- 请求方法：POST
- 路由：/configure/set
- 参数：表单数据包含配置信息
- 功能：保存机器爬虫的配置信息
- 返回结果：
  ```json
  {
      "success": true,
      "msg": "保存配置成功",
      "data": {
          "配置字段1": "新值1",
          "配置字段2": "新值2",
          ...
      }
  }
  ```

## 参考资料

1. [How to install gcc8 using devtoolset-8-gcc](https://stackoverflow.com/questions/53310625/how-to-install-gcc8-using-devtoolset-8-gcc)
2. [flask-socketio on uWSGI](https://stackoverflow.com/questions/62078367/flask-socketio-on-uwsgi)
3. [Centos安装python3导入ssl时解决 ModuleNotFoundError: No module named ‘_ssl‘问题](https://blog.csdn.net/qq_39715000/article/details/125009276)