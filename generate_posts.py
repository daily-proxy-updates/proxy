import os
import json
import random
import datetime
import requests
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, quote, unquote
from email.utils import parsedate_to_datetime

# 配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SITES_DIR = os.path.join(PROJECT_ROOT, 'sites')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'README.md')
ARCHIVES_DIR = os.path.join(PROJECT_ROOT, 'archives')

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

def sanitize_filename(name):
    """Sanitize filename to be safe for filesystem"""
    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with hyphens
    name = name.replace(" ", "-")
    # Limit length
    return name[:100]

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
            for item in root.findall('./channel/item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                
                if title is not None and link is not None:
                    title_text = title.text
                    link_text = link.text
                    desc_text = description.text if description is not None else ""
                    date_text = pub_date.text if pub_date is not None else ""
                    
                    # Parse date
                    try:
                        if date_text:
                            dt = parsedate_to_datetime(date_text)
                            # Convert to naive datetime for consistency if needed, but keeping tz info is fine
                            # For file system, we might want local time or UTC. Let's stick to UTC or input time.
                        else:
                            dt = datetime.datetime.now()
                    except Exception as e:
                        print(f"Date parse error: {e}")
                        dt = datetime.datetime.now()

                    # Ensure link uses proxy_host
                    if link_text:
                        parsed = urlparse(link_text)
                        # Reconstruct url with proxy_host
                        new_link = link_text.replace(parsed.netloc, proxy_host)
                        
                        posts.append({
                            'name': title_text, # Use title as name
                            'url': new_link,
                            'type': 'article',
                            'description': desc_text,
                            'date': dt
                        })
            print(f"Found {len(posts)} posts for {proxy_host}")
            return posts
        else:
            print(f"Failed to fetch feed for {proxy_host}: Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching feed for {proxy_host}: {e}")
    return []

def save_article_to_archive(item, proxy_host):
    """Save article to local markdown file in archives/YYYY/MM"""
    dt = item['date']
    # If dt is struct_time or similar, ensure it's datetime
    if not isinstance(dt, (datetime.datetime, datetime.date)):
         dt = datetime.datetime.now()
         
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")
    
    # Create dir: archives/YYYY/MM
    archive_dir = os.path.join(ARCHIVES_DIR, year, month)
    os.makedirs(archive_dir, exist_ok=True)
    
    # Filename: DD-title.md
    safe_title = sanitize_filename(item['name'])
    filename = f"{day}-{safe_title}.md"
    filepath = os.path.join(archive_dir, filename)
    
    # Relative path for README (URL encoded for markdown link)
    # On Windows this might need separator handling, but for GitHub/Linux it's forward slash
    rel_path = f"archives/{year}/{month}/{quote(filename)}"
    
    # Content generation
    content = f"# {item['name']}\n\n"
    content += f"**发布时间**: {dt.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    if item.get('description'):
        # Clean up description (simple tag stripping if needed, but raw is okay for now)
        desc = item['description']
        content += f"## 摘要\n\n{desc}\n\n"
    
    content += f"---\n\n"
    content += f"## 阅读全文\n\n"
    content += f"[点击此处阅读完整文章]({item['url']})\n\n"
    content += f"---\n"
    content += f"*本文章由 [Mirror Proxy](https://github.com/daily-proxy-updates/proxy) 自动归档，原始内容来自 [{proxy_host}](https://{proxy_host})*\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return rel_path

def scan_local_archives():
    """Scan local archives directory for existing markdown files"""
    archives = []
    if not os.path.exists(ARCHIVES_DIR):
        return archives
        
    # Walk through archives directory
    for root, dirs, files in os.walk(ARCHIVES_DIR):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                # Parse date from path: archives/YYYY/MM/DD-title.md
                try:
                    rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                    path_parts = rel_path.split(os.sep)
                    # path_parts should be ['archives', 'YYYY', 'MM', 'DD-title.md']
                    if len(path_parts) >= 4:
                        year = int(path_parts[1])
                        month = int(path_parts[2])
                        day_str = path_parts[3].split('-')[0]
                        day = int(day_str)
                        
                        # Create date object (approximate time, as we don't parse file content for time)
                        dt = datetime.datetime(year, month, day)
                        
                        # Read title/desc from file content
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read(1000) # Read first 1000 chars
                            
                        # Extract title (# Title)
                        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                        title = title_match.group(1) if title_match else file.replace('.md', '')
                        
                        # Extract description (## 摘要\n\nDesc)
                        desc_match = re.search(r'## 摘要\s*\n\n(.+?)(\n\n|$)', content, re.DOTALL)
                        desc = desc_match.group(1) if desc_match else ""
                        
                        # URL encoded path for README link
                        # Ensure forward slashes for markdown link
                        link_path = f"archives/{year}/{month:02d}/{quote(file)}"
                        
                        archives.append({
                            'name': title,
                            'url': "", # Not needed for local file if we use local_path
                            'local_path': link_path,
                            'type': 'article',
                            'description': desc,
                            'date': dt
                        })
                except Exception as e:
                    print(f"Error scanning archive {file}: {e}")
                    
    # Sort by date desc
    archives.sort(key=lambda x: x['date'], reverse=True)
    return archives

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
    
    # Save posts to archive and update item with local path
    for post in feed_posts:
        local_path = save_article_to_archive(post, proxy_host)
        post['local_path'] = local_path # Store local path for README
        valid_links.append(post)
        
    # 2. 读取并转换推广链接 (Redirects)
    links_path = os.path.join(SITES_DIR, f"{site_id}_links.json")
    if os.path.exists(links_path):
        try:
            with open(links_path, 'r', encoding='utf-8') as f:
                links = json.load(f)
            
            for kw, url in links.items():
                if url.startswith('http'):
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

def generate_content(new_items, existing_archives, count=50):
    """生成 Markdown 内容
    new_items: 本次抓取的新内容（包含文章和推广链接）
    existing_archives: 本地已有的归档文章列表
    """
    
    # Merge articles: new articles from feed + existing archives
    # Use a dict to deduplicate by local_path or name
    all_articles = {}
    
    # Add existing archives first
    for item in existing_archives:
        all_articles[item['local_path']] = item
        
    # Add new articles (will overwrite if same path, which is fine)
    new_articles = [i for i in new_items if i.get('type') == 'article']
    for item in new_articles:
        if 'local_path' in item:
            all_articles[item['local_path']] = item
            
    # Convert back to list and sort by date
    sorted_articles = list(all_articles.values())
    sorted_articles.sort(key=lambda x: x.get('date', datetime.datetime.min), reverse=True)
    
    # Take top N articles for the main list
    display_articles = sorted_articles[:count]
    
    # Get referrals from new_items (referrals are not archived, just current)
    referrals = [i for i in new_items if i.get('type') != 'article']
    
    # 生成 Markdown
    today = datetime.date.today().strftime("%Y-%m-%d")
    md_content = f"# 每日科技资讯与网络加速归档 (Last Updated: {today})\n\n"
    
    md_content += "> 本项目自动抓取并归档最新的科技资讯、网络加速资源与教程。所有内容均已永久保存至 GitHub。\n\n"
    
    # 随机插入一些关键词段落
    tags = random.sample(KEYWORDS, min(5, len(KEYWORDS)))
    md_content += f"**热门标签**：{'、'.join(tags)}\n\n"
    
    md_content += "## 最新更新 (Recent Updates)\n\n"
    
    # List articles
    if display_articles:
        for item in display_articles:
            title = generate_title(item)
            link_url = item.get('local_path', item.get('url', '#'))
            
            # Date prefix
            date_str = item.get('date').strftime("%Y-%m-%d") if item.get('date') else ""
            
            md_content += f"### 📄 [{title}]({link_url})\n"
            if date_str:
                md_content += f"*{date_str}* - "
            
            # Add a small snippet if available
            if item.get('description'):
                # Take first 100 chars
                snippet = re.sub(r'<[^>]+>', '', item['description'])[:100] + "..."
                md_content += f"{snippet}\n\n"
            else:
                md_content += f"点击查看归档全文...\n\n"
    else:
        md_content += "暂无更新。\n\n"

    md_content += "## 推荐资源 (Recommended Resources)\n\n"
    
    if referrals:
        # Limit referrals to prevent clutter
        display_referrals = random.sample(referrals, min(10, len(referrals)))
        for item in display_referrals:
            title = generate_title(item)
            emoji = random.choice(["🚀", "⚡", "🌐", "🔥", "💡", "📝", "⭐", "💎"])
            
            md_content += f"### {emoji} [{title}]({item['url']})\n"
            
            desc_templates = [
                f"点击上方链接访问 {item['name']} 官网，获取最新优惠。",
                f"{item['name']} 是一款性价比极高的加速服务，支持多平台使用。",
                f"晚高峰 4K 视频秒开，{item['name']} 值得一试。",
                f"注册即可免费试用，{item['name']} 提供稳定高速的节点。",
                "专线接入，超低延迟，游戏/视频两不误。"
            ]
            md_content += f"{random.choice(desc_templates)}\n\n"
    
    # Archive Links Section
    md_content += "---\n"
    md_content += "## 历史归档 (History)\n\n"
    
    # Group by Year/Month
    archive_groups = {}
    for item in sorted_articles:
        if item.get('date'):
            key = item['date'].strftime("%Y年%m月")
            path = f"archives/{item['date'].strftime('%Y/%m')}/"
            archive_groups[key] = path
            
    for key, path in archive_groups.items():
         md_content += f"- [{key} 归档]({path})\n"
    
    md_content += "\n---\n"
    md_content += "### 免责声明\n"
    md_content += "本文内容仅供学习和技术交流使用，请勿用于非法用途。请遵守当地法律法规。\n\n"
    md_content += f"*自动更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return md_content

def main():
    print("开始生成内容...")
    
    # 1. Scan local archives first
    print("Scanning local archives...")
    existing_archives = scan_local_archives()
    print(f"Found {len(existing_archives)} existing archived articles.")

    # 2. 获取所有站点
    configs = get_all_site_configs()
    if not configs:
        print("No site configs found.")
        return

    # 3. 随机选择一个站点抓取新内容
    new_items = []
    
    random.shuffle(configs)
    
    for config in configs:
        print(f"Trying site: {config.get('name', config['id'])}")
        items = fetch_site_data(config)
        if items:
            new_items = items
            print(f"Successfully fetched {len(items)} items from {config['id']}")
            break
        print(f"No items found for {config['id']}, trying next...")
    
    # Note: Even if new_items is empty, we still want to regenerate README with existing archives
    if not new_items and not existing_archives:
        print("No content found (neither new nor archived).")
        return

    # 4. 生成内容 (Combine new and old)
    content = generate_content(new_items, existing_archives, count=50)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已生成至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()