#!/usr/bin/env bash
# 本地 config.yaml + YAML 订阅 -> /etc/mihomo/config.yaml。
set -Eeuo pipefail
umask 077
export PATH="/usr/local/bin:$PATH"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
local_config="$script_dir/config.yaml"
config_dir="${1:-/etc/mihomo}"

# 默认配置目录通常属于 root；需要时自动通过 sudo 重新执行。
if ! mkdir -p "$config_dir" 2>/dev/null || [[ ! -w "$config_dir" ]]; then
  if (( EUID != 0 )) && command -v sudo >/dev/null 2>&1; then
    echo "写入 $config_dir 需要管理员权限，将通过 sudo 继续。"
    exec sudo bash "$script_dir/subscribe.sh" "$@"
  fi
  echo "无法写入配置目录：$config_dir，请检查目录权限。" >&2
  exit 1
fi

for cmd in curl awk base64 mihomo mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "缺少命令：$cmd，请先安装。" >&2
    exit 1
  }
done
[[ -s "$local_config" ]] || { echo "本地配置不存在或为空：$local_config" >&2; exit 1; }
config_dir="$(cd "$config_dir" && pwd)"
target="$config_dir/config.yaml"
[[ "$local_config" != "$target" ]] || { echo '模板目录不能与输出目录相同。' >&2; exit 1; }
[[ ! -L "$target" ]] || { echo '目标 config.yaml 是符号链接，请改用普通文件。' >&2; exit 1; }

# 防止两个订阅更新同时覆盖配置。
lock="$config_dir/.subscribe.lock"
mkdir "$lock" 2>/dev/null || { echo '另一个订阅更新正在进行，或 .subscribe.lock 尚未清理。' >&2; exit 1; }
stage=''
backup=''
replaced=false
committed=false
cleanup() {
  result=$?
  trap - EXIT
  if [[ "$replaced" == true && "$committed" == false ]]; then
    if [[ -n "$backup" ]]; then
      mv -f "$backup" "$target" || { echo "恢复失败，请从 $backup 手动恢复。" >&2; result=1; }
    else
      rm -f "$target"
    fi
    echo '未保留无效配置，已恢复更新前的状态。' >&2
  fi
  [[ -z "$stage" ]] || rm -rf -- "$stage"
  rmdir "$lock"
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
stage="$(mktemp -d "$config_dir/.subscribe.XXXXXX")"

read -r -s -p '请输入订阅 URL（输入不显示）：' sub_url
printf '\n'
case "$sub_url" in
  http://*|https://*) ;;
  *) echo '请输入 HTTP / HTTPS 订阅 URL。' >&2; exit 1 ;;
esac
[[ "$sub_url" != *$'\r'* ]] || { echo 'URL 包含非法换行。' >&2; exit 1; }

escaped_url="${sub_url//\\/\\\\}"
escaped_url="${escaped_url//\"/\\\"}"
echo '正在下载订阅……'
printf 'url = "%s"\n' "$escaped_url" | \
  curl --config - -fsSL --proto '=http,https' --proto-redir '=http,https' \
    --retry 2 --connect-timeout 15 --max-time 120 --max-filesize 20971520 \
    -A mihomo -o "$stage/subscription.yaml"
unset sub_url escaped_url
[[ -s "$stage/subscription.yaml" ]] || { echo '订阅内容为空。' >&2; exit 1; }
if grep -qiE '<(!doctype[[:space:]]+html|html|head|body)([[:space:]>])' "$stage/subscription.yaml"; then
  echo '返回的是网页，请使用实际订阅链接。' >&2
  exit 1
fi

