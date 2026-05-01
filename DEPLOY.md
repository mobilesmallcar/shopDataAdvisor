# Shop Data Advisor 服务器部署流程

> 部署目标：Ubuntu 服务器 + Docker Compose  
> 代码仓库：https://gitee.com/agents_3/shop-data-advisor.git  
> 分支：`cpu-部署`  
> 部署路径：`/opt/projects/shopDataAdvisor`

## 端口说明

| 端口 | 用途 | 说明 |
|------|------|------|
| **18083** | FastAPI 服务端口 | 前端页面 + Swagger 文档 |
| **13306** | MySQL | 外部客户端连接 |
| **19200** | Elasticsearch | 外部客户端连接 |
| **16333** | Qdrant HTTP | 外部客户端连接 |
| **16334** | Qdrant gRPC | 外部客户端连接 |

---

## 一、环境准备（服务器上执行）

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

> 装完后退出 SSH 重新登录，让 docker 用户组生效。

---

## 二、拉取代码

```bash
cd /opt
sudo git clone -b cpu-部署 https://gitee.com/agents_3/shop-data-advisor.git projects/shopDataAdvisor
sudo chown -R $(whoami):$(whoami) projects/shopDataAdvisor
cd projects/shopDataAdvisor
```

---

## 三、宿主机构建 .venv

```bash
# 构建虚拟环境（Linux x86_64）
uv sync --no-dev

# 下载 Embedding 模型（首次需要，约 100MB）
python scripts/download_embedding.py --model BAAI/bge-small-zh-v1.5
```

> 这一步在**宿主机**执行，`.venv`（约 1.5G）会被 Docker 镜像复制进去，避免容器内重复下载。  
> **必须在 Linux 服务器上**执行 `uv sync`，Windows 的 `.venv` 不能复制到 Linux 容器运行。

---

## 四、启动容器

```bash
cd docker
sudo docker compose up -d --build
```

首次启动会自动完成：
1. MySQL 初始化（`meta.sql` + `dw.sql`）
2. Elasticsearch 启动
3. Qdrant 启动
4. 应用容器启动（复制宿主机的 `.venv`，修复软链接，加载模型）

> `--build` 首次必须加；后续如果只是改代码，不需要加。

访问验证：
- 前端页面：`http://<服务器IP>:18083`
- Swagger 文档：`http://<服务器IP>:18083/docs`

---

## 五、后续更新代码

### 5.1 只改前端/后端代码（不涉及依赖）

```bash
cd /opt/projects/shopDataAdvisor
git pull origin cpu-部署
sudo docker compose -f docker/docker-compose.yaml restart app
```

> `docker-compose.yaml` 已挂载 `./app`、`./main.py`、`./prompts`、`./scripts`，重启容器即可加载最新代码，**不需要重新 build 镜像**。

### 5.2 改了依赖（pyproject.toml / uv.lock）

```bash
cd /opt/projects/shopDataAdvisor
git pull origin cpu-部署
uv sync --no-dev              # 重新安装依赖
sudo docker compose -f docker/docker-compose.yaml down
sudo docker compose -f docker/docker-compose.yaml up -d --build
```

> 依赖变更后必须重新 build 镜像，因为 `.venv` 是构建时 COPY 进镜像的，不是挂载的。

### 5.3 改了配置（`docker/app_config.yaml`）

```bash
# 直接修改文件即可，已挂载为 volume
vim docker/app_config.yaml
sudo docker compose -f docker/docker-compose.yaml restart app
```

---

## 六、分支说明

| 分支 | 用途 |
|------|------|
| `master` | 原始代码（CUDA 版 PyTorch） |
| `cpu-部署` | **当前部署分支**（CPU 版 PyTorch + Docker 配置 + Linux 适配） |

所有部署相关的修改都在 `cpu-部署` 分支，后续更新代码时切记拉取这个分支。

---

## 七、常用命令速查

```bash
# 查看容器状态
sudo docker ps | grep shopDataAdvisor

# 查看实时日志
sudo docker logs -f shopDataAdvisor-app

# 停止全部服务
sudo docker compose -f docker/docker-compose.yaml down

# 停止并清数据（慎用）
sudo docker compose -f docker/docker-compose.yaml down -v

# 启动/重启
sudo docker compose -f docker/docker-compose.yaml up -d
sudo docker compose -f docker/docker-compose.yaml restart app

# 进入容器排查
sudo docker exec -it shopDataAdvisor-app bash
```

---

## 八、已知注意事项（随口提）

- 容器内 FastAPI 监听的是 `0.0.0.0:18083`，不是 `127.0.0.1`
- `.venv` 是宿主机预构建后 COPY 进镜像的，所以**必须在 Linux 服务器上**执行 `uv sync`
- 修改 `docker/docker-compose.yaml` 后要用 `down && up -d`，`restart` 不会重新读取配置
- 原 `uv.lock` 是 Windows 环境下生成的，Linux 上会被忽略，`uv sync` 会自动重新生成
- 如果 `scripts/start.sh` 报 `bad interpreter`，执行 `sed -i 's/\r$//' scripts/start.sh` 修复换行符
