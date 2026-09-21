#!/usr/bin/env bash
# 只下载、解码并打印，不修改 /etc/mihomo。
set -euo pipefail
umask 077

for cmd in curl base64 mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "缺少命令：$cmd" >&2
    exit 1
  }
done

printf '输出包含订阅及节点凭证，请勿公开分享。\n'
read -r -s -p '请输入订阅 URL（输入不显示）：' sub_url
printf '\n'
case "$sub_url" in
  http://*|https://*) ;;
  *) echo '请输入 HTTP / HTTPS 订阅 URL。' >&2; exit 1 ;;
esac
[[ "$sub_url" != *$'\r'* ]] || { echo 'URL 包含非法换行。' >&2; exit 1; }

work_dir="$(mktemp -d)"
trap 'rm -rf -- "$work_dir"' EXIT
escaped_url="${sub_url//\\/\\\\}"
escaped_url="${escaped_url//\"/\\\"}"

printf '正在下载订阅……\n'
printf 'url = "%s"\n' "$escaped_url" | \
  curl --config - -fsSL --proto '=http,https' --proto-redir '=http,https' \
    --connect-timeout 15 --max-time 120 --max-filesize 20971520 \
    -A mihomo -o "$work_dir/subscription"

[[ -s "$work_dir/subscription" ]] || { echo '订阅内容为空。' >&2; exit 1; }
if grep -qiE '<(!doctype[[:space:]]+html|html|head|body)([[:space:]>])' "$work_dir/subscription"; then
  echo '返回的是 HTML 网页，请使用实际订阅链接。' >&2
  exit 1
fi

if grep -qE '^(proxies|proxy-providers|proxy-groups):' "$work_dir/subscription"; then
  printf '\n----- YAML 配置 / 节点列表 -----\n\n'
  cat "$work_dir/subscription"
  printf '\n\n以上为订阅原始 YAML，尚未进行 Mihomo 语法及连通性校验。\n'
  exit 0
fi

# 兼容 Linux 和 macOS 的 base64 解码参数。
if base64 --decode </dev/null >/dev/null 2>&1; then
  decode_flag=--decode
else
  decode_flag=-D
fi

node_file="$work_dir/subscription"
if ! grep -qE '^[[:space:]]*[a-zA-Z][a-zA-Z0-9+.-]*://' "$node_file"; then
  encoded="$(tr -d '[:space:]' < "$node_file" | tr '_-' '/+')"
  case $((${#encoded} % 4)) in
    2) encoded+='==' ;;
    3) encoded+='=' ;;
  esac
  if ! printf '%s' "$encoded" | base64 "$decode_flag" > "$work_dir/decoded" 2>/dev/null; then
    echo '无法识别内容：应为 YAML、节点链接或 Base64 订阅。' >&2
    exit 1
  fi
  node_file="$work_dir/decoded"
fi

# 每个非空行必须是 URI；具体协议及参数交给 Mihomo 解析。
if ! grep -qE '^[[:space:]]*[a-zA-Z][a-zA-Z0-9+.-]*://' "$node_file" || \
   grep -vE '^[[:space:]]*$|^[[:space:]]*[a-zA-Z][a-zA-Z0-9+.-]*://' "$node_file" | grep -q .; then
  echo '解码结果不是有效的节点链接列表。' >&2
  exit 1
fi

printf '\n----- 解析后的节点链接 -----\n\n'
cat "$node_file"
printf '\n\n----- Mihomo 配置预览 -----\n\n'
# YAML 单引号字符串中，单引号使用两个单引号转义。
yaml_url="$(printf '%s' "$sub_url" | sed "s/'/''/g")"
cat <<EOF_CONFIG
mixed-port: 7890
allow-lan: false
mode: rule
external-controller: 127.0.0.1:9090
tun:
  enable: false
proxy-providers:
  subscription:
    type: http
    url: '$yaml_url'
    path: ./subscription.txt
    interval: 3600
proxy-groups:
  - name: PROXY
    type: select
    use:
      - subscription
rules:
  - MATCH,PROXY
EOF_CONFIG
printf '\n节点链接由 Mihomo 原生解析，此处未逐个转换为 proxies YAML，也未验证连通性。\n'
