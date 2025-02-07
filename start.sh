#!/bin/bash

# 激活虚拟环境（如果使用）
source .venv/bin/activate

# 启动Gunicorn
gunicorn -c gunicorn.conf.py app:app 