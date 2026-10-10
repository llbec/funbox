# PostgreSQL 部署

基于 Docker Compose 的 PostgreSQL 16 单容器部署，数据持久化到宿主机 `./data` 目录。

## 目录结构

```
postgreSQL/
├── docker-compose.yml   # 编排文件
├── .env.example         # 环境变量模板
├── .env                 # 实际配置（从模板复制，不提交 Git）
└── data/                # 数据持久化目录（bind mount，属主 999:999）
```

## 首次部署

```bash
# 1. 准备配置
cp .env.example .env
# 编辑 .env，至少改 POSTGRES_PASSWORD
vi .env

# 2. 准备数据目录（关键步骤，勿跳过）
mkdir -p data && sudo chown 999:999 data
# 999:999 是官方 postgres 镜像内部的 UID:GID
# 不 chown 的话容器启动时可能因无写权限而失败

# 3. 启动
sudo docker compose up -d

# 4. 验证
sudo docker compose ps
sudo docker compose logs -f postgres
# 健康检查通过后即可连接
```

## 日常运维

```bash
# 启动 / 停止 / 重启
sudo docker compose up -d
sudo docker compose stop
sudo docker compose restart

# 查看状态
sudo docker compose ps

# 查看日志
sudo docker compose logs -f postgres
sudo docker compose logs --tail 100 postgres

# 连接数据库（宿主机无需装 psql 客户端）
sudo docker exec -it postgres psql -U postgres -d appdb
# 或用密码远程连接
psql -h <服务器IP> -p 5432 -U postgres -d appdb
```

## 更新配置

### 改密码 / 端口 / 库名

改 `.env` 后需重建容器使环境变量生效：

```bash
vi .env
sudo docker compose up -d   # Compose 会检测变更并重建容器
```

> 注意：改 `POSTGRES_DB` / `POSTGRES_USER` **不会**对已有数据库生效——这两个变量仅在数据目录为空（首次初始化）时生效。要改库名/用户名必须先删数据重新部署（见下文「完全重新部署」），或进 psql 手动建库建用户。

### 升级 PostgreSQL 版本

```bash
# 1. 先备份
sudo docker exec postgres pg_dumpall -U postgres > backup_$(date +%Y%m%d).sql

# 2. 改镜像版本
vi docker-compose.yml   # image: postgres:16 → postgres:17

# 3. 停旧容器
sudo docker compose down

# 4. 升级数据目录（大版本升级需要，不能直接用旧 data 启动）
sudo docker run --rm -v "$PWD/data:/var/lib/postgresql/data" \
  -e POSTGRES_PASSWORD=changeme postgres:17 \
  # 详见官方文档的 pg_upgrade 流程，或用 pg_upgradecontainer
echo

# 5. 重新启动
sudo docker compose up -d
```

> 小版本升级（16.4 → 16.6）直接改 tag + `up -d` 即可，无需迁移数据。

## 删除容器与数据

### 仅删除容器（保留数据）

```bash
sudo docker compose down
# data/ 目录保留，重新 up -d 后数据原样恢复
```

### 删除容器 + 匿名卷（仍保留 bind mount 数据）

```bash
sudo docker compose down -v
# -v 只删 compose 定义的命名卷；本配置用的是 bind mount，data/ 不受影响
```

### 彻底删除（容器 + 数据，不可恢复）

```bash
# 1. 停并删容器
sudo docker compose down

# 2. 删除宿主机上的数据目录（数据永久丢失！）
sudo rm -rf data/

# 3. 确认
ls -la   # data/ 应已不存在
```

> 删除前建议先备份：`sudo docker exec postgres pg_dumpall -U postgres > backup.sql`

## 完全重新部署

适用场景：换库名/用户名、升级大版本、数据损坏重来。

```bash
# 1. 备份（如果旧数据还需要）
sudo docker exec postgres pg_dumpall -U postgres > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 停并删容器
sudo docker compose down

# 3. 删除数据目录
sudo rm -rf data/

# 4. 修改 .env（如需要换库名/用户名/密码）
vi .env

# 5. 重新准备数据目录
mkdir -p data && sudo chown 999:999 data

# 6. 启动（首次启动会按 .env 初始化新库/用户）
sudo docker compose up -d

# 7. 如需导入旧数据
sudo docker exec -i postgres psql -U postgres -d postgres < backup_*.sql
```

## 常见问题

### `ls data/` 提示 Permission denied

正常现象。`data/` 属主是 `999:999`（容器内 postgres 用户），宿主机普通用户无权访问。

```bash
# 用 sudo 查看
sudo ls -la data/

# 需要直接读写，把当前用户加入 999 组（重新登录后生效）
sudo usermod -aG 999 $USER
```

> **切勿** `sudo chown -R $USER:$USER data/`，改回普通用户后容器内 postgres（UID 999）将失去写权限，重启后无法启动。

### 宿主机 `psql` 报 `You must install at least one postgresql-client-<version>`

宿主机没装 psql 客户端。两种方案：

```bash
# 方案 A：进容器用自带 psql（推荐，零安装）
sudo docker exec -it postgres psql -U postgres

# 方案 B：宿主机装客户端
sudo apt install postgresql-client-16
```

### `docker compose down -v` 后 data/ 还在

这是预期行为。`-v` 只删 Docker 管理的命名卷，而本配置用 `./data` 是 bind mount（宿主机目录），不属于 Docker 卷。要删数据必须手动 `sudo rm -rf data/`。

### 改了 .env 但没生效

`POSTGRES_DB` / `POSTGRES_USER` 仅在数据目录为空时生效。已有数据时要改这两个值，需走「完全重新部署」流程，或进 psql 手动操作。

> AI生成
