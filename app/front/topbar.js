(function () {
  'use strict';

  function initTopbar() {
  // ─── CONFIG ───
  const isChatPage = location.pathname === '/chat';

  // ─── INSERT CSS ───
  const style = document.createElement('style');
  style.textContent = `
    .topbar {
      position: fixed; top: 0; left: 0; right: 0;
      height: 50px;
      background: rgba(244,246,251,.94);
      backdrop-filter: blur(20px) saturate(180%);
      border-bottom: 1px solid rgba(0,0,0,0.08);
      display: flex; align-items: center; padding: 0 20px; gap: 0;
      z-index: 200;
    }
    html:not(.light) .topbar,
    [data-theme="dark"] .topbar {
      background: rgba(9,13,24,.9);
      border-bottom-color: rgba(255,255,255,0.055);
    }

    .topbar .logo {
      display: flex; align-items: center; gap: 9px;
      text-decoration: none; flex-shrink: 0;
    }
    .topbar .logo-mark {
      width: 30px; height: 30px; border-radius: 8px;
      background: linear-gradient(135deg, #C99A2E 0%, #8A6515 100%);
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 2px 8px rgba(201,154,46,.3);
    }
    .topbar .logo-mark svg { width: 15px; height: 15px; fill: #000; }
    .topbar .logo-name {
      font-size: 14px; font-weight: 700; color: #1A2333;
      letter-spacing: -.02em;
    }
    html:not(.light) .topbar .logo-name,
    [data-theme="dark"] .topbar .logo-name { color: #DDE4EF; }

    .topbar .logo-badge {
      font-size: 10px; font-weight: 600; letter-spacing: .1em;
      color: #C99A2E; opacity: .75; text-transform: uppercase;
    }

    .topbar .tb-sep { width: 1px; height: 18px; background: rgba(0,0,0,0.08); margin: 0 16px; }
    html:not(.light) .topbar .tb-sep,
    [data-theme="dark"] .topbar .tb-sep { background: rgba(255,255,255,0.055); }

    .topbar .tb-conn {
      display: flex; align-items: center; gap: 6px;
      font-size: 12px; color: #4A5B72;
    }
    html:not(.light) .topbar .tb-conn,
    [data-theme="dark"] .topbar .tb-conn { color: #7A8FA8; }

    .topbar .conn-dot {
      width: 6px; height: 6px; border-radius: 50%;
      background: #34D399;
      box-shadow: 0 0 5px #34D399;
      transition: all .3s;
    }
    .topbar .conn-dot.off { background: #F87171; box-shadow: 0 0 5px #F87171; }

    .topbar .tb-right {
      margin-left: auto;
      display: flex; align-items: center; gap: 12px;
    }
    .topbar .tb-link {
      display: flex; align-items: center; gap: 5px;
      padding: 4px 10px; border-radius: 4px;
      font-size: 12px; font-weight: 600; color: #4A5B72;
      text-decoration: none; border: 1px solid rgba(0,0,0,0.08);
      transition: all .2s;
    }
    .topbar .tb-link:hover {
      color: #1A2333; background: #E8ECF5; border-color: rgba(201,154,46,0.38);
    }
    html:not(.light) .topbar .tb-link,
    [data-theme="dark"] .topbar .tb-link {
      color: #7A8FA8; border-color: rgba(255,255,255,0.055);
    }
    html:not(.light) .topbar .tb-link:hover,
    [data-theme="dark"] .topbar .tb-link:hover {
      color: #DDE4EF; background: #162030; border-color: rgba(201,154,46,0.38);
    }

    .topbar .tb-time {
      font-size: 11px; color: #8A97AA; font-family: 'JetBrains Mono', monospace;
      display: flex; align-items: center; gap: 5px;
    }
    html:not(.light) .topbar .tb-time,
    [data-theme="dark"] .topbar .tb-time { color: #374B62; }
    .topbar .tb-time svg { opacity: .45; }

    .topbar .tb-icon-btn {
      width: 30px; height: 30px; border-radius: 8px;
      background: transparent; border: 1px solid rgba(0,0,0,0.08);
      display: flex; align-items: center; justify-content: center;
      color: #4A5B72; cursor: pointer;
      transition: all .2s;
      padding: 0;
    }
    .topbar .tb-icon-btn:hover { color: #C99A2E; background: #E8ECF5; border-color: #C99A2E; }
    html:not(.light) .topbar .tb-icon-btn,
    [data-theme="dark"] .topbar .tb-icon-btn {
      color: #7A8FA8; border-color: rgba(255,255,255,0.055);
    }
    html:not(.light) .topbar .tb-icon-btn:hover,
    [data-theme="dark"] .topbar .tb-icon-btn:hover {
      color: #C99A2E; background: #162030; border-color: #C99A2E;
    }

    .topbar .avatar-btn {
      width: 30px; height: 30px; border-radius: 50%;
      background: rgba(201,154,46,0.07); border: 1px solid rgba(201,154,46,0.28);
      display: flex; align-items: center; justify-content: center;
      font-size: 12px; font-weight: 700; color: #E0B84A;
      cursor: pointer;
    }
  `;
  document.head.appendChild(style);

  // ─── INSERT HTML ───
  const linkLabel = isChatPage ? '📊 面板' : '💬 聊天';
  const linkHref  = isChatPage ? '/' : '/chat';
  const linkTitle = isChatPage ? '切换到数据面板' : '切换到聊天模式';

  const header = document.createElement('header');
  header.className = 'topbar';
  header.innerHTML = `
    <a href="/" class="logo">
      <div class="logo-mark">
        <svg viewBox="0 0 16 16">
          <path d="M1 1h6v6H1zM9 1h6v6H9zM1 9h6v6H1zM12 9v6M9 12h6"/>
        </svg>
      </div>
      <span class="logo-name">商品数据助手</span>
      <span class="logo-badge">&nbsp;Xsy</span>
    </a>
    <div class="tb-sep"></div>
    <div class="tb-conn">
      <div class="conn-dot" id="connDot"></div>
      <span id="connText">连接中…</span>
    </div>
    <div class="tb-right">
      <div class="tb-time">
        <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
        </svg>
        <span id="syncTime">--:--</span>
      </div>
      <a href="${linkHref}" class="tb-link" title="${linkTitle}">${linkLabel}</a>
      <button class="tb-icon-btn" id="themeBtn" title="切换主题">
        <svg id="themeIcon" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
        </svg>
      </button>
      <div class="avatar-btn">A</div>
    </div>
  `;
  document.body.insertBefore(header, document.body.firstChild);

  // ─── THEME ICON ───
  function setThemeIcon(isDark) {
    const icon = document.getElementById('themeIcon');
    if (!icon) return;
    if (isDark) {
      icon.innerHTML = '<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>';
    } else {
      icon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
    }
  }

  // ─── CONNECTION ───
  async function checkConn() {
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 3000);
      await fetch('/docs', { signal: ctrl.signal, mode: 'no-cors' });
      clearTimeout(t);
      document.getElementById('connDot').classList.remove('off');
      document.getElementById('connText').textContent = '服务已连接';
    } catch {
      document.getElementById('connDot').classList.add('off');
      document.getElementById('connText').textContent = '服务未启动';
    }
  }

  // ─── TIME ───
  function updateTime() {
    const el = document.getElementById('syncTime');
    if (el) el.textContent = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }

  // ─── THEME BUTTON ───
  document.getElementById('themeBtn').addEventListener('click', () => {
    document.dispatchEvent(new CustomEvent('topbar-theme-toggle'));
  });

  // ─── INIT ───
  updateTime();
  setInterval(updateTime, 60000);
  checkConn();

  // ─── EXPOSE API ───
  window.Topbar = { setThemeIcon, checkConn, updateTime };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTopbar);
  } else {
    initTopbar();
  }
})();
