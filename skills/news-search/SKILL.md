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

**注意：不只查新浪，要查所有主要新闻源**

## 使用方式
当收到消息包含"新闻搜索"时，执行以下步骤：

### 1. 搜索新闻
使用web_fetch工具访问多个新闻源RSS获取最新新闻，不只查新浪，要查所有主要新闻源：

**新浪新闻RSS：**
- 国内要闻RSS: http://rss.sina.com.cn/news/china/focus15.xml
- 财经新闻RSS: http://rss.sina.com.cn/news/finance/focus15.xml (如果可用)
- 科技新闻RSS: http://rss.sina.com.cn/news/tech/focus15.xml (如果可用)

**腾讯新闻RSS：**
- 腾讯新闻国内: http://rss.qq.com/news/china.htm
- 腾讯新闻财经: http://rss.qq.com/news/finance.htm
- 腾讯新闻科技: http://rss.qq.com/news/tech.htm

**网易新闻RSS：**
- 网易新闻国内: http://news.163.com/rss/domestic.xml
- 网易新闻财经: http://news.163.com/rss/finance.xml
- 网易新闻科技: http://news.163.com/rss/tech.xml

**搜狐新闻RSS：**
- 搜狐新闻国内: http://rss.sohu.com/news/china.xml
- 搜狐新闻财经: http://rss.sohu.com/news/finance.xml
- 搜狐新闻科技: http://rss.sohu.com/news/tech.xml

**百度新闻（通过百度新闻页面搜索）：**
- 百度新闻搜索: https://news.baidu.com/
- 按类别搜索：金融、股票、科技、政治、军事

### 2. 解析和过滤
使用Python解析各新闻源RSS XML，根据关键词过滤新闻条目。将所有新闻源的搜索结果合并，去重后按相关性排序。

### 3. 格式化消息
将过滤后的新闻按类别整理，生成格式化的消息。在消息开头注明新闻来源（新浪、腾讯、网易、搜狐、百度等）。

### 4. 发送飞书消息
使用openclaw message send命令将新闻摘要发送到飞书。

## 示例命令
```bash
# 发送测试新闻
openclaw message send --channel feishu --target "ou_798a7cb40b7daf203981afa4b4f08ad8" --message "📰 新闻摘要..."
```

## 注意事项
- 不只查新浪，要查所有主要新闻源
- 如果某个RSS源不可用，使用其他可用源
- 百度新闻作为备选，通过web_fetch访问百度新闻页面并提取新闻
- 每天只推送一次，避免信息过载
- 确保新闻时效性，优先推送当日新闻
- 合并多个新闻源的搜索结果，去重后推送