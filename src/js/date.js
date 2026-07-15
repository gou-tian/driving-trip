/* ============================================================
 * 出发日期动态化 · date.js
 *
 * 数据流:
 *   默认值  ◀── trip.json[0].date_full (2026/07/23)
 *   URL     ◀── ?date=YYYY-MM-DD
 *   本地     ◀── localStorage["xj-depart-date"]
 *
 * DOM 标记约定(由 render.py 注入):
 *   <input type="date" id="xj-depart-date" data-default="2026-07-23">
 *   <span data-xj-date="depart|format">2026/07/23</span>
 *   <span data-xj-date="return|format">2026/08/11</span>
 *   <span data-xj-day-num="N">2026/07/23</span>
 *   <span data-xj-day-short="N">7/23(周四)</span>
 *   <table> 内的 tr 加 data-xj-row-num="N"
 *
 * 广播:日期变化时派发 window 'xj-depart-date-changed' 事件,
 *       weather.js 监听后自动重查天气。
 * ============================================================ */

(function () {
  "use strict";

  const STORAGE_KEY = "xj-depart-date";
  const DEFAULT_ISO = "2026-07-23"; // 与 trip.json[0].date_full 锚定
  const TRIP_DAYS = 20; // D1..D20
  const WK = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];

  // ============================================================
  // 工具
  // ============================================================
  function pad2(n) {
    return n < 10 ? "0" + n : "" + n;
  }

  function isoToDate(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    return new Date(y, m - 1, d);
  }

  function dateToISO(d) {
    return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
  }

  function dateToSlash(d) {
    return d.getFullYear() + "/" + pad2(d.getMonth() + 1) + "/" + pad2(d.getDate());
  }

  function dateToShort(d) {
    return d.getMonth() + 1 + "/" + d.getDate() + "(" + WK[d.getDay()] + ")";
  }

  function offsetDays(iso, n) {
    const d = isoToDate(iso);
    d.setDate(d.getDate() + n);
    return d;
  }

  function isValidISO(s) {
    return typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s);
  }

  // ============================================================
  // 优先级:URL > localStorage > 默认值
  // ============================================================
  function readFromURL() {
    try {
      const u = new URL(window.location.href);
      const v = u.searchParams.get("date");
      return isValidISO(v) ? v : null;
    } catch {
      return null;
    }
  }

  function readFromStorage() {
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      return isValidISO(v) ? v : null;
    } catch {
      return null;
    }
  }

  function writeToStorage(iso) {
    try {
      localStorage.setItem(STORAGE_KEY, iso);
    } catch {}
  }

  function clearStorage() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {}
  }

  function writeToURL(iso) {
    try {
      const u = new URL(window.location.href);
      u.searchParams.set("date", iso);
      window.history.replaceState(null, "", u.toString());
    } catch {}
  }

  // ============================================================
  // 当前生效日期(对外暴露窗口全局)
  // ============================================================
  let currentISO = DEFAULT_ISO;

  function resolveInitial() {
    const fromURL = readFromURL();
    if (fromURL) {
      currentISO = fromURL;
      writeToStorage(fromURL);
      return;
    }
    const fromStorage = readFromStorage();
    if (fromStorage) {
      currentISO = fromStorage;
      writeToURL(fromStorage);
      return;
    }
    currentISO = DEFAULT_ISO;
  }

  // ============================================================
  // DOM 应用
  // ============================================================
  function applyAll() {
    // 1. hero 区 input 同步
    document.querySelectorAll("[data-xj-depart-input]").forEach((el) => {
      const dflt = el.getAttribute("data-default") || DEFAULT_ISO;
      if (!readFromStorage() && !readFromURL()) {
        // 第一次访问:用 data-default
        currentISO = dflt;
      }
      el.value = currentISO;
    });

    // 2. 出发/返程/抵达(及任意 [data-xj-date="KEY|format"])
    document.querySelectorAll("[data-xj-date]").forEach((el) => {
      const spec = el.getAttribute("data-xj-date"); // 例:"depart|format"
      const [key, fmt] = spec.split("|");
      let d;
      switch (key) {
        case "depart":
          d = isoToDate(currentISO);
          break;
        case "return":
          d = offsetDays(currentISO, TRIP_DAYS - 1); // D20 = 返程 = depart + 19
          break;
        case "arrive":
          d = offsetDays(currentISO, TRIP_DAYS); // D20 抵达 = depart + 20
          break;
        default:
          return;
      }
      el.textContent =
        fmt === "short"
          ? dateToShort(d)
          : fmt === "dash"
            ? d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate())
            : dateToSlash(d);
    });

    // 3. 行程卡片 / 表格:data-xj-day-num / data-xj-day-short
    document.querySelectorAll("[data-xj-day-num]").forEach((el) => {
      const n = parseInt(el.getAttribute("data-xj-day-num"), 10);
      if (!isFinite(n)) return;
      el.textContent = dateToSlash(offsetDays(currentISO, n - 1));
    });
    document.querySelectorAll("[data-xj-day-short]").forEach((el) => {
      const n = parseInt(el.getAttribute("data-xj-day-short"), 10);
      if (!isFinite(n)) return;
      el.textContent = dateToShort(offsetDays(currentISO, n - 1));
    });

    // 4. weather-block 的 data-date(IS0 格式)与 day-num 同步
    document.querySelectorAll("[data-xj-row-num]").forEach((row) => {
      const n = parseInt(row.getAttribute("data-xj-row-num"), 10);
      if (!isFinite(n)) return;
      const block = row.querySelector(".weather-block[data-date]");
      const cell = row.querySelector("[data-xj-day-short], [data-xj-day-num]");
      const newISO = dateToISO(offsetDays(currentISO, n - 1));
      if (block) block.setAttribute("data-date", newISO);
      if (cell && cell.hasAttribute("data-xj-day-short"))
        cell.textContent = dateToShort(offsetDays(currentISO, n - 1));
      if (cell && cell.hasAttribute("data-xj-day-num"))
        cell.textContent = dateToSlash(offsetDays(currentISO, n - 1));
    });

    // 5. JSON-LD datePublished(若有)
    document.querySelectorAll('script[type="application/ld+json"]').forEach((s) => {
      try {
        const obj = JSON.parse(s.textContent);
        if (obj && obj.datePublished && /^D\d+$/i.test(obj.headline || "")) {
          const m = obj.headline.match(/D(\d+)/i);
          if (m) {
            const n = parseInt(m[1], 10);
            obj.datePublished = dateToSlash(offsetDays(currentISO, n - 1));
            s.textContent = JSON.stringify(obj);
          }
        }
      } catch {}
    });
  }

  function setDepart(iso) {
    if (!isValidISO(iso)) return;
    currentISO = iso;
    writeToStorage(iso);
    writeToURL(iso);
    applyAll();
    window.dispatchEvent(
      new CustomEvent("xj-depart-date-changed", { detail: { iso: currentISO } }),
    );
  }

  // ============================================================
  // input 监听
  // ============================================================
  function bindInputs() {
    document.querySelectorAll("[data-xj-depart-input]").forEach((el) => {
      el.addEventListener("change", (e) => {
        const v = e.target.value;
        if (isValidISO(v)) setDepart(v);
      });
    });
  }

  // ============================================================
  // 启动
  // ============================================================
  function init() {
    resolveInitial();
    applyAll();
    bindInputs();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // 暴露:天气刷新、其他脚本可调用
  window.__xjDepartISO = () => currentISO;
  window.__xjDepartDate = () => isoToDate(currentISO);
  window.__xjApplyDepart = setDepart;
  window.__xjDayISO = (n) => dateToISO(offsetDays(currentISO, n - 1));
})();
