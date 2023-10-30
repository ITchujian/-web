#!/bin/bash

# 安装 node.js
curl -sL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 验证安装结果
node -v
npm -v
