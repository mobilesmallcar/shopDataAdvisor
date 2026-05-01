# Shop Data Advisor - CPU 部署镜像
FROM python:3.12-slim

WORKDIR /app

# 换国内 apt 源并安装系统依赖（gcc 用于编译某些 Python 包）
RUN sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' \
    /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' \
    /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制整个项目到容器（包含代码、配置、模型以及预构建的 .venv）
COPY . /app/

# 修复 .venv 中的 Python 解释器软链接。
# 宿主机上 uv 创建的 .venv/bin/python 可能是指向宿主机绝对路径的软链接，
# 在容器内会失效，因此重新链接到容器自带的 Python 3.12。
RUN rm -f /app/.venv/bin/python /app/.venv/bin/python3 /app/.venv/bin/python3.12 && \
    ln -s $(which python3.12) /app/.venv/bin/python && \
    ln -s $(which python3.12) /app/.venv/bin/python3 && \
    ln -s $(which python3.12) /app/.venv/bin/python3.12

# 暴露服务端口
EXPOSE 18083

# 使用容器内 .venv 的 Python 直接启动服务
CMD ["/app/.venv/bin/python", "main.py"]
