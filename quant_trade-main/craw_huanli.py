import requests
from lxml import html

# 配置部分 - 只需修改这里
url = "https://www.huangli123.net/huangli/"  # 替换为您的目标网址

# 添加您想要抓取的所有XPath路径
xpath_selectors = [
    "/html/body/div[1]/div[1]/div[1]/span[1]",           # 标题
    "/html/body/div[1]/div[1]/div[2]/span[1]",           # 副标题
    "/html/body/div[1]/div[1]/div[3]/span[1]"
]

# 获取网页内容
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # 检查请求是否成功
    tree = html.fromstring(response.content)
    
    print(f"开始抓取: {url}")
    print("=" * 50)
    
    # 遍历所有XPath选择器
    for i, selector in enumerate(xpath_selectors, 1):

        # 提取内容
        elements = tree.xpath(selector)
 
        # 显示结果
        for j, element in enumerate(elements, 1):
            if hasattr(element, 'text_content'):
                # 处理元素节点
                content = element.text_content().strip()
                if content:  # 只显示非空内容
                    print(f"  {j}. {content}")
            else:
                # 处理属性节点或文本节点
                content = str(element).strip()
                if content:  # 只显示非空内容
                    print(f"  {j}. {content}")
                    
except requests.RequestException as e:
    print(f"网络请求错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")