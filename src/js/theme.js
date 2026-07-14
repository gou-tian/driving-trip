/* ============================================================
 * 暗色模式切换 · theme.js
 *
 * 工作原理:
 *   1. 启动时读 localStorage.theme
 *   2. 设 :root[data-theme="dark"|"light"]
 *   3. 切换按钮触发 <html> 上 data-theme 翻转
 * ============================================================ */

(function () {
  "use strict";

  const STORAGE_KEY = "xj-theme";
  const root = document.documentElement;

  function getSystemPref() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function getStored() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return null;
    }
  }

  function setStored(theme) {
    try {
      if (theme) localStorage.setItem(STORAGE_KEY, theme);
      else localStorage.removeItem(STORAGE_KEY);
    } catch {}
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      root.setAttribute("data-theme", "dark");
    } else if (theme === "light") {
      root.setAttribute("data-theme", "light");
    } else {
      root.removeAttribute("data-theme"); // 跟随系统
    }
  }

  function currentTheme() {
    const attr = root.getAttribute("data-theme");
    if (attr === "dark" || attr === "light") return attr;
    return getSystemPref();
  }

  function toggle() {
    const next = currentTheme() === "dark" ? "light" : "dark";
    applyTheme(next);
    setStored(next);
    updateButtons();
  }

  function updateButtons() {
    const theme = currentTheme();
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      const label = theme === "dark" ? "☀ 切到浅色" : "🌙 切到深色";
      btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
      btn.setAttribute("aria-label", label);
      btn.textContent = label;
    });
  }

  // 启动:应用 stored 或系统偏好
  const stored = getStored();
  if (stored === "dark" || stored === "light") {
    applyTheme(stored);
  } else {
    applyTheme(null); // 跟随系统
  }

  // 监听系统偏好变化(仅在用户未手动选过)
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!getStored()) applyTheme(null);
  });

  // 暴露 toggle
  window.__toggleTheme = toggle;
  window.__updateThemeButtons = updateButtons;

  // DOM ready 后挂按钮
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateButtons);
  } else {
    updateButtons();
  }

  // 任意按钮点击事件代理
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-theme-toggle]");
    if (btn) {
      e.preventDefault();
      toggle();
    }
  });
})();
