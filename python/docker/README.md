# 更新 Docker 镜像加速器

仅依赖 Python 3.8+ 标准库，适用于 Linux。程序读取 [DockerHub 仓库 README](https://github.com/dongyubin/DockerHub) 的有效镜像表格，排除失效列表和使用示例中的地址。

在仓库根目录执行：

```bash
sudo python3 python/docker/update_mirrors.py
```

程序依次执行：

1. 备份 `/etc/docker/daemon.json` 为同目录的 `yyyymmddhhmmss.daemon.json`，时间使用服务器本地时区。同一秒备份已存在则退出，不覆盖。
2. 按网页顺序提取地址、补全 HTTPS、去重。
3. 检测 `/v2/` 接口，取前 **最多 5 个**通过检测的地址；不足 5 个就使用实际数量。
4. 仅替换 `registry-mirrors`，保留其他 JSON 配置，原子写回文件。
5. 默认不修改 `data-root`：已有则保留，没有也不新增。仅传入 `--data-root 路径` 时新增或覆盖该字段。

配置不存在、JSON 无效、下载失败或没有可用地址时退出，原配置不变。配置已存在时备份会保留。检测只验证 Registry 接口响应，401 表示需要认证，不保证所有镜像都可拉取。

遇到 GitHub TLS 握手超时，程序会依次尝试 GitHub Raw、jsDelivr 和 GitHub raw 地址，最多两轮。jsDelivr 可能存在缓存。可以延长每次网络操作的超时时间：

```bash
sudo python3 python/docker/update_mirrors.py --timeout 30
```

如果服务器无法访问这些地址，在自己电脑下载该仓库的原始 `README.md` 并上传到服务器，然后运行：

```bash
sudo python3 python/docker/update_mirrors.py --readme-file ./README.md
```

此选项只跳过网页下载，仍会检测镜像地址；`--skip-check` 只跳过镜像检测，不解决网页下载超时。两者可组合使用。

如果只想按网页标注提取地址，不做网络检测：

```bash
sudo python3 python/docker/update_mirrors.py --skip-check
```

需要显式修改数据目录时（会新增或覆盖原 `data-root`）：

```bash
sudo python3 python/docker/update_mirrors.py --data-root /srv/docker
```

程序不自动重启 Docker。需要使配置生效时执行（会影响正在运行的服务）：

```bash
sudo systemctl restart docker
```

指定其他文件测试：

```bash
python3 python/docker/update_mirrors.py --config ./daemon.json
```

运行离线测试：

```bash
python3 -m unittest discover -s python/docker -p 'test_*.py'
```
