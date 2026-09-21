# Linux 部署 Mihomo

参考[原文](https://www.celyn-blog.xyz/posts/ubuntu-mihomo-proxy/)。以下以 **Ubuntu / Debian、x86_64** 为例，使用有 sudo 权限的用户，按顺序在同一个终端执行。使用普通 HTTP / SOCKS 代理，不开启 TUN。

## 1. 下载

安装所需工具：

```bash
sudo apt update
sudo apt install -y curl gzip nano
mkdir -p ~/mihomo-install
cd ~/mihomo-install
```

从[官方 Releases](https://github.com/MetaCubeX/mihomo/releases/latest)下载。以下使用 2026-09-21 查询到的最新稳定版 `v1.19.31`：

```bash
curl -fL https://github.com/MetaCubeX/mihomo/releases/download/v1.19.31/mihomo-linux-amd64-compatible-v1.19.31.gz -o mihomo.gz
```

如果 `uname -m` 输出 `aarch64`，将下载命令中的 `amd64-compatible` 换成 `arm64`。

## 2. 解压

```bash
gzip -df mihomo.gz
```

## 3. 放入 PATH 目录

```bash
sudo install -m 755 mihomo /usr/local/bin/mihomo
export PATH="/usr/local/bin:$PATH"
mihomo -v
```

显示版本信息后继续。

## 4. 创建配置文件

```bash
sudo mkdir -p /etc/mihomo
sudo chown "$(id -un):$(id -gn)" /etc/mihomo
chmod 700 /etc/mihomo
touch /etc/mihomo/config.yaml
chmod 600 /etc/mihomo/config.yaml
```

## 5. 导入配置

推荐使用本目录的订阅脚本。先编辑脚本旁的 `deploy/mihomo/config.yaml`，设置端口、日志、控制器和面板等本地参数，然后在仓库根目录执行：

```bash
sudo bash deploy/mihomo/subscribe.sh
```

按提示粘贴 **Clash / Mihomo YAML 订阅 URL**。脚本将订阅与本地模板合并为单个 `/etc/mihomo/config.yaml`，不再使用单独的节点文件。

- 订阅中的 `proxies`、`proxy-groups`、`rules` 及本地未定义的字段会保留。
- 本地与订阅的同名顶层字段，以本地整个字段为准。例如本地 `mixed-port: 7890` 覆盖订阅的 `9981`；本地定义 `dns` 时会替换订阅的整个 `dns` 块。
- 支持常规块式 YAML（顶层键不加引号），也支持 Base64 编码的 YAML。URI 节点列表无法直接合并，请使用服务商提供的 Clash / Mihomo YAML 链接。
- 写入后执行 `mihomo -t -d /etc/mihomo`，失败自动恢复原配置，首次生成失败则移除无效文件。成功时保留旧配置备份。

本地模板不会被修改。更新订阅时重新运行同一命令即可，修改本地设置也应编辑模板。脚本不会启动或重载进程；成功后跳到第 6 节启动。模板已包含 MetaCubeXD 设置，访问方式见第 7 节。

如果要保留服务商完整配置，使用下面的手动导入方式：

复制执行后，粘贴自己的 **Clash / Mihomo YAML 订阅链接**并按回车：

```bash
read -r -p '请粘贴订阅链接：' MIHOMO_SUB_URL
curl -fL "$MIHOMO_SUB_URL" -o /etc/mihomo/config.download.yaml && \
  install -m 600 /etc/mihomo/config.download.yaml /etc/mihomo/config.yaml
unset MIHOMO_SUB_URL
```

打开配置：

```bash
nano /etc/mihomo/config.yaml
```

将下面的字段合并到配置中：已有同名字段就修改，没有则添加。保留订阅里的节点、代理组和规则，**不要用下面片段替换整个文件**。

```yaml
mixed-port: 7890
allow-lan: false
mode: rule
external-controller: 127.0.0.1:9090
tun:
  enable: false
```

按 `Ctrl+O`、回车保存，按 `Ctrl+X` 退出。检查配置：

```bash
mihomo -t -d /etc/mihomo
```

检查通过后继续。

## 6. nohup 启动

首次启动执行一次，已有 Mihomo 运行时不要重复执行：

```bash
nohup /usr/local/bin/mihomo -d /etc/mihomo > /etc/mihomo/mihomo.log 2>&1 < /dev/null &
echo $! > /etc/mihomo/mihomo.pid
sleep 2
tail -n 30 /etc/mihomo/mihomo.log
```

测试代理：

```bash
curl --noproxy '' -x http://127.0.0.1:7890 --max-time 30 https://api.github.com
```

收到正常 JSON 响应后，让当前终端使用代理：

```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export all_proxy=socks5h://127.0.0.1:7890
export no_proxy=localhost,127.0.0.1,::1
```

退出 SSH 后 Mihomo 仍会运行；服务器重启后需重新启动。

## 7. MetaCubeXD

打开配置文件：

```bash
nano /etc/mihomo/config.yaml
```

添加以下两行；已有同名字段则修改：

```yaml
external-ui: ui
external-ui-url: "https://github.com/MetaCubeX/metacubexd/archive/refs/heads/gh-pages.zip"
```

保存退出后，检查配置。通过后发送重载信号，无需重复启动进程：

```bash
mihomo -t -d /etc/mihomo && kill -HUP "$(cat /etc/mihomo/mihomo.pid)"
```

等待面板下载完成，查看日志：

```bash
tail -f /etc/mihomo/mihomo.log
```

按 `Ctrl+C` 退出日志查看。检查页面，返回 `200` 表示可以访问：

```bash
curl --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9090/ui/
```

在**自己电脑的终端**执行以下命令，将 `用户名@服务器IP` 替换成实际 SSH 地址：

**macOS（终端）：**

```bash
ssh -NT -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -L 19090:127.0.0.1:9090 用户名@服务器IP
```

**Windows（PowerShell）：**

```powershell
ssh -NT -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -L 19090:127.0.0.1:9090 用户名@服务器IP
```

连接成功后通常没有输出，保持终端打开，在自己电脑的浏览器访问：

**<http://127.0.0.1:19090/ui/>**

面板中填写：

- 后端地址：`http://127.0.0.1:19090`
- 密钥：配置文件中的 `secret` 值，没有配置则留空

连接后，在“代理 / Proxies”中切换节点即可。不需要在服务器防火墙中开放 `7890` 或 `9090`。
