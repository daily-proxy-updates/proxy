import os
import json
import random
import datetime

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
            
            # 收集该站点的链接
            valid_links = []
            
            # 1. 如果有 links 文件，读取推荐链接
            if os.path.exists(links_path):
                with open(links_path, 'r', encoding='utf-8') as f:
                    links = json.load(f)
                
                for kw, url in links.items():
                    if url.startswith('http'):
                        valid_links.append({
                            'name': kw, # 原始关键词
                            'url': url,
                            'type': 'referral'
                        })
            
            # 2. 将站点本身也作为一个推荐（如果是镜像站）
            if site_config.get('proxyHost'):
                valid_links.append({
                    'name': site_config.get('name', site_id),
                    'url': f"https://{site_config['proxyHost']}",
                    'type': 'site'
                })

            if valid_links:
                sites_data.append({
                    'site_name': site_config.get('name', site_id),
                    'links': valid_links
                })
                
        except Exception as e:
            print(f"Error processing {site_id}: {e}")
        
    return sites_data

def generate_title(item):
    """根据链接类型生成标题"""
    name = item['name']
    # 首字母大写
    name = name.capitalize() if name else "Unknown"
    
    template = random.choice(TITLE_TEMPLATES)
    return template.format(name=name)

def generate_content(sites_data, count=15):
    """生成 Markdown 内容"""
    all_items = []
    
    # 展平所有链接
    for site in sites_data:
        for link in site['links']:
            all_items.append(link)
    
    if not all_items:
        return "No articles found."

    # 随机选择指定数量的文章
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
    sites = load_sites_and_links()
    content = generate_content(sites, count=random.randint(10, 20))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已生成至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
