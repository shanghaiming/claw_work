---
name: "news-search"
description: "搜索金融、资本市场、科技、政治、军事新闻并通过飞书推送。当用户请求新闻搜索或定时任务触发时激活。"
---

# 新闻搜索技能

## 功能
每天早上7点自动搜索以下类别新闻，并通过飞书推送：
1. 金融
2. 资本市场  
3. 科技
4. 政治
5. 军事

## 使用方式
当收到消息包含"新闻搜索"时，执行以下步骤：

### 1. 搜索新闻
使用web_fetch工具访问新浪新闻RSS源获取最新新闻：
- 国内要闻RSS: http://rss.sina.com.cn/news/china/focus15.xml
- 财经新闻RSS: http://rss.sina.com.cn/news/finance/focus15.xml (如果可用)
- 科技新闻RSS: http://rss.sina.com.cn/news/tech/focus15.xml (如果可用)

### 2. 解析和过滤
使用Python解析RSS XML，根据关键词过滤新闻条目。

### 3. 格式化消息
将过滤后的新闻按类别整理，生成格式化的消息。

### 4. 发送飞书消息
使用openclaw message send命令将新闻摘要发送到飞书。

## 示例命令
```bash
# 发送测试新闻
openclaw message send --channel feishu --target "ou_798a7cb40b7daf203981afa4b4f08ad8" --message "📰 新闻摘要..."
```

## 注意事项
- 如果RSS源不可用，使用百度新闻页面作为备选
- 每天只推送一次，避免信息过载
- 确保新闻时效性，优先推送当日新闻