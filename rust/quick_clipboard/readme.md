# quick_clipboard

`quick_clipboard` 是一个简单的命令行剪贴板工具：从 JSON 配置文件读取常用文本，按序号展示描述，用户选择后将对应文本复制到系统剪贴板。

## 功能

- 从配置文件读取多条文本项
- 只在终端中展示描述，不直接展示要复制的敏感文本
- 根据用户输入的序号复制对应文本
- 使用 `arboard` 访问系统剪贴板，支持 macOS、Windows、Linux

## 配置文件

配置文件是一个 JSON 数组，每一项包含：

- `description`：展示给用户看的描述
- `text`：实际复制到剪贴板的文本

示例：

```json
[
  {
    "description": "GitHub token",
    "text": "ghp_xxxxxxxxxxxxxxxxxxxx"
  },
  {
    "description": "Wi-Fi password",
    "text": "correct-horse-battery-staple"
  }
]
```

可以复制 `clips.example.json` 为 `clips.json` 后按需修改。

## 使用

```bash
cargo run -- clips.json
```

也可以先构建：

```bash
cargo build --release
```

然后运行：

```bash
./target/release/quick_clipboard clips.json
```

如果不传配置文件路径，程序默认读取可执行文件同目录下的 `clips.json`。

运行后会看到类似输出：

```text
Available clips:
No.  Description
1    GitHub token
2    Wi-Fi password
Select clip number:
```

输入序号并回车后，对应文本会被复制到系统剪贴板。
