from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = ['index.html', 'tentang/index.html', 'status/index.html', 'privasi/index.html']

class SiteContractTests(unittest.TestCase):
    def read(self, rel):
        return (ROOT / rel).read_text(encoding='utf-8')

    def combined(self, rels=PUBLIC_PAGES):
        return '\n'.join(self.read(rel) for rel in rels)

    def test_homepage_has_exactly_five_primary_sections(self):
        html = self.read('index.html')
        ids = re.findall(r'<(?:section|footer|spl-footer)\b[^>]*data-primary-section[^>]*id="([^"]+)"', html)
        self.assertEqual(ids, ['hero', 'tentang-singkat', 'pangan', 'ketersediaan', 'footer'])

    def test_all_public_pages_use_bootstrap_538(self):
        css_asset = ROOT / 'assets/vendor/bootstrap-5.3.8.min.css'
        js_asset = ROOT / 'assets/vendor/bootstrap-5.3.8.bundle.min.js'
        self.assertTrue(css_asset.is_file())
        self.assertTrue(js_asset.is_file())
        for rel in PUBLIC_PAGES:
            html = self.read(rel)
            self.assertIn('/assets/vendor/bootstrap-5.3.8.min.css', html, rel)
            self.assertIn('/assets/vendor/bootstrap-5.3.8.bundle.min.js', html, rel)
            self.assertNotIn('cdn.jsdelivr.net/npm/bootstrap@5.3.8', html, rel)
            self.assertRegex(html, r'class="[^"]*\bcontainer\b', rel)
            self.assertIn('navbar', html, rel)

    def test_animation_stack_is_gsap_scrolltrigger_everywhere(self):
        gsap_asset = ROOT / 'assets/vendor/gsap-3.15.0.min.js'
        trigger_asset = ROOT / 'assets/vendor/ScrollTrigger-3.15.0.min.js'
        self.assertTrue(gsap_asset.is_file())
        self.assertTrue(trigger_asset.is_file())
        for rel in PUBLIC_PAGES:
            html = self.read(rel)
            self.assertIn('/assets/vendor/gsap-3.15.0.min.js', html, rel)
            self.assertIn('/assets/vendor/ScrollTrigger-3.15.0.min.js', html, rel)
            self.assertNotIn('cdn.jsdelivr.net/npm/gsap@3.15.0', html, rel)
            self.assertIn('/assets/js/site.js', html, rel)
        js = self.read('assets/js/site.js')
        self.assertIn('gsap.registerPlugin(ScrollTrigger)', js)
        self.assertIn('ScrollTrigger.create', js)
        self.assertIn('gsap.matchMedia()', js)

    def test_homepage_uses_swiper_1420(self):
        css_asset = ROOT / 'assets/vendor/swiper-14.2.0.min.css'
        js_asset = ROOT / 'assets/vendor/swiper-14.2.0.min.js'
        self.assertTrue(css_asset.is_file())
        self.assertTrue(js_asset.is_file())
        html = self.read('index.html')
        self.assertIn('/assets/vendor/swiper-14.2.0.min.css', html)
        self.assertIn('/assets/vendor/swiper-14.2.0.min.js', html)
        self.assertNotIn('cdn.jsdelivr.net/npm/swiper@14.2.0', html)
        self.assertIn('class="swiper spl-food-swiper"', html)
        js = self.read('assets/js/site.js')
        self.assertIn('new Swiper', js)
        self.assertIn('keyboard:', js)
        self.assertIn('breakpoints:', js)

    def test_public_pages_remove_known_browser_console_noise_sources(self):
        public = self.combined()
        self.assertNotIn('cdn.jsdelivr.net/npm/', public)
        self.assertNotIn('loading="lazy"', public)

        js = self.read('assets/js/site.js')
        stale_targets = [
            '.platform-card.google',
            '.platform-card.windows',
            '.availability-hill.first',
            '.availability-hill.second',
        ]
        for target in stale_targets:
            self.assertNotIn(target, js, target)

    def test_hero_characters_are_height_driven_and_prominent(self):
        css = self.read('assets/css/site.css')
        self.assertIn('.hero-character', css)
        self.assertRegex(css, r'height:\s*clamp\([^;]+\)')
        self.assertIn('.hero-character--2', css)
        self.assertIn('.hero-character--4', css)
        self.assertIn('min-height: 720px', css)

    def test_about_section_uses_five_provided_place_objects(self):
        html = self.read('index.html')
        self.assertIn('class="journey-board"', html)
        self.assertEqual(html.count('data-journey-node'), 5)
        self.assertNotIn('class="journey-map"', html)
        self.assertNotIn('data-journey-stop', html)
        for place in ['Rumah', 'Sekolah', 'Pasar', 'Dapur', 'Festival']:
            self.assertIn(place, html)
        for asset in [
            '/assets/journey-places/01-rumah.png',
            '/assets/journey-places/02-sekolah.png',
            '/assets/journey-places/03-pasar.png',
            '/assets/journey-places/04-dapur.png',
            '/assets/journey-places/05-festival.png'
        ]:
            self.assertIn(asset, html)

        js = self.read('assets/js/site.js')
        self.assertIn('[data-journey-node]', js)
        self.assertIn('.journey-node-figure', js)
        self.assertNotIn('.journey-route-path', js)

    def test_food_carousel_contains_fourteen_production_foods(self):
        html = self.read('index.html')
        foods = ['Beras', 'Singkong', 'Ubi Jalar', 'Jagung', 'Kangkung', 'Bayam', 'Timun', 'Terong', 'Pisang', 'Pepaya', 'Mangga', 'Jambu Biji', 'Ikan Lele', 'Ikan Nila']
        for food in foods:
            self.assertIn(food, html)
        self.assertEqual(html.count('data-food-card'), 14)

    def test_food_cards_support_focus_and_detail_modal(self):
        html = self.read('index.html')
        self.assertEqual(html.count('role="button" tabindex="0" aria-pressed="false"'), 14)
        self.assertEqual(html.count('data-food-detail'), 14)
        self.assertIn('id="foodDetailModal"', html)
        self.assertIn('data-food-modal-image', html)
        self.assertIn('data-food-modal-title', html)
        self.assertIn('data-food-modal-description', html)

        css = self.read('assets/css/site.css')
        self.assertIn('.swiper-slide.is-selected .food-card', css)
        self.assertIn('.food-detail-trigger', css)
        self.assertIn('.food-detail-modal-content', css)

        js = self.read('assets/js/site.js')
        self.assertIn('setSelectedFood', js)
        self.assertIn('openFoodDetail', js)
        self.assertIn('bootstrap.Modal.getOrCreateInstance', js)

    def test_food_section_compact_single_focus_visual_contract(self):
        html = self.read('index.html')
        self.assertIn('Kenali pangan lokal dalam petualanganmu.', html)
        self.assertEqual(html.count('class="foods-nav-icon"'), 2)

        css = self.read('assets/css/site.css')
        self.assertIn('/* SPL 07F COMPACT SINGLE FOCUS START */', css)
        self.assertIn('height: calc(100svh - var(--spl-header));', css)
        self.assertIn('.foods-section .foods-nav-wrap .spl-food-prev,', css)
        self.assertIn('.spl-food-swiper.has-selection .swiper-slide:not(.is-selected) .food-card', css)
        self.assertIn('.spl-food-swiper .swiper-slide.swiper-slide-active:not(.is-selected) .food-card', css)

    def test_food_title_is_horizontal_and_card_images_are_fully_contained(self):
        css = self.read('assets/css/site.css')
        self.assertIn('/* SPL 07G HORIZONTAL TITLE FULL IMAGE START */', css)
        self.assertIn('white-space: nowrap;', css)
        self.assertIn('max-width: none;', css)
        self.assertIn('object-fit: contain;', css)
        self.assertIn('max-width: 92%;', css)
        self.assertIn('max-height: 92%;', css)
        self.assertIn('.spl-food-swiper.has-selection .swiper-slide.is-selected .food-visual img', css)

    def test_food_card_images_use_hard_contain_box(self):
        css = self.read('assets/css/site.css')
        self.assertIn('/* SPL 07H FOOD IMAGE TRUE CONTAIN START */', css)
        self.assertIn('width: 100%;', css)
        self.assertIn('height: 100%;', css)
        self.assertIn('max-width: 100%;', css)
        self.assertIn('max-height: 100%;', css)
        self.assertIn('object-fit: contain;', css)
        self.assertIn('object-position: center center;', css)
        self.assertIn('transform: none;', css)

    def test_download_preflight_modal_and_real_counter_contract(self):
        html = self.read('index.html')
        css = self.read('assets/css/site.css')
        js = self.read('assets/js/site.js')
        privacy = self.read('privasi/index.html')
        sql_path = ROOT / 'server/site_api/sql/001_init.sql'
        self.assertTrue(
            sql_path.exists(),
            'site API SQL schema must exist after implementation'
        )
        sql = sql_path.read_text(encoding='utf-8')

        self.assertIn('class="availability-section download-cta-section"', html)
        self.assertEqual(html.count('data-download-counter='), 3)
        self.assertIn('data-download-counter="android"', html)
        self.assertIn('data-download-counter="windows"', html)
        self.assertIn('data-download-counter="total"', html)
        self.assertNotIn('data-download-target=', html)
        self.assertNotIn('href="/downloads/sahabat-pangan-lokal-android.apk" download', html)
        self.assertNotIn('href="/downloads/Sahabat-Pangan-Lokal-Windows.zip" download', html)
        self.assertIn('data-download-platform="android"', html)
        self.assertIn('data-download-platform="windows"', html)

        self.assertIn('id="downloadPreflightModal"', html)
        self.assertIn('role="dialog"', html)
        self.assertIn('aria-modal="true"', html)
        self.assertIn('data-preflight-status-list', html)
        self.assertIn('data-preflight-final-download', html)
        self.assertIn('aria-live="polite"', html)

        self.assertIn('/* SPL 08D DOWNLOAD PREFLIGHT MODAL START */', css)
        self.assertIn('.download-preflight-backdrop', css)
        self.assertIn('.download-preflight-dialog', css)
        self.assertIn('backdrop-filter: blur(', css)

        self.assertIn('/api/site/v1/download-stats', js)
        self.assertIn('/api/site/v1/download-preflight', js)
        self.assertIn('/api/site/v1/download-start', js)
        self.assertIn('runLatencyProbe', js)
        self.assertIn('runRangeSpeedProbe', js)
        self.assertIn('classifyNetwork', js)
        self.assertIn('localPreview', js)
        self.assertIn('location.hostname.endsWith(\'.test\')', js)

        self.assertIn('lokasi perkiraan', privacy.lower())
        self.assertIn('ip mentah', privacy.lower())
        self.assertIn('gps', privacy.lower())
        self.assertIn('waktu server', privacy.lower())

        self.assertIn('CREATE TABLE IF NOT EXISTS site.release_metadata', sql)
        self.assertIn('CREATE TABLE IF NOT EXISTS site.download_events', sql)
        self.assertNotIn('raw_ip', sql.lower())
        self.assertNotIn('latitude', sql.lower())
        self.assertNotIn('longitude', sql.lower())
    def test_download_preflight_modal_is_xl_structured_and_outside_inert_main(self):
        html = self.read('index.html')
        css = self.read('assets/css/site.css')
        js = self.read('assets/js/site.js')

        main_end = html.index('</main>')
        modal_index = html.index('id="downloadPreflightModal"')
        footer_index = html.index('<spl-footer', main_end)

        self.assertGreater(modal_index, main_end)
        self.assertLess(modal_index, footer_index)

        self.assertIn('class="download-preflight-header"', html)
        self.assertIn('class="download-preflight-body"', html)
        self.assertIn('class="download-preflight-footer"', html)
        self.assertIn('class="download-preflight-body-grid"', html)

        self.assertIn('width: min(96vw, 1140px);', css)
        self.assertIn('grid-template-rows: auto minmax(0, 1fr) auto;', css)
        self.assertIn('.download-preflight-body {', css)
        self.assertIn('overflow-y: auto;', css)
        self.assertIn('overscroll-behavior: contain;', css)
        self.assertIn('.download-preflight-footer {', css)

        self.assertIn("const main = document.getElementById('main-content');", js)
        self.assertIn('node.inert = true;', js)
    def test_download_cta_is_compact_and_android_only_on_mobile_tablet(self):
        html = self.read('index.html')
        self.assertIn('Petualanganmu siap dimainkan.', html)

        css = self.read('assets/css/site.css')
        self.assertIn('/* SPL 08C COMPACT DOWNLOAD MOBILE START */', css)
        self.assertIn('@media (min-width: 1200px)', css)
        self.assertIn('height: calc(100svh - var(--spl-header));', css)
        self.assertIn('@media (max-width: 1199.98px)', css)
        self.assertIn('.download-platform-card--windows {', css)
        self.assertIn('display: none;', css)
        self.assertIn('.download-platform-grid {', css)
        self.assertIn('grid-template-columns: minmax(0, 1fr);', css)

    def test_homepage_nav_footer_scrollspy_and_favicon_are_synchronized(self):
        html = self.read('index.html')
        self.assertIn(
            'rel="icon" type="image/webp" href="/assets/brand/logo_game.webp"',
            html
        )
        self.assertIn(
            'rel="apple-touch-icon" href="/assets/brand/logo_game.png"',
            html
        )
        self.assertIn('<spl-navbar data-page="home"></spl-navbar>', html)
        self.assertIn(
            '<spl-footer data-page="home" data-primary-section id="footer"></spl-footer>',
            html
        )

        config = self.read('assets/js/site-config.js')
        components = self.read('assets/js/site-components.js')
        for label in ['Beranda', 'Petualangan', 'Pangan', 'Unduh', 'Tentang', 'Kabar']:
            self.assertIn(label, config)
        self.assertIn('data-section-link', components)
        self.assertIn('footer-nav footer-nav-main', components)
        self.assertIn('/privasi/', config)

        css = self.read('assets/css/site.css')
        self.assertIn('/* SPL 09 NAV FOOTER SCROLLSPY START */', css)
        self.assertIn('.nav-section-pill.active', css)
        self.assertIn(
            'scroll-margin-top: calc(var(--spl-header) + 12px);',
            css
        )
        self.assertIn('.footer-utility', css)

        js = self.read('assets/js/site.js')
        self.assertIn('data-section-link', js)
        self.assertIn('updateSectionNavActiveState', js)
        self.assertIn('requestAnimationFrame', js)
        self.assertIn('bootstrap.Collapse.getOrCreateInstance', js)
    def test_food_counter_reports_visible_card_range(self):
        js = self.read('assets/js/site.js')
        self.assertIn('function getVisibleFoodSlideIndexes', js)
        self.assertIn('visibilityRatio >= 0.5', js)
        self.assertIn('const firstVisible = visibleIndexes[0] + 1;', js)
        self.assertIn('const lastVisible = visibleIndexes[visibleIndexes.length - 1] + 1;', js)
        self.assertIn('`${padFoodNumber(firstVisible)}–${padFoodNumber(lastVisible)}`', js)
        self.assertIn('slideChangeTransitionEnd(instance)', js)
        self.assertIn('resize(instance)', js)
        self.assertIn('breakpoint(instance)', js)
        self.assertNotIn('current.textContent = padFoodNumber(swiper.realIndex + 1);', js)

    def test_footer_is_compact(self):
        css = self.read('assets/css/site.css')
        block = re.search(r'\.site-footer\s*\{([^}]*)\}', css, re.S)
        self.assertIsNotNone(block)
        body = block.group(1)
        self.assertNotIn('min-height: 430px', body)
        self.assertRegex(body, r'padding:\s*(?:[12]\d|[1-6]rem|\d+px)')
        self.assertIn('.footer-landscape', css)

    def test_internal_pages_have_motion_hooks_and_friendly_copy(self):
        for rel in ['tentang/index.html', 'status/index.html', 'privasi/index.html']:
            html = self.read(rel)
            self.assertIn('data-page-hero', html, rel)
            self.assertIn('data-reveal', html, rel)
        public = self.combined().lower()
        banned = [
            'kegiatan penelitian', 'algoritma', 'build pengembangan',
            'persiapan distribusi', 'dalam pengujian', '2d berbasis skenario',
            'versi publik', 'telemetry', 'backend'
        ]
        for term in banned:
            self.assertNotIn(term, public, term)

    def test_accessibility_and_reduced_motion_contract(self):
        html = self.read('index.html')
        self.assertIn('href="#main-content"', html)
        self.assertIn('aria-label="Pangan lokal"', html)
        css = self.read('assets/css/site.css')
        self.assertIn(':focus-visible', css)
        self.assertIn('@media (prefers-reduced-motion: reduce)', css)
        js = self.read('assets/js/site.js')
        self.assertIn('(prefers-reduced-motion: reduce)', js)

    def test_required_internal_pages_and_legacy_redirects_exist(self):
        for rel in ['tentang/index.html', 'status/index.html', 'privasi/index.html']:
            self.assertTrue((ROOT / rel).is_file(), rel)
        for rel, target in [('privacy.html', '/privasi/'), ('status.html', '/status/')]:
            html = self.read(rel)
            self.assertIn(target, html)
            self.assertIn('http-equiv="refresh"', html)

    def test_active_runtime_assets_are_present_and_legacy_assets_are_absent(self):
        required = [
            'assets/backgrounds/bg-main-menu.png',
            'assets/brand/logo_game.png',
            'assets/brand/logo_game.webp',
            'assets/characters/hero/character-01-happy.png',
            'assets/characters/hero/character-02-happy.png',
            'assets/characters/hero/character-03-happy.png',
            'assets/characters/hero/character-04-happy.png',
            'assets/journey-places/01-rumah.png',
            'assets/journey-places/02-sekolah.png',
            'assets/journey-places/03-pasar.png',
            'assets/journey-places/04-dapur.png',
            'assets/journey-places/05-festival.png',
        ]
        required.extend([
            f'assets/foods/{name}' for name in [
                'food_rice.png', 'food_cassava.png', 'food_sweet_potato.png',
                'food_corn.png', 'food_water_spinach.png', 'food_spinach.png',
                'food_cucumber.png', 'food_eggplant.png', 'food_banana.png',
                'food_papaya.png', 'food_mango.png', 'food_guava.png',
                'food_catfish.png', 'food_tilapia.png',
            ]
        ])
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

        legacy = [
            'assets/environment',
            'assets/foreground',
            'assets/production',
            'assets/social',
            'assets/asset-manifest.json',
            'assets/site.css',
            'scripts/prepare-assets.ps1',
            'favicon.png',
            'icon-512.png',
            'site.webmanifest',
        ]
        for rel in legacy:
            self.assertFalse((ROOT / rel).exists(), rel)

        qa_root = ROOT / 'qa'
        self.assertTrue(qa_root.is_dir(), 'qa')
        qa_files = sorted(
            path.relative_to(ROOT).as_posix()
            for path in qa_root.rglob('*')
            if path.is_file()
        )
        self.assertEqual(
            qa_files,
            ['qa/update-system-verification.txt'],
        )

        character_root = ROOT / 'assets/characters'
        self.assertEqual(
            sorted(path.name for path in character_root.iterdir()),
            ['hero']
        )

    def test_404_uses_active_css_and_brand_favicon(self):
        html = self.read('404.html')
        self.assertIn('/assets/css/site.css', html)
        self.assertIn('/assets/brand/logo_game.webp', html)
        self.assertNotIn('/assets/site.css', html)
        self.assertNotIn('/favicon.png', html)
    def test_caddy_example_keeps_legacy_redirects(self):
        caddy = self.read('Caddyfile.example')
        self.assertIn('redir /privacy.html /privasi/ 301', caddy)
        self.assertIn('redir /status.html /status/ 301', caddy)


    def test_public_pages_use_shared_navbar_and_footer_components(self):
        for rel in PUBLIC_PAGES:
            html = self.read(rel)
            self.assertIn('<spl-navbar', html, rel)
            self.assertIn('<spl-footer', html, rel)
            self.assertNotRegex(
                html,
                r'<nav\b[^>]*class="navbar navbar-expand-lg fixed-top spl-navbar"',
                rel
            )
            self.assertNotRegex(
                html,
                r'<footer\b[^>]*class="site-footer"',
                rel
            )
            self.assertIn('/assets/js/site-config.js', html, rel)
            self.assertIn('/assets/js/site-components.js', html, rel)

            config_pos = html.index('/assets/js/site-config.js')
            components_pos = html.index('/assets/js/site-components.js')
            site_pos = html.index('/assets/js/site.js')
            self.assertLess(config_pos, components_pos, rel)
            self.assertLess(components_pos, site_pos, rel)

    def test_site_config_contains_canonical_navigation(self):
        config = self.read('assets/js/site-config.js')
        for token in [
            '#hero',
            '#tentang-singkat',
            '#pangan',
            '#ketersediaan',
            '/tentang/',
            '/status/',
            '/privasi/',
        ]:
            self.assertIn(token, config)

    def test_site_components_define_light_dom_navbar_and_footer(self):
        js = self.read('assets/js/site-components.js')
        self.assertIn("customElements.define('spl-navbar'", js)
        self.assertIn("customElements.define('spl-footer'", js)
        self.assertIn('this.innerHTML =', js)
        self.assertNotIn('attachShadow', js)
        self.assertIn('data-section-link', js)
        self.assertIn('footer-nav footer-nav-main', js)

    def test_hero_motion_uses_isolated_transform_layers(self):
        html = self.read('index.html')
        self.assertEqual(html.count('class="hero-character-parallax"'), 4)

        js = self.read('assets/js/site.js')
        self.assertIn(".fromTo('.hero-character'", js)
        self.assertIn(
            "document.querySelectorAll('.hero-character-parallax')",
            js
        )
        self.assertIn(
            "gsap.fromTo('.hero-character-parallax'",
            js
        )
        self.assertIn(
            "hero.querySelectorAll('.hero-character-parallax')",
            js
        )
        self.assertNotIn(
            "gsap.to('.hero-character',",
            js
        )

    def test_journey_keeps_line_but_removes_inline_card_arrows(self):
        css = self.read('assets/css/site.css')
        self.assertIn('.journey-flow::before', css)
        self.assertNotRegex(
            css,
            r'\.journey-node(?::last-child)?::after\s*\{[^}]*\}'
        )
        self.assertNotIn(
            '.journey-node:nth-child(3)::after',
            css
        )
        self.assertNotIn(
            '.journey-node:nth-child(4)::before',
            css
        )

        html = self.read('index.html')
        self.assertIn('class="journey-order-pill"', html)
        self.assertIn('<i>→</i>', html)

    def test_internal_pages_share_favicon_and_current_availability_state(self):
        for rel in ['tentang/index.html', 'status/index.html', 'privasi/index.html']:
            html = self.read(rel)
            self.assertIn(
                'rel="icon" type="image/webp" href="/assets/brand/logo_game.webp"',
                html,
                rel
            )
            self.assertIn(
                'rel="apple-touch-icon" href="/assets/brand/logo_game.png"',
                html,
                rel
            )

        status = self.read('status/index.html')
        self.assertNotIn('Segera Hadir', status)
        self.assertNotIn('belum dapat diunduh', status)
        self.assertIn('Petualangannya sudah tersedia.', status)
        self.assertIn('/#ketersediaan', status)


    def test_skip_link_only_reveals_for_explicit_keyboard_navigation(self):
        html = self.read('index.html')
        self.assertIn(
            '<a class="skip-link" href="#main-content">Lewati ke konten utama</a>',
            html
        )

        css = self.read('assets/css/site.css')
        self.assertIn('.keyboard-nav .skip-link:focus-visible', css)
        self.assertIn('opacity: 0;', css)
        self.assertIn('pointer-events: none;', css)
        self.assertNotRegex(css, r'\.skip-link:focus\s*\{')

        js = self.read('assets/js/site.js')
        self.assertIn("event.key === 'Tab'", js)
        self.assertIn("html.classList.add('keyboard-nav')", js)
        self.assertIn("html.classList.remove('keyboard-nav')", js)
        self.assertIn("'pointerdown'", js)


    def test_homepage_hero_gsap_is_guarded_on_pages_without_home_hero(self):
        js = self.read('assets/js/site.js')
        block = re.search(
            r"const homeHero = document\.querySelector\('#hero'\);\s*"
            r"if \(homeHero\) \{(?P<body>.*?)"
            r"\n    \}\s*\n\s*const journeyNodes =",
            js,
            re.S
        )
        self.assertIsNotNone(block)
        body = block.group('body')
        homepage_only_tokens = [
            'const heroTimeline = gsap.timeline',
            '[data-hero-enter="logo"]',
            '[data-hero-enter="eyebrow"]',
            '[data-hero-enter="title"]',
            '[data-hero-enter="lead"]',
            '[data-hero-enter="actions"]',
            "'.hero-character'",
            "'.hero-bg-img'",
            "'.hero-copy-card'",
            "'.hero-character-parallax'",
        ]
        for token in homepage_only_tokens:
            self.assertIn(token, body, token)

if __name__ == '__main__':
    unittest.main(verbosity=2)
