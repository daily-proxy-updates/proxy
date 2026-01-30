import os
import json
import random
import datetime
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, quote

# 配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SITES_DIR = os.path.join(PROJECT_ROOT, 'sites')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'README.md')

# 关键词库
KEYWORDS = [
    "机场推荐", "科学上网", "梯子推荐", "翻墙软件", "VPN推荐", 
    "Clash节点", "Shadowsocks", "V2Ray", "Trojan", "高速节点",
    "解锁Netflix", "4K秒开", "稳定机场", "便宜机场", "IPLC专线"
]

# 标题模板
TITLE_TEMPLATES = [
    "{name} 机场推荐 - 高速稳定 4K 秒开",
    "2024 最佳机场推荐：{name} 评测",
    "{name} 怎么样？最新使用体验报告",
    "稳定好用的梯子推荐：{name}",
    "{name} - 解锁流媒体，晚高峰不卡顿",
    "便宜机场推荐：{name} 性价比之选",
    "{name} 官网地址与最新优惠码",
    "安卓/iOS/Mac/Windows 通用机场推荐：{name}"
]

def fetch_feed_posts(proxy_host):
    """Fetch posts from the site's RSS feed"""
    # Try different schemes if https fails, but default to https
    url = f"https://{proxy_host}/feed"
    print(f"Fetching feed from: {url}")
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        if response.status_code == 200:
            # Parse XML
            try:
                content = response.content
                try:
                    text = content.decode('utf-8')
                except UnicodeDecodeError:
                    text = content.decode('gbk', errors='ignore')
                root = ET.fromstring(text)
            except ET.ParseError as e:
                print(f"XML Parse Error for {proxy_host}: {e}")
                return []
                
            posts = []
            # Standard RSS 2.0: channel -> item
            # Also handle Atom if needed, but WordPress uses RSS 2.0 by default at /feed
            for item in root.findall('./channel/item'):
                title = item.find('title')
                link = item.find('link')
                
                if title is not None and link is not None:
                    title_text = title.text
                    link_text = link.text
                    
                    # Ensure link uses proxy_host
                    if link_text:
                        parsed = urlparse(link_text)
                        # Reconstruct url with proxy_host
                        new_link = link_text.replace(parsed.netloc, proxy_host)
                        
                        posts.append({
                            'name': title_text, # Use title as name
                            'url': new_link,
                            'type': 'article'
                        })
            print(f"Found {len(posts)} posts for {proxy_host}")
            return posts
        else:
            print(f"Failed to fetch feed for {proxy_host}: Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching feed for {proxy_host}: {e}")
    return []

