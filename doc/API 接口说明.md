## API接口说明
### 市场数据接口
基础URL: `https://www.simcompanies.com/api/v3/market/all/{serverType}/{orderType}/`

参数说明：
- `serverType`: 服务器类型
  - `0`: 商业大亨服务器
  - `1`: 企业家服务器

- `orderType`: 商品分类
  - `1`: 电力
  - `2`: 水

示例：
1. 商业大亨服务器电力: `/market/0/1/`
2. 商业大亨服务器水: `/market/0/2/`
3. 企业家服务器电力: `/market/1/1/`
4. 企业家服务器水: `/market/1/2/`

> **注意：** 
> - API返回的数据格式参考文档末尾的JSON示例
> - 返回的数据0_1.json和1_1.json是两个地址的商品组合。路径在`doc`目录下。


示例：
```json
{
    "id": 95475829,
    "kind": 1,
    "quantity": 5639232,
    "quality": 0,
    "price": 0.26,
    "seller": {
        "id": 3237138,
        "company": "ELECTRIC ENERGY CITY",
        "realmId": 0,
        "logo": "https://d1fxy698ilbz6u.cloudfront.net/logo/aeadafcee7ae8c79988ba108a28efd17c23df0ea.png",
        "certificates": 1,
        "contest_wins": 0,
        "npc": false,
        "courseId": null,
        "ip": "8c7f6b"
    },
    "posted": "2025-01-05T12:27:16.064763+00:00",
    "fees": 0
}
```
响应格式：
```json
[
    {
        "id": "订单ID",
        "kind": "商品类型ID",
        "quantity": "商品数量",
        "quality": "商品品质(0-12)",
        "price": "商品单价",
        "seller": {
            "id": "玩家ID",
            "company": "玩家公司名称",
            "realmId": "玩家公司服务器ID",
            "logo": "玩家公司logo地址",
            "certificates": "玩家公司证书数量",
            "contest_wins": "玩家公司比赛获胜次数",
            "npc": "玩家是否NPC",
            "ip": "玩家IP地址"
        },
        "posted": "玩家订单发布时间",
        "fees": "交易费用"
    }
]

## 二、文档格式

### 2.1 Markdown格式规范
1. 标题格式：
   - 一级标题：使用单个 `#` 
   - 二级标题：使用两个 `##`
   - 三级标题：使用三个 `###`

2. 列表格式：
   - 无序列表：使用 `-` 或 `*`
   - 有序列表：使用数字加点 `1.`
   - 列表缩进：使用两个空格

3. 代码块：
   - 单行代码：使用反引号 `` ` ``
   - 多行代码：使用三个反引号 ``` 并指定语言
   ```python
   # 示例代码
   print("Hello World")
   ```

4. 表格格式：
   | 列1 | 列2 | 列3 |
   |-----|-----|-----|
   |内容1|内容2|内容3|

5. 强调格式：
   - 斜体：使用单个 `*` 或 `_`
   - 粗体：使用两个 `**` 或 `__`
   - 删除线：使用两个 `~~`

6. 链接和图片：
   - 链接：`[链接文字](URL)`
   - 图片：`![图片描述](图片URL)`

7. 引用：
   - 使用 `>` 进行引用
   > 这是一个引用示例

8. 分隔线：
   - 使用三个或更多的 `-` 或 `*`
   ---
