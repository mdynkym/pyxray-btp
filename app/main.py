import os
import time
import socket
import subprocess

from .config import ENABLE_ARGO, FILE_PATH
from .utils import ensure_directory, clean_old_files
from .server import start_http_server
from .xray import generate_config, XRAY_PORT
from .runner import authorize_and_run
from .links import generate_subscription
from .meta import get_cf_meta, summarize_meta
from .hotspot import fetch_hot_topics
from .blog import render_blog_html, write_blog, write_news_pages

PUBLIC_DIR = os.path.join(FILE_PATH, "public")


def check_xray():
    print("\n--- Xray 启动检测 ---")
    # 进程
    try:
        ps_output = subprocess.check_output(['ps', 'aux'], text=True)
        proc_ok = 'xray' in ps_output
    except Exception as e:
        print(f"[错误] 检查进程失败: {e}")
        proc_ok = False
    # 配置
    cfg_ok = False
    cfg_path = os.path.join(FILE_PATH, 'config.json')
    if os.path.exists(cfg_path):
        try:
            result = subprocess.run([
                os.path.join(FILE_PATH, 'xray'), 'run', '-test', '-c', cfg_path
            ],
                                    capture_output=True,
                                    text=True)
            cfg_ok = (result.returncode == 0)
            if not cfg_ok:
                print(f"[错误] 配置文件无效: {result.stderr.strip()}")
        except Exception as e:
            print(f"[错误] 配置检查失败: {e}")
    else:
        print("[错误] 找不到 config.json")
    # 端口
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            port_ok = sock.connect_ex(('127.0.0.1', XRAY_PORT)) == 0
    except Exception as e:
        print(f"[错误] 检查端口失败: {e}")
        port_ok = False

    print(f"XRAY进程检查: {'✅ 正常' if proc_ok else '❌ 异常'}")
    print(f"配置文件检查: {'✅ 正常' if cfg_ok else '❌ 异常'}")
    print(f"端口监听检查: {'✅ 正常' if port_ok else '❌ 异常'}")
    if proc_ok and cfg_ok and port_ok:
        print("结论: ✅ Xray 正常运行\n")
    else:
        print("结论: ❌ Xray 异常，请检查日志和配置\n")


def check_cloudflared():
    print("\n--- Cloudflared 隧道检测 ---")
    # 进程
    try:
        ps_output = subprocess.check_output(['ps', 'aux'], text=True)
        proc_ok = 'cloudflared' in ps_output
    except Exception as e:
        print(f"[错误] 检查 Cloudflared 进程失败: {e}")
        proc_ok = False

    if proc_ok:
        print("✅ 隧道已连接 Cloudflare")
    else:
        print("❌ cloudflared 可能未启动，请检查 token 或网络")


def build_and_publish_blog():
    print("\n--- 生成节点所在地热点博客 ---")
    meta_raw = get_cf_meta()
    meta = summarize_meta(meta_raw) if meta_raw else {}
    topics = fetch_hot_topics(meta.get("city"), meta.get("country"))
    # 生成 news 下的静态页面
    topics_with_pages = write_news_pages(PUBLIC_DIR, meta, topics)
    # 首页用本地链接替换原链接
    html = render_blog_html(meta, topics_with_pages)
    path = write_blog(PUBLIC_DIR, html)
    print(f"博客已生成：{path}")


def main():
    ensure_directory()
    clean_old_files()

    build_and_publish_blog()

    start_http_server()
    generate_config()

    # 启动 Xray / cloudflared
    authorize_and_run()

    time.sleep(3)  # 给进程一点时间启动

    # 检测 Xray
    check_xray()

    # 检测 cloudflared
    if ENABLE_ARGO:
        check_cloudflared()

    # 生成订阅
    generate_subscription()

    while True:
        time.sleep(3600)


if __name__ == '__main__':
    main()