def get_all_site_configs():
    """获取所有站点配置"""
    configs = []
    if not os.path.exists(SITES_DIR):
        print(f"Error: Sites directory {SITES_DIR} not found.")
        return []

    site_files = [f for f in os.listdir(SITES_DIR) if f.endswith('.json') and not f.endswith('_links.json')]
    
    for site_file in site_files:
        try:
            site_path = os.path.join(SITES_DIR, site_file)
            with open(site_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Ensure we have the filename id
                config['id'] = site_file.replace('.json', '')
                configs.append(config)
        except Exception as e:
            print(f"Error loading config {site_file}: {e}")
            
    return configs

def fetch_site_data(site_config):
    """获取单个站点的数据（文章和链接）"""
    site_id = site_config.get('id')
    proxy_host = site_config.get('proxyHost')
    
    if not proxy_host:
        return []
        
    if isinstance(proxy_host, list):
        proxy_host = proxy_host[0]
        
    valid_links = []
    
    # 1. 获取 RSS 文章 (Sub-pages)
    feed_posts = fetch_feed_posts(proxy_host)
    if feed_posts:
        valid_links.extend(feed_posts)
        
    # 2. 读取并转换推广链接 (Redirects)
    links_path = os.path.join(SITES_DIR, f"{site_id}_links.json")
    if os.path.exists(links_path):
        try:
            with open(links_path, 'r', encoding='utf-8') as f:
                links = json.load(f)
            
            for kw, url in links.items():
                if url.startswith('http'):
                    # Convert to local redirect link: https://site.com/keyword
                    # Server handles this via dynamicLinks
                    # We assume server uses decoded path matching, so we can use encoded or decoded.
                    # Standard URL should be encoded.
                    encoded_kw = quote(kw)
                    local_url = f"https://{proxy_host}/{encoded_kw}"
                    
                    valid_links.append({
                        'name': kw,
                        'url': local_url,
                        'type': 'referral'
                    })
        except Exception as e:
            print(f"Error loading links for {site_id}: {e}")

    # 3. 添加站点主页
    valid_links.append({
        'name': site_config.get('name', site_id),
        'url': f"https://{proxy_host}",
        'type': 'site'
    })
    
    return valid_links

def generate_title(item):
    """根据链接类型生成标题"""
    name = item['name']
    
    # 如果是文章类型的链接，直接使用文章标题
    if item.get('type') == 'article':
        return name
        
    # 首字母大写
    name = name.capitalize() if name else "Unknown"
    
    template = random.choice(TITLE_TEMPLATES)
    return template.format(name=name)

def generate_content(all_items, count=15):
    """生成 Markdown 内容"""
    if not all_items:
        return "No articles found."

    # 随机选择指定数量的文章
    # Ensure we don't error if count > len
    selected_items = random.sample(all_items, min(count, len(all_items)))
    
    # 生成 Markdown
    today = datetime.date.today().strftime("%Y-%m-%d")
    md_content = f"# 机场推荐与网络加速指南 ({today})\n\n"
    
    md_content += "> 本文每日自动更新，整理了最新的网络加速资源、机场推荐与科学上网技巧，助你畅游互联网。\n\n"
    
    # 随机插入一些关键词段落
    tags = random.sample(KEYWORDS, min(5, len(KEYWORDS)))
    md_content += f"**热门标签**：{'、'.join(tags)}\n\n"
    
    md_content += "## 精选资源推荐\n\n"
    
    for item in selected_items:
        title = generate_title(item)
        emoji = random.choice(["🚀", "⚡", "🌐", "🔥", "💡", "📝", "⭐", "💎"])
        
        md_content += f"### {emoji} [{title}]({item['url']})\n\n"
        
        # 生成简短描述
        if item.get('type') == 'article':
            # 对于文章，生成简单的阅读引导
            desc_templates = [
                "点击阅读全文，了解更多详细信息。",
                "最新更新内容，不容错过。",
                "干货满满，建议收藏阅读。",
                "深度解析，带你了解更多。",
                "点击上方链接查看完整教程/评测。"
            ]
        else:
            desc_templates = [
                f"点击上方链接访问 {item['name']} 官网，获取最新优惠。",
                f"{item['name']} 是一款性价比极高的加速服务，支持多平台使用。",
                f"晚高峰 4K 视频秒开，{item['name']} 值得一试。",
                f"注册即可免费试用，{item['name']} 提供稳定高速的节点。",
                "专线接入，超低延迟，游戏/视频两不误。"
            ]
        md_content += f"{random.choice(desc_templates)}\n\n"
    
    md_content += "---\n"
    md_content += "### 免责声明\n"
    md_content += "本文内容仅供学习和技术交流使用，请勿用于非法用途。请遵守当地法律法规。\n\n"
    md_content += f"*自动更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return md_content

def main():
    print("开始生成内容...")
    
    # 1. 获取所有站点
    configs = get_all_site_configs()
    if not configs:
        print("No site configs found.")
        return

    # 2. 随机选择一个站点 (尝试最多3次，以防选中的站点没有数据)
    selected_items = []
    
    # Shuffle to pick randomly
    random.shuffle(configs)
    
    for config in configs:
        print(f"Trying site: {config.get('name', config['id'])}")
        items = fetch_site_data(config)
        if items:
            selected_items = items
            print(f"Successfully fetched {len(items)} items from {config['id']}")
            break
        print(f"No items found for {config['id']}, trying next...")
    
    if not selected_items:
        print("Failed to fetch content from any site.")
        return

    # 3. 生成内容
    content = generate_content(selected_items, count=random.randint(10, 20))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已生成至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()