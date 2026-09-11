(() => {
  'use strict';

  const config = window.SPL_SITE_CONFIG;
  const fallbackMarkup = `
    <a href="/" class="spl-component-fallback">Sahabat Pangan Lokal</a>
  `;

  const resolveSectionHref = (hash, isHome) => (
    isHome ? hash : `/${hash}`
  );

  class SplNavbar extends HTMLElement {
    connectedCallback() {
      if (!config) {
        this.innerHTML = fallbackMarkup;
        return;
      }

      const page = this.dataset.page || '';
      const isHome = page === 'home';

      const sectionLinks = config.sections.map((item, index) => {
        const href = resolveSectionHref(item.hash, isHome);
        const active = isHome && index === 0;
        const sectionData = isHome ? ' data-section-link' : '';
        const activeClass = active ? ' active' : '';
        const current = active ? ' aria-current="page"' : '';
        const downloadClass = item.key === 'download'
          ? ' nav-section-pill--download'
          : '';

        return `
          <li class="nav-item">
            <a
              class="nav-link nav-section-pill${downloadClass}${activeClass}"
              ${sectionData}
              href="${href}"
              ${current}
            >${item.label}</a>
          </li>
        `;
      }).join('');

      const pageLinks = config.pages.map((item, index) => {
        const active = page === item.key;
        const activeClass = active ? ' active' : '';
        const current = active ? ' aria-current="page"' : '';
        const separatorClass = index === 0
          ? ' nav-page-separator ms-lg-1'
          : '';

        return `
          <li class="nav-item${separatorClass}">
            <a
              class="nav-link nav-page-link${activeClass}"
              href="${item.href}"
              ${current}
            >${item.label}</a>
          </li>
        `;
      }).join('');

      const brandHref = isHome ? '#hero' : '/';
      const brandLabel = isHome
        ? 'Sahabat Pangan Lokal, kembali ke bagian beranda'
        : 'Sahabat Pangan Lokal, kembali ke beranda';

      this.innerHTML = `
        <nav
          class="navbar navbar-expand-lg fixed-top spl-navbar"
          data-spl-navbar
          aria-label="Navigasi utama"
        >
          <div class="container">
            <a
              class="navbar-brand d-flex align-items-center gap-2"
              href="${brandHref}"
              aria-label="${brandLabel}"
            >
              <span class="brand-badge" aria-hidden="true">SPL</span>
              <span class="brand-name">${config.brand.name}</span>
            </a>

            <button
              class="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#splNav"
              aria-controls="splNav"
              aria-expanded="false"
              aria-label="Buka navigasi"
            >
              <span class="navbar-toggler-icon"></span>
            </button>

            <div
              class="collapse navbar-collapse justify-content-end"
              id="splNav"
            >
              <ul
                class="navbar-nav align-items-lg-center gap-lg-1 spl-section-nav"
                id="splSectionNav"
              >
                ${sectionLinks}
                ${pageLinks}
              </ul>
            </div>
          </div>
        </nav>
      `;
    }
  }

  class SplFooter extends HTMLElement {
    connectedCallback() {
      if (!config) {
        this.innerHTML = fallbackMarkup;
        return;
      }

      const page = this.dataset.page || '';
      const isHome = page === 'home';

      const sectionLinks = config.sections.map((item) => `
        <a href="${resolveSectionHref(item.hash, isHome)}">${item.label}</a>
      `).join('');

      const pageLinks = config.pages.map((item) => `
        <a href="${item.href}">${item.label}</a>
      `).join('');

      const privacyCurrent = page === 'privasi'
        ? ' aria-current="page"'
        : '';

      this.innerHTML = `
        <footer class="site-footer">
          <div class="footer-landscape" aria-hidden="true">
            <img src="/assets/backgrounds/bg-main-menu.png" alt="">
          </div>

          <div class="container">
            <div class="row align-items-start gy-3">
              <div class="col-lg-4">
                <div class="footer-title">
                  Sahabat <span>Pangan Lokal</span>
                </div>
                <div class="footer-copy">
                  ${config.footer.tagline}
                </div>
              </div>

              <div class="col-lg-5">
                <nav
                  class="footer-nav footer-nav-main"
                  aria-label="Navigasi footer utama"
                >
                  ${sectionLinks}
                  ${pageLinks}
                </nav>

                <div class="footer-utility">
                  <span>Informasi</span>
                  <a
                    href="${config.legal.privacy.href}"
                    ${privacyCurrent}
                  >${config.legal.privacy.label}</a>
                </div>
              </div>

              <div class="col-lg-3 text-lg-end footer-meta">
                <div>${config.footer.institution}</div>
                <div>${config.footer.copyright}</div>
              </div>
            </div>
          </div>
        </footer>
      `;
    }
  }

  if (!customElements.get('spl-navbar')) {
    customElements.define('spl-navbar', SplNavbar);
  }

  if (!customElements.get('spl-footer')) {
    customElements.define('spl-footer', SplFooter);
  }
})();
