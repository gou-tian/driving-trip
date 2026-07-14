#!/usr/bin/env bash
# ============================================================
#   deploy.sh · 一键部署 新疆自驾 dist/ → gtian.cn
# ============================================================
# 用法:
#   ./scripts/deploy.sh              # 默认部署(走公钥)
#   ./scripts/deploy.sh --dry-run    # 只构建 + rsync --dry-run,不上传
#   ./scripts/deploy.sh --skip-build # 跳过 build,直接用现成 dist/
#   ./scripts/deploy.sh --rollback   # 回滚到最近一次备份
#
# 配置:修改下方 DEPLOY_* 变量即可
# ============================================================
set -euo pipefail

# ---------- 配置 ----------
DEPLOY_HOST="gtian.cn"
DEPLOY_USER="ubuntu"
DEPLOY_SSH_KEY="/Users/goutian/资料/个人资料/qq-cloud/QQ20270207.pem"
DEPLOY_REMOTE_DIR="/www/wwwroot/trip.gtian.cn/xinjiang"
DEPLOY_PUBLIC_URL="https://trip.gtian.cn/xinjiang/"

# ---------- 路径 ----------
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$HERE/dist"

# ---------- 参数 ----------
DRY_RUN=false
SKIP_BUILD=false
ROLLBACK=false
for arg in "$@"; do
  case "$arg" in
    --dry-run)    DRY_RUN=true ;;
    --skip-build) SKIP_BUILD=true ;;
    --rollback)   ROLLBACK=true ;;
    -h|--help)
      grep -E '^#( |$)' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *) echo "未知参数: $arg"; exit 1 ;;
  esac
done

