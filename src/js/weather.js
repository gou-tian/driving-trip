/* ============================================================
 * 实时天气查询 · Open-Meteo(免费、无 key、CORS 友好)
 *
 * 数据源:
 *   https://api.open-meteo.com/v1/forecast
 *
 * 用法(在 HTML 标记上):
 *   <div class="weather-block"
 *        data-lat="37.5149"
 *        data-lon="105.1856"
 *        data-date="2026-07-25">
 *     <!-- 以下是 fallback 静态值,JS 拉到数据会平滑覆盖 -->
 *     <span class="temp">22–34℃</span>
 *     <span class="desc">晴</span>
 *     <span class="uv">强</span>
 *   </div>
 *
 * 预报范围:今天 + 16 天。日期超出会 fallback 到静态值。
 * ============================================================ */

(function () {
  "use strict";

  // ============================================================
  // WMO 天气代码 → 中文短描述
  // 来源:https://open-meteo.com/en/docs
  // ============================================================
  const WMO = {
    0: "晴",
    1: "晴间多云",
    2: "多云",
    3: "阴",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "中毛毛雨",
    55: "强毛毛雨",
    56: "冻毛毛雨",
    57: "强冻毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "强冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "阵雨",
    81: "强阵雨",
    82: "暴阵雨",
    85: "阵雪",
    86: "强阵雪",
    95: "雷暴",
    96: "雷暴伴小冰雹",
    99: "雷暴伴大冰雹",
  };

  // UV index 等级(中国标准)
  const UV_LEVEL = [
    [0, 2, "弱", "#3a9"],
    [3, 5, "中等", "#da3"],
    [6, 7, "强", "#e80"],
    [8, 10, "很强", "#e33"],
    [11, 99, "极强", "#c0c"],
  ];

  function uvLevel(idx) {
    for (const [lo, hi, label, color] of UV_LEVEL) {
      if (idx >= lo && idx <= hi) return { label, color };
    }
    return { label: "弱", color: "#3a9" };
  }

  // ============================================================
  // 工具:DOM 创建(避免 innerHTML)
  // ============================================================
  function makeSpan(className, text, style) {
    const s = document.createElement("span");
    s.className = className;
    s.textContent = text;
    if (style) s.style.cssText = style;
    return s;
  }

  // ============================================================
  // 工具:日期范围 + 边界分类(本地浏览器时间)
  // ============================================================
  function boundary() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const max = new Date(today);
    max.setDate(max.getDate() + 15); // Open-Meteo horizon = today + 15d
    const fmt = (d) =>
      `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    return { today, max, todayStr: fmt(today), maxStr: fmt(max) };
  }

  function classifyDate(dateStr) {
    const { maxStr } = boundary();
    const mmdd = (s) => s.slice(5).replace("-", "/");
    // 用 ISO 字符串字典序比较,避免 new Date() 时区错位
    if (dateStr > maxStr) {
      return {
        status: "out-of-range",
        msg: `超出预报窗口(截至 ${mmdd(maxStr)}),刷新无效`,
      };
    }
    return { status: "in-range" };
  }

  function nowTimeStr() {
    const d = new Date();
    return `${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
  }

  // 兼容旧调用(name 仍保留)
  function getForecastRange() {
    const { today, max } = boundary();
    return { today, max };
  }

  function isInForecast(targetDateStr) {
    const { todayStr, maxStr } = boundary();
    return targetDateStr >= todayStr && targetDateStr <= maxStr;
  }

  // ============================================================
  // 缓存:同 lat/lon 的请求合并
  // ============================================================
  const cache = new Map();
  function getWeather(lat, lon, startDate, endDate) {
    const key = `${lat.toFixed(3)},${lon.toFixed(3)}|${startDate}|${endDate}`;
    if (cache.has(key)) return cache.get(key);

    const url =
      "https://api.open-meteo.com/v1/forecast" +
      "?latitude=" +
      lat +
      "&longitude=" +
      lon +
      "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,wind_speed_10m_max,uv_index_max" +
      "&timezone=Asia%2FShanghai" +
      "&start_date=" +
      startDate +
      "&end_date=" +
      endDate;

    const promise = fetch(url, { mode: "cors" })
      .then((r) => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .catch((err) => {
        cache.delete(key);
        throw err;
      });

    cache.set(key, promise);
    return promise;
  }

  // ============================================================
  // 状态显示:loading / out-of-range / error
  // ============================================================
  function clearBlock(block) {
    while (block.firstChild) block.removeChild(block.firstChild);
  }

  function showLoading(block) {
    clearBlock(block);
    block.appendChild(makeSpan("note", "⏳ 加载中…"));
    block.dataset.weatherStatus = "loading";
  }

  function showOutOfRange(block, msg) {
    clearBlock(block);
    block.appendChild(makeSpan("note", "⚠️ " + msg));
    block.appendChild(makeRefreshBtn(block));
    block.dataset.weatherStatus = "out-of-range";
  }

  function showError(block, fallbackText) {
    clearBlock(block);
    block.appendChild(makeSpan("note", "⚠️ API 暂不可达,显示静态值"));
    block.appendChild(document.createElement("br"));
    block.appendChild(makeSpan("temp", fallbackText));
    block.appendChild(makeRefreshBtn(block));
    block.dataset.weatherStatus = "static";
  }

  // ============================================================
  // 刷新按钮 + 时间戳 + meta 容器
  // ============================================================
  function makeRefreshBtn(block) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "weather-refresh";
    b.textContent = "🔄";
    b.title = "刷新实时天气";
    b.setAttribute("aria-label", "刷新实时天气");
    b.onclick = async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const lat = parseFloat(block.dataset.lat);
      const lon = parseFloat(block.dataset.lon);
      const d = block.dataset.date;
      const key = `${lat.toFixed(3)},${lon.toFixed(3)}|${d}|${d}`;
      cache.delete(key); // 强制重拉
      showLoading(block);
      await updateBlock(block);
    };
    return b;
  }

  function makeTimestamp(dateStr) {
    const s = document.createElement("span");
    s.className = "weather-timestamp";
    s.textContent =
      "📅 " + dateStr.slice(5).replace("-", "/") + " · 🕐 " + nowTimeStr() + " · 🌐 Open-Meteo";
    return s;
  }

  function makeMeta(dateStr, block) {
    const span = document.createElement("span");
    span.className = "weather-meta";
    span.appendChild(makeTimestamp(dateStr));
    span.appendChild(makeRefreshBtn(block));
    return span;
  }

  // ============================================================
  // 更新单个 weather-block
  // ============================================================
  async function updateBlock(block) {
    const lat = parseFloat(block.dataset.lat);
    const lon = parseFloat(block.dataset.lon);
    const date = block.dataset.date;

    if (!isFinite(lat) || !isFinite(lon) || !date) {
      block.dataset.weatherStatus = "static";
      return;
    }

    // 记录 fallback 以备失败时用
    if (!block.dataset.fallback) {
      block.dataset.fallback = block.textContent.trim();
    }

    const cls = classifyDate(date);
    if (cls.status === "out-of-range") {
      showOutOfRange(block, cls.msg);
      return;
    }

    // 进入过渡态
    if (block.dataset.weatherStatus !== "loading") showLoading(block);

    try {
      const data = await getWeather(lat, lon, date, date);
      const daily = data.daily;
      const idx = daily.time.indexOf(date);
      if (idx < 0) throw new Error("日期不在响应里");

      const tmax = Math.round(daily.temperature_2m_max[idx]);
      const tmin = Math.round(daily.temperature_2m_min[idx]);
      const code = daily.weather_code[idx];
      const desc = WMO[code] || "天气 " + code;
      const uv = daily.uv_index_max[idx];
      const uvInfo = uvLevel(Math.round(uv));
      const wind = daily.wind_speed_10m_max[idx];
      const precip = daily.precipitation_sum[idx];

      // 用 clearBlock 替换旧 while 循环
      clearBlock(block);

      block.appendChild(makeSpan("temp", tmin + "–" + tmax + "℃"));
      block.appendChild(document.createTextNode(" · "));
      block.appendChild(makeSpan("desc", desc));
      block.appendChild(document.createTextNode(" · "));
      block.appendChild(
        makeSpan(
          "uv",
          "☀ UV " + Math.round(uv) + "(" + uvInfo.label + ")",
          "color:" + uvInfo.color,
        ),
      );
      block.appendChild(document.createTextNode(" · "));
      block.appendChild(makeSpan("wind", "🌬 " + Math.round(wind) + " km/h"));
      if (precip > 0) {
        block.appendChild(document.createTextNode(" · "));
        block.appendChild(makeSpan("precip", "🌧 " + precip.toFixed(1) + " mm"));
      }
      block.appendChild(document.createTextNode(" · "));
      block.appendChild(makeSpan("live-tag", "📡 实时预报", "color:#2c7a4a;font-weight:600"));

      // 追加 meta(时间戳 + 刷新按钮)
      block.appendChild(makeMeta(date, block));

      block.dataset.weatherStatus = "live";
    } catch (err) {
      console.warn("[weather] 实时查询失败,保留静态:", err.message);
      showError(block, block.dataset.fallback || "22–34℃");
    }
  }

  // ============================================================
  // 启动
  // ============================================================
  function run() {
    const blocks = document.querySelectorAll(".weather-block[data-lat]");
    if (!blocks.length) return;

    showStatusBanner(blocks, blocks.length);

    blocks.forEach(updateBlock);
  }

  // ============================================================
  // 日期变化时(date.js 派发的 xj-depart-date-changed)重查所有 block
  // ============================================================
  function rerun() {
    run();
  }

  // 暴露给 date.js / 控制台调试
  window.__xjWeatherRefresh = rerun;

  function showStatusBanner(blocks, count) {
    const banner = document.createElement("div");
    banner.id = "weather-status";
    const span = document.createElement("span");
    span.className = "ws-loading";
    span.textContent = "⏳ 查询 " + count + " 天 Open-Meteo 预报…";
    banner.appendChild(span);
    banner.style.cssText = [
      "position: fixed",
      "bottom: 12px",
      "right: 12px",
      "background: rgba(28,95,163,0.92)",
      "color: white",
      "padding: 8px 14px",
      "border-radius: 20px",
      "font-size: 12px",
      "box-shadow: 0 2px 10px rgba(0,0,0,0.15)",
      "z-index: 999",
      'font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif',
      "transition: opacity 0.3s",
    ].join(";");
    document.body.appendChild(banner);

    const obs = new MutationObserver(() => {
      const all = document.querySelectorAll(".weather-block[data-lat]");
      const allDone = [...all].every(
        (b) =>
          b.dataset.weatherStatus === "live" ||
          b.dataset.weatherStatus === "static" ||
          b.dataset.weatherStatus === "out-of-range",
      );
      if (allDone) {
        const live = document.querySelectorAll('[data-weather-status="live"]').length;
        const out = document.querySelectorAll('[data-weather-status="out-of-range"]').length;
        const ok = live + out;
        if (ok === count) {
          banner.textContent =
            "✅ " + live + " 天实时 · " + out + " 天超界 · " + (count - ok) + " 天静态";
        } else {
          banner.textContent = "⏸ API 不可达,部分使用静态值";
        }
        banner.style.opacity = "0.7";
        setTimeout(function () {
          banner.style.display = "none";
        }, 3500);
        obs.disconnect();
      }
    });
    blocks.forEach((b) => {
      obs.observe(b, {
        attributes: true,
        attributeFilter: ["data-weather-status"],
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  // 出发日期变化(date.js 派发) → 只重新查询,不再显示 banner
  window.addEventListener("xj-depart-date-changed", () => {
    document.querySelectorAll(".weather-block[data-lat]").forEach((b) => {
      b.removeAttribute("data-weather-status");
      updateBlock(b);
    });
  });
})();
