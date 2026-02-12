# 记录一次 Autoptimize 插件引起的服务器资源被攻击者恶意耗尽问题的解决过程

**发布时间**: 2025-11-21 10:41

## 摘要

<p>本文记录了一次由 WordPress 优化插件 Autoptimize 引起的服务器资源异常消耗问题。通过日志分析，发现攻击者利用畸形请求 (/data:text/javascript&#8230;) 绕过正常的静态文件处理，强制触发 ph [&#8230;]</p>
<p><a href="https://laowangblog.yss.best/autoptimize-php-fpm-100-issue.html">记录一次 Autoptimize 插件引起的服务器资源被攻击者恶意耗尽问题的解决过程</a>最先出现在<a href="https://laowangblog.yss.best">老王博客</a>。</p>


---

## 阅读全文

[点击此处阅读完整文章](https://laowangblog.yss.best/autoptimize-php-fpm-100-issue.html)

---
*本文章自动归档，原始内容来自 [laowangblog.yss.best](https://laowangblog.yss.best)*