SSH_OPTS=(-i "$DEPLOY_SSH_KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15)
SSH="ssh ${SSH_OPTS[*]} ${DEPLOY_USER}@${DEPLOY_HOST}"

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
yello() { printf '\033[33m%s\033[0m\n' "$*"; }
step()  { printf '\n\033[36m▶ %s\033[0m\n' "$*"; }

# ---------- 远端权限检测 ----------
SUDO=""
if [[ -z "${DEPLOY_NO_SUDO:-}" ]]; then
  if ! $SSH "test -w '$DEPLOY_REMOTE_DIR'" 2>/dev/null; then
    if $SSH "sudo -n true" 2>/dev/null; then
      SUDO="sudo"
      yello "→ 检测到 ${DEPLOY_REMOTE_DIR} 无写权限,自动启用 sudo"
    else
      red "❌ 远端目录无写权限,且 sudo 需要密码"
      red "   请用 www 用户 ssh,或 chown -R ubuntu $DEPLOY_REMOTE_DIR"
      exit 1
    fi
  fi
fi

# ---------- 步骤 ----------
step "1/5  预检"
if [[ ! -f "$DEPLOY_SSH_KEY" ]]; then
  red "❌ SSH 公钥不存在: $DEPLOY_SSH_KEY"
  exit 1
fi
chmod 600 "$DEPLOY_SSH_KEY" 2>/dev/null || true
green "✅ SSH key OK"

if ! command -v rsync >/dev/null; then red "❌ 需要 rsync"; exit 1; fi
if ! command -v python3 >/dev/null; then red "❌ 需要 python3"; exit 1; fi
green "✅ 工具链 OK"

# ---------- 回滚模式 ----------
if $ROLLBACK; then
  step "ROLLBACK: 找最近备份"
  BACKUP=$($SSH "ls -dt ${DEPLOY_REMOTE_DIR}.bak.* 2>/dev/null | head -1" || true)
  if [[ -z "$BACKUP" ]]; then
    red "❌ 没找到备份目录(${DEPLOY_REMOTE_DIR}.bak.*)"
    exit 1
  fi
  yello "→ 最新备份: $BACKUP"
  $SSH "$SUDO mv '$DEPLOY_REMOTE_DIR' '$DEPLOY_REMOTE_DIR'.broken.\$(date +%H%M%S)" \
    && $SSH "$SUDO mv '$BACKUP' '$DEPLOY_REMOTE_DIR'" \
    || { red "❌ 回滚失败"; exit 1; }
  $SSH "$SUDO chown -R www:www '$DEPLOY_REMOTE_DIR'" 2>/dev/null || true
  green "✅ 回滚完成"
  exit 0
fi

# ---------- 2. 构建 ----------
if ! $SKIP_BUILD; then
  step "2/5  构建 dist/"
  ( cd "$HERE" && python3 -m scripts.build --clean )
else
  step "2/5  跳过构建 (--skip-build)"
  if [[ ! -d "$DIST" ]]; then red "❌ dist/ 不存在,先去掉 --skip-build"; exit 1; fi
fi

FILE_COUNT=$(find "$DIST" -type f | wc -l | tr -d ' ')
TOTAL_KB=$(du -sk "$DIST" | cut -f1)
yello "→ $FILE_COUNT 个文件 · ${TOTAL_KB} KB"

if $DRY_RUN; then
  step "3/5  DRY RUN: rsync 不真传"
  rsync -avzn --delete --exclude='.DS_Store' \
    -e "ssh ${SSH_OPTS[*]}" \
    "$DIST/" "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_REMOTE_DIR}/"
  green "✅ Dry run 完成(没真改)"
  exit 0
fi

# ---------- 3. 备份旧版 ----------
step "3/5  备份旧版"
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="${DEPLOY_REMOTE_DIR}.bak.${STAMP}"
if $SSH "[ -d '$DEPLOY_REMOTE_DIR' ]"; then
  $SSH "$SUDO mv '$DEPLOY_REMOTE_DIR' '$BACKUP_PATH'" \
    && yello "→ 已备份到 $BACKUP_PATH" \
    || { red "❌ 备份失败(可能需要 sudo)"; exit 1; }
else
  yello "→ 线上为空,跳过备份"
fi
green "✅ 备份就绪"

# ---------- 4. rsync 上传 ----------
step "4/5  上传 dist/ → ${DEPLOY_USER}@${DEPLOY_HOST}"
$SSH "$SUDO mkdir -p '$DEPLOY_REMOTE_DIR'" || { red "❌ 创建远端目录失败"; exit 1; }
RSYNC_PATH_FLAG=()
[[ -n "$SUDO" ]] && RSYNC_PATH_FLAG=(--rsync-path="sudo rsync")
rsync -avz --delete --no-perms --no-owner --no-group --exclude='.DS_Store' \
  -e "ssh ${SSH_OPTS[*]}" \
  "${RSYNC_PATH_FLAG[@]}" \
  "$DIST/" "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_REMOTE_DIR}/" \
  | tail -10
green "✅ 上传完成"

# 把上传后的目录 owner 改成 www(nginx/PHP worker 用户),保证静态服务能读
if [[ -n "$SUDO" ]]; then
  $SSH "$SUDO chown -R www:www '$DEPLOY_REMOTE_DIR'" || yello "⚠️ chown www:www 失败(可能 www 用户不存在)"
fi

# ---------- 5. 在线验证 ----------
step "5/5  在线验证"
sleep 1
if ! curl -fsSI --max-time 10 "$DEPLOY_PUBLIC_URL" >/dev/null; then
  red "❌ 访问 $DEPLOY_PUBLIC_URL 失败"
  yello "→ 自动回滚中..."
  $SSH "mv '$DEPLOY_REMOTE_DIR' '$DEPLOY_REMOTE_DIR'.bad.\$STAMP && mv '$BACKUP_PATH' '$DEPLOY_REMOTE_DIR'"
  red "已回滚,排查问题再试"
  exit 1
fi
green "✅ HTTP 200 OK"

# spot checks
for path in "" "day/day-01.html" "amap/index.html" "sitemap.xml" "robots.txt" "manifest.webmanifest"; do
  STATUS=$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 10 "${DEPLOY_PUBLIC_URL}${path}")
  printf '   %-40s %s\n' "${path:-/}" "$STATUS"
done

# 关键内容 sanity check
if curl -fsS --max-time 10 "${DEPLOY_PUBLIC_URL}" | grep -q '新疆自驾 20 天'; then
  green "✅ 页面含网站标题"
else
  red "❌ 页面未含预期内容"
fi

if curl -fsS --max-time 10 "${DEPLOY_PUBLIC_URL}day/day-01.html" | grep -qE 'class="topbar"'; then
  green "✅ 顶部导航渲染正确"
else
  red "❌ 顶部导航渲染异常"
fi

# ---------- 6. 清理旧备份(>7 天) ----------
step "6/6  清理 7 天以上旧备份"
$SSH "find $(dirname "$DEPLOY_REMOTE_DIR") -maxdepth 1 -type d -name 'xinjiang.bak.*' -mtime +7 -exec rm -rf {} + 2>/dev/null; true"
green "✅ 完成"

step "总览"
yello "线上地址: $DEPLOY_PUBLIC_URL"
yello "本机备份: $BACKUP_PATH  (7 天后自动清理)"
yello "回滚命令: $0 --rollback"
green "🎉 部署成功!"
