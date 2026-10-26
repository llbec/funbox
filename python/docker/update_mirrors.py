#!/usr/bin/env python3
"""备份 Docker 配置，从 DockerHub README 提取并检测最多五个镜像源。"""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SOURCE = 'https://raw.githubusercontent.com/dongyubin/DockerHub/main/README.md'


def extract_mirrors(markdown):
    """只读取有效列表表格的地址列，保持顺序、去重，排除失效区。"""
    in_section = False
    address_column = None
    mirrors = []
    for line in markdown.splitlines():
        if line.startswith('#'):
            title = line.lstrip('#').strip()
            if title == 'DockerHub国内镜像加速源列表':
                in_section = True
                continue
            if in_section:
                break
        if not in_section or not line.strip().startswith('|'):
            continue
        columns = [part.strip() for part in line.strip().strip('|').split('|')]
        if '镜像加速器地址' in columns:
            address_column = columns.index('镜像加速器地址')
            continue
        if address_column is None or len(columns) <= address_column:
            continue
        # 删除划线内容，避免收录已标记失效的地址。
        cell = re.sub(r'~~.*?~~', '', columns[address_column])
        match = re.search(r'(?:https?://)?(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}(?::\d+)?(?:/[^\s`<>()\[\]，（）]*)?', cell)
        if not match:
            continue
        url = match.group(0).rstrip('/')
        if '://' not in url:
            url = 'https://' + url
        parsed = urlsplit(url)
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            continue
        if url not in mirrors:
            mirrors.append(url)
    return mirrors


def fetch_readme(timeout):
    request = Request(SOURCE, headers={'User-Agent': 'docker-mirror-updater/1.0'})
    with urlopen(request, timeout=timeout) as response:
        content = response.read(2 * 1024 * 1024 + 1)
    if len(content) > 2 * 1024 * 1024:
        raise ValueError('README 超过大小限制')
    return content.decode('utf-8-sig')


def check_mirror(url, timeout):
    """探测 Registry V2 接口，不保证任意镜像都能拉取。"""
    request = Request(url.rstrip('/') + '/v2/', headers={'User-Agent': 'docker-mirror-updater/1.0'})
    try:
        with urlopen(request, timeout=timeout) as response:
            code, headers, body = response.status, response.headers, response.read(65536)
    except HTTPError as exc:
        code, headers = exc.code, exc.headers
        body = exc.read(65536)
        exc.close()
    except (OSError, URLError, ValueError) as exc:
        return False, str(exc)
    registry_header = 'registry/2.0' in headers.get('Docker-Distribution-Api-Version', '').lower()
    if code == 401 and (registry_header or 'bearer ' in headers.get('WWW-Authenticate', '').lower()):
        return True, 'Registry V2 返回 401（需要认证）'
    if code == 200:
        try:
            registry_body = json.loads(body) == {}
        except (ValueError, UnicodeError):
            registry_body = False
        if registry_header or registry_body:
            return True, 'Registry V2 返回 200'
    return False, f'HTTP {code}，未识别为正常 Registry V2 响应'


def select_mirrors(candidates, timeout, skip_check=False):
    selected = []
    for url in candidates:
        ok, message = (True, '按网页列表选取，未检测') if skip_check else check_mirror(url, timeout)
        print(f'{"采用" if ok else "跳过"} {url}：{message}')
        if ok:
            selected.append(url)
        if len(selected) == 5:
            break
    return selected


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'JSON 含重复字段：{key}')
        result[key] = value
    return result


def update(config_path, data_root=None, timeout=10, skip_check=False):
    if config_path.is_symlink() or not config_path.is_file():
        raise ValueError(f'配置必须是已存在的普通文件：{config_path}')
    original = config_path.read_bytes()
    metadata = config_path.stat()
    backup = config_path.with_name(datetime.now().strftime('%Y%m%d%H%M%S') + '.daemon.json')
    # 独占创建，避免同一秒重复执行覆盖旧备份。
    with backup.open('xb') as output:
        os.fchmod(output.fileno(), stat.S_IMODE(metadata.st_mode))
        output.write(original)
    shutil.copystat(config_path, backup)
    print(f'已备份：{backup}')

    config = json.loads(original, object_pairs_hook=unique_object)
    if not isinstance(config, dict):
        raise ValueError('daemon.json 顶层必须是 JSON 对象')
    # 拒绝 NaN / Infinity 等非标准 JSON 值。
    json.dumps(config, allow_nan=False)
    candidates = extract_mirrors(fetch_readme(timeout))
    if not candidates:
        raise ValueError('网页未提取到镜像地址，可能是网页结构变化；原配置未修改')
    selected = select_mirrors(candidates, timeout, skip_check)
    if not selected:
        raise ValueError('没有通过检测的镜像地址，原配置未修改')
    config['registry-mirrors'] = selected
    # 仅显式传入参数时新增或覆盖 data-root。
    if data_root is not None:
        config['data-root'] = data_root
        print(f'设置 data-root：{data_root}')
    payload = json.dumps(config, ensure_ascii=False, indent=2, allow_nan=False) + '\n'

    # 同目录临时文件 + 原子替换，失败不会留下半个 JSON 文件。
    fd, name = tempfile.mkstemp(prefix='.daemon.', suffix='.tmp', dir=config_path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            os.fchmod(output.fileno(), stat.S_IMODE(metadata.st_mode))
            current = os.fstat(output.fileno())
            if (current.st_uid, current.st_gid) != (metadata.st_uid, metadata.st_gid):
                os.fchown(output.fileno(), metadata.st_uid, metadata.st_gid)
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        if config_path.is_symlink() or config_path.read_bytes() != original:
            raise ValueError('运行期间配置被其他程序修改，已取消写入')
        os.replace(temporary, config_path)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'已更新：{config_path}，共 {len(selected)} 个镜像地址。')
    print('未重启 Docker。需要生效时执行：sudo systemctl restart docker')
    print(f'\n{config_path} 当前内容：')
    print(config_path.read_text(encoding='utf-8'), end='')
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('/etc/docker/daemon.json'), help='配置文件路径')
    parser.add_argument('--data-root', default=None, help='显式指定时新增或覆盖 data-root；不传则保持原配置')
    parser.add_argument('--timeout', type=float, default=10, help='网络请求超时秒数，默认 10')
    parser.add_argument('--skip-check', action='store_true', help='不检测连通性，直接使用网页列出的前五个地址')
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout 必须大于 0')
    try:
        update(args.config, args.data_root, args.timeout, args.skip_check)
    except (OSError, ValueError, URLError) as exc:
        print(f'失败：{exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