# 延续测试脚本的 Base64 解码流程；只有解码后为 YAML 才能直接合并。
if ! grep -qE '^(proxies|proxy-providers):' "$stage/subscription.yaml"; then
  if base64 --decode </dev/null >/dev/null 2>&1; then decode_flag=--decode; else decode_flag=-D; fi
  encoded="$(tr -d '[:space:]' < "$stage/subscription.yaml" | tr '_-' '/+')"
  case $((${#encoded} % 4)) in 2) encoded+='==' ;; 3) encoded+='=' ;; esac
  if printf '%s' "$encoded" | base64 "$decode_flag" > "$stage/decoded" 2>/dev/null && \
     grep -qE '^(proxies|proxy-providers):' "$stage/decoded"; then
    mv "$stage/decoded" "$stage/subscription.yaml"
  else
    echo '此合并脚本需要 Clash / Mihomo YAML 订阅；节点 URI 或其 Base64 编码不能直接合并为 YAML。' >&2
    exit 1
  fi
  unset encoded
fi

echo '正在合并订阅与本地 config.yaml（本地同名顶层字段优先）……'
# 按完整顶层字段块合并，保留节点列表、嵌套配置及其缩进。
# 适用于常规块式 YAML，顶层键不加引号；不支持 JSON、多文档 YAML。
# 不声称解析所有 YAML 语法，最终由 Mihomo 作语法及引用校验。
awk '
function fail(message) { print message > "/dev/stderr"; failed=1; exit 1 }
FNR == 1 { source++; key=""; document=0; ended=0 }
{ sub(/\r$/, "") }
/^---[[:space:]]*(#.*)?$/ {
  if (document || count[source]) fail("不支持多文档 YAML")
  document=1; next
}
/^\.\.\.[[:space:]]*(#.*)?$/ { ended=1; next }
/^[[:space:]]*(#.*)?$/ {
  if (key != "") block[source,key]=block[source,key] $0 "\n"
  next
}
{
  if (ended) fail("YAML 文档结束后还有内容")
  if ($0 ~ /^[A-Za-z0-9_-]+:[[:space:]]/ || $0 ~ /^[A-Za-z0-9_-]+:$/) {
    key=$0; sub(/:.*/, "", key)
    if ((source SUBSEP key) in block) fail("存在重复的 YAML 顶层字段")
    keys[source,++count[source]]=key
    block[source,key]=$0 "\n"
  } else {
    if (key == "" || $0 !~ /^([[:space:]]|-[[:space:]])/) fail("请使用顶层键不加引号的常规块式 YAML")
    block[source,key]=block[source,key] $0 "\n"
  }
}
END {
  if (failed) exit 1
  if (!count[1] || !count[2]) { print "配置不能为空" > "/dev/stderr"; exit 1 }
  for (i=1;i<=count[1];i++) {
    key=keys[1,i]
    if (!((2 SUBSEP key) in block)) printf "%s", block[1,key]
  }
  for (i=1;i<=count[2];i++) printf "%s", block[2,keys[2,i]]
}' "$stage/subscription.yaml" "$local_config" > "$stage/config.yaml"

if [[ -e "$target" ]]; then
  backup="$(mktemp "$config_dir/config.yaml.bak.XXXXXX")"
  cp -p "$target" "$backup"
fi
chmod 600 "$stage/config.yaml"
# sudo 执行后仍让发起调用的普通用户能够读取配置并运行 Mihomo。
if (( EUID == 0 )) && [[ -n "${SUDO_UID:-}" && -n "${SUDO_GID:-}" ]]; then
  chown "$SUDO_UID:$SUDO_GID" "$stage/config.yaml"
fi
replaced=true
mv -f "$stage/config.yaml" "$target"
echo "已保存：$target"
echo "执行校验：mihomo -t -d $config_dir"
if ! mihomo -t -d "$config_dir"; then
  echo 'Mihomo 配置校验失败。' >&2
  exit 1
fi
committed=true
echo '订阅合并成功，配置校验通过。'
[[ -z "$backup" ]] || echo "旧配置备份：$backup"
echo '本地模板未修改。重新启动或重载 Mihomo 后生效。'
