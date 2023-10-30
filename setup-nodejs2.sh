#!/bin/bash

# 安装 node.js
cd /root
wget https://nodejs.org/dist/v18.17.1/node-v18.17.1-linux-x64.tar.xz
tar xvf node-v18.17.1-linux-x64.tar.xz
mv node-v18.17.1-linux-x64 ~
ln -s /root/node-v18.17.1-linux-x64/bin/node /usr/local/bin/node
ln -s /root/node-v18.17.1-linux-x64/bin/npm /usr/local/bin/npm

# 安装 gcc-8
yum install centos-release-scl
yum install -y devtoolset-8-gcc devtoolset-8-gcc-c++ devtoolset-8-binutils
echo "source /opt/rh/devtoolset-8/enable" >> /etc/profile
source /etc/profile

# 安装 make4.3
wget https://ftp.gnu.org/gnu/make/make-4.3.tar.gz
tar -xzvf make-4.3.tar.gz && cd make-4.3/
./configure  --prefix=/usr/local/make
make && make install
cd /usr/bin/ && mv make make.bak
ln -sv /usr/local/make/bin/make /usr/bin/make

# 安装 glibc-2.28
wget http://ftp.gnu.org/gnu/glibc/glibc-2.28.tar.gz
tar xf glibc-2.28.tar.gz
cd glibc-2.28/ && mkdir build && cd build
../configure --prefix=/usr --disable-profile --enable-add-ons --with-headers=/usr/include --with-binutils=/usr/bin
make && make install

# 安装 libstdc++.so.6
yum install libstdc++.so.6 -y
wget http://ftp.de.debian.org/debian/pool/main/g/gcc-8/libstdc++6_8.3.0-6_amd64.deb
ar -x libstdc++6_8.3.0-6_amd64.deb
tar -xvf data.tar.xz
cp usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25 /usr/lib64/
rm -rf /usr/lib64/libstdc++.so.6
ln -s /usr/lib64/libstdc++.so.6.0.25 /usr/lib64/libstdc++.so.6

echo "All dependencies have been installed successfully!"
echo "Node.js version: $(node -v)"
echo "npm version: $(npm -v)"