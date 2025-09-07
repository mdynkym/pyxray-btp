
# Xray + Cloudflared SAP BTP平台 与 VPS 双模式版

## 📌 项目简介

这是一个集成了 **Xray 代理**、**Cloudflared 隧道**、**热点博客伪装** 的一键部署项目，支持：

- **双模式运行**：
  - `argo` 模式：Xray 内部端口 + Cloudflared HTTP/2 隧道（可选 SNI 伪装）
  - `direct` 模式：Xray 直连公网端口（VPS 用）
- **节点所在地热点博客伪装**：
  - 启动时获取 Cloudflare meta → 自动匹配语言/地区 → 拉取 Google News RSS → 生成 HTML 博客
  - `/` 显示博客，`SUB_PATH` 输出订阅（需 `SUB_TOKEN` 验证）
- **健康检测**：
  - Xray：进程 / 配置 / 端口
  - Cloudflared：进程检测（兼容固定隧道）
- **安全增强**：
  - 订阅路径可自定义（`SUB_PATH`）
  - 访问需密码（`SUB_TOKEN`）

---

## 📂 目录结构

    app/ 
      config.py # 配置与环境变量 
      utils.py # 工具函数 
      meta.py # 获取 Cloudflare meta 
      hotspot.py # 拉取热点新闻 
      blog.py # 生成 HTML 博客 
      server.py # HTTP 服务（博客 + 订阅） 
      xray.py # 生成 Xray 配置 
      runner.py # 启动 Xray / Cloudflared 
      links.py # 生成订阅文件 
      main.py # 启动流程入口 
    requirements.txt # Python 依赖 
    Procfile # BTP 启动命令 
    manifest.yml # BTP 部署配置 
    runtime.txt # Python 运行时版本

---

## ⚙️ 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `MODE` | 运行模式：`argo` 或 `direct` | `argo` |
| `UUID` | VLESS 用户 UUID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `XRAY_PORT` | Xray监听端口 | `3001` |
| `FAKE_SNI` | 可选，Cloudflared SNI 伪装域名 | `www.visa.com.sg` |
| `ARGO_TOKEN` | 可选，Cloudflared 固定隧道 token | `<token>` |
| `DOMAIN` | 指向Argo 或 公网端口（VPS） | `xxx.xxx.com` |
| `PORT` | 博客 HTTP 服务端口 | `8080` |
| `SUB_PATH` | 订阅路径 | `/api/sub` |
| `SUB_TOKEN` | 订阅访问密码 | `mysecret` |

---

## 🚀 部署方法

### **BTP（Cloudflared 模式）**

在根目录下先将 manifest.template.yml 复制改名为 manifest.yml 相应值改正确，然后直接：

cf push

或者在 app 目录下：

cf push myapp \
  -b python_buildpack \
  -m 256M \
  -k 512M \
  -c "python main.py" \
  -e MODE=argo \
  -e UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  -e XRAY_PORT=3001 \
  -e DOMAIN=xxx.xxx.com \
  -e FAKE_SNI=www.visa.com.sg \
  -e SUB_PATH=/api/sub \
  -e SUB_TOKEN=mysecret

**访问订阅**

  https://app里面btp平台分配的域名/api/sub?token=mysecret

或者app日志里面查看

### **VPS（直连/Argo模式）**

先安装依赖，在运行：

export MODE=direct
export UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export XRAY_PORT=443
export DOMAIN=xxx.xxx.com
export FAKE_SNI=www.visa.com.sg
export PORT=8080
export SUB_PATH=/api/sub
export SUB_TOKEN=mysecret
python3 main.py

**访问订阅**

  https://你的域名:PORT/api/sub?token=mysecret

---

## 🌐 访问说明

### 博客首页：/

显示节点所在地的热点新闻（自动本地化语言）

### 订阅地址：SUB_PATH + token

例如 /api/sub?token=mysecret

## 🛠 健康检测

启动时会自动检测：

### Xray 进程 / 配置 / 端口

### Cloudflared 进程（argo 模式）

## 📜 许可证

本项目仅供学习与研究使用，请勿用于违反当地法律法规的用途。
