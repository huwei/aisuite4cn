# Dashscope（阿里云百炼）

`dashscope` 是 `qwen` 的别名 Provider，使用相同的 API 端点和认证方式。使用任一均可。

详细用法请参考 [Qwen 指南](qwen.md)。

## 环境变量

```shell
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

## 安装

```shell
pip install 'aisuite4cn[dashscope]'
```

## 使用示例

```python
import aisuite4cn as ai

client = ai.Client()

# 使用 dashscope 别名
response = client.chat.completions.create(
    model="dashscope:qwen-max",
    messages=[
        {"role": "user", "content": "你好！"},
    ],
)
print(response.choices[0].message.content)
```

## 推荐模型

与 [Qwen](qwen.md) 相同：`qwen-max`、`qwen-plus`、`qwen-turbo` 等。

## 特殊说明

- `dashscope` 和 `qwen` 是完全等价的别名，指向同一 API 端点
- 选择任一 provider 名称使用即可，无需重复配置
