import json
import os
import random
import datetime
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # Python 2 fallback

# 配置部分
SITES_DIR = '../mirror/sites'  # 相对路径，指向 mirror 项目的 sites 目录
OUTPUT_FILE = 'README.md'
# 关键词列表，用于随机插入或作为标题
KEYWORDS = [
    "机场推荐", "科学上网", "翻墙教程", "VPN推荐", "Clash节点", 
    "Shadowsocks节点", "V2Ray节点", "Trojan节点", "免费节点", 
    "高速梯子", "稳定机场", "流媒体解锁", "ChatGPT解锁", 
    "4K秒开", "晚高峰不卡", "IPLC专线", "中转机场"
]

def load_sites_and_links():
    """读取所有站点配置和对应的链接文件"""
    sites_data = []
    
    if not os.path.exists(SITES_DIR):
        print(f"Error: Sites directory {SITES_DIR} not found.")
        return []

    # 获取所有站点配置文件
    site_files = [f for f in os.listdir(SITES_DIR) if f.endswith('.json') and not f.endswith('_links.json')]
    
    for site_file in site_files:
        site_id = site_file.replace('.json', '')
        site_path = os.path.join(SITES_DIR, site_file)
        links_path = os.path.join(SITES_DIR, f"{site_id}_links.json")
        
        try:
            with open(site_path, 'r', encoding='utf-8') as f:
                site_config = json.load(f)
            
            # 只有当对应的 links 文件存在时才处理
            if os.path.exists(links_path):
                with open(links_path, 'r', encoding='utf-8') as f:
                    links = json.load(f)
                
                valid_links = []
                for kw, url in links.items():
                    if url.startswith('http'):
                         # 尝试使用镜像域名替换原始域名
                        proxy_host = site_config.get('proxyHost')
                        final_url = url
                        if proxy_host:
                            try:
                                # 解析原始 URL
                                parsed_url = urlparse(url)
                                # 替换 host 为镜像 host
                                # 如果 proxy_host 是数组，取第一个
                                host_to_use = proxy_host[0] if isinstance(proxy_host, list) else proxy_host
                                final_url = url.replace(parsed_url.netloc, host_to_use)
                            except:
                                pass
                        
                        valid_links.append({'title': kw, 'url': final_url})
                
                if valid_links:
                    sites_data.append({
                        'name': site_config.get('name', site_id),
                        'proxy_host': site_config.get('proxyHost', ''),
                        'links': valid_links
                    })
        except Exception as e:
            print(f"Error processing {site_id}: {e}")
            
    return sites_data

def generate_content(sites_data, count=15):
    """生成 Markdown 内容"""
    all_articles = []
    
    # 收集所有文章链接
    for site in sites_data:
        for link in site['links']:
            all_articles.append({
                'title': link['title'],
                'url': link['url'],
                'site_name': site['name']
            })
    
    if not all_articles:
        return "No articles found."

    # 随机选择指定数量的文章
    selected_articles = random.sample(all_articles, min(count, len(all_articles)))
    
    # 生成 Markdown
    today = datetime.date.today().strftime("%Y-%m-%d")
    md_content = f"# 机场推荐与网络加速指南 ({today})\n\n"
    
    md_content += "> 本文整理了最新的网络加速资源与技巧，助你畅游互联网。\n\n"
    
    # 随机插入一些关键词段落
    md_content += f"**热门标签**：{'、'.join(random.sample(KEYWORDS, 5))}\n\n"
    
    md_content += "## 精选文章\n\n"
    
    for article in selected_articles:
        # 随机给标题加一些 emoji
        emoji = random.choice(["🚀", "⚡", "🌐", "🔥", "💡", "📝"])
        md_content += f"### {emoji} [{article['title']}]({article['url']})\n\n"
        # 可以在这里加一些随机生成的描述文本，增加 SEO
        md_content += f"了解更多关于 {article['title']} 的详细内容，请点击上方链接访问。\n\n"
        
    md_content += "---\n"
    md_content += f"*自动更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return md_content

def main():
    print("开始生成内容...")
    sites = load_sites_and_links()
    content = generate_content(sites, count=random.randint(10, 20))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已生成至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
