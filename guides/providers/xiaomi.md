# Xiaomi（小米）

`xiaomi` 是 `mimo` 的别名 Provider，使用相同的 API 端点和认证方式。使用任一均可。

详细用法请参考 [Mimo 指南](mimo.md)。

## 环境变量

```shell
export MIMO_API_KEY="your-mimo-api-key"
```

## 安装

```shell
pip install 'aisuite4cn[xiaomi]'
```

## 使用示例

```python
import aisuite4cn as ai

client = ai.Client()

# 使用 xiaomi 别名
response = client.chat.completions.create(
    model="xiaomi:your-model-name",
    messages=[
        {"role": "user", "content": "你好！"},
    ],
)
print(response.choices[0].message.content)
```

## 特殊说明

- `xiaomi` 和 `mimo` 是完全等价的别名，指向同一 API 端点
- 选择任一 provider 名称使用即可，无需重复配置
