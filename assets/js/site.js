(() => {
  'use strict';

  const html = document.documentElement;
  const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const navbar = document.querySelector('[data-spl-navbar]');
  const gsapReady = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
  const swiperReady = typeof window.Swiper !== 'undefined';

  html.classList.add('js-motion');

  const enableKeyboardNavigation = (event) => {
    if (event.key === 'Tab') {
      html.classList.add('keyboard-nav');
    }
  };

  const disableKeyboardNavigation = () => {
    html.classList.remove('keyboard-nav');
  };

  window.addEventListener('keydown', enableKeyboardNavigation, true);
  window.addEventListener(
    'pointerdown',
    disableKeyboardNavigation,
    { passive: true }
  );

  const updateNavbar = () => {
    if (!navbar) return;
    navbar.classList.toggle('is-scrolled', window.scrollY > 18 || document.body.classList.contains('internal-page'));
  };
  updateNavbar();
  window.addEventListener('scroll', updateNavbar, { passive: true });

  const showEverything = () => {
    document.querySelectorAll('[data-hero-enter], [data-reveal]').forEach((node) => {
      node.style.opacity = '1';
      node.style.transform = 'none';
    });
  };

  const initSwiper = () => {
    const carousel = document.querySelector('.spl-food-swiper');
    if (!carousel) return;

    if (swiperReady) {
      const swiper = new Swiper('.spl-food-swiper', {
        slidesPerView: 1.18,
        spaceBetween: 16,
        centeredSlides: true,
        grabCursor: true,
        speed: 620,
        keyboard: { enabled: true, onlyInViewport: true },
        navigation: {
          nextEl: '.spl-food-next',
          prevEl: '.spl-food-prev'
        },
        pagination: {
          el: '.spl-food-pagination',
          clickable: true
        },
        breakpoints: {
          576: { slidesPerView: 2.15, spaceBetween: 18 },
          768: { slidesPerView: 2.8, spaceBetween: 20 },
          992: { slidesPerView: 4.05, spaceBetween: 22, centeredSlides: false },
          1400: { slidesPerView: 4.4, spaceBetween: 24, centeredSlides: false }
        }
      });
      carousel.dataset.swiperReady = 'true';
      return swiper;
    }

    // Offline fallback: native horizontal scroll remains usable when Swiper CDN is unavailable.
    const wrapper = carousel.querySelector('.swiper-wrapper');
    if (wrapper) {
      wrapper.style.display = 'flex';
      wrapper.style.gap = '16px';
      wrapper.style.overflowX = 'auto';
      wrapper.style.scrollSnapType = 'x mandatory';
      wrapper.style.scrollBehavior = 'smooth';
      const slides = [...wrapper.querySelectorAll('.swiper-slide')];
      slides.forEach((slide, index) => {
        slide.style.minWidth = '260px';
        slide.style.scrollSnapAlign = 'center';
        slide.classList.toggle('swiper-slide-active', index === 0);
      });
      const step = () => (slides[0]?.getBoundingClientRect().width || 260) + 16;
      const activateNearest = () => {
        if (!slides.length) return;
        const center = wrapper.scrollLeft + wrapper.clientWidth / 2;
        let best = 0;
        let dist = Infinity;
        slides.forEach((slide, i) => {
          const d = Math.abs((slide.offsetLeft + slide.offsetWidth / 2) - center);
          if (d < dist) { dist = d; best = i; }
        });
        slides.forEach((slide, i) => slide.classList.toggle('swiper-slide-active', i === best));
      };
      carousel.querySelector('.spl-food-next')?.addEventListener('click', () => wrapper.scrollBy({ left: step(), behavior: 'smooth' }));
      carousel.querySelector('.spl-food-prev')?.addEventListener('click', () => wrapper.scrollBy({ left: -step(), behavior: 'smooth' }));
      wrapper.addEventListener('scroll', () => window.requestAnimationFrame(activateNearest), { passive: true });
    }
  };

  const initGsap = () => {
    if (!gsapReady || reduceMotionQuery.matches) {
      showEverything();
      return;
    }

    const { gsap, ScrollTrigger } = window;
    gsap.registerPlugin(ScrollTrigger);
    const mm = gsap.matchMedia();

    const homeHero = document.querySelector('#hero');
    if (homeHero) {
      const heroTimeline = gsap.timeline({ defaults: { ease: 'power3.out' } });
      heroTimeline
        .fromTo('[data-hero-enter="logo"]', { y: -36, scale: .82, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: .75 })
        .fromTo('[data-hero-enter="eyebrow"]', { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: .5 }, '-=.35')
        .fromTo('[data-hero-enter="title"]', { y: 48, opacity: 0 }, { y: 0, opacity: 1, duration: .8 }, '-=.25')
        .fromTo('[data-hero-enter="lead"]', { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .65 }, '-=.42')
        .fromTo('[data-hero-enter="actions"]', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: .55 }, '-=.38')
        .fromTo('.hero-character', { y: 120, opacity: 0, scale: .82 }, { y: 0, opacity: 1, scale: 1, duration: .95, stagger: .11, ease: 'back.out(1.35)' }, '-=.72');
      // Gentle idle motion lives on the inner images so it never competes with
      // the existing wrapper-based entrance and ScrollTrigger parallax.
      const heroIdleMotions = [
        { y: -4, rotation: -.22, duration: 3.4, delay: .10 },
        { y: -6, rotation:  .28, duration: 3.0, delay: .55 },
        { y: -3, rotation: -.30, duration: 3.7, delay: .25 },
        { y: -5, rotation:  .24, duration: 3.2, delay: .70 }
      ];
      document.querySelectorAll('.hero-character img').forEach((node, index) => {
        const motion = heroIdleMotions[index % heroIdleMotions.length];
        gsap.to(node, {
          y: motion.y,
          rotation: motion.rotation,
          duration: motion.duration,
          delay: 2.05 + motion.delay,
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut',
          transformOrigin: '50% 100%'
        });
      });

      mm.add('(min-width: 992px)', () => {
        gsap.to('.hero-bg-img', {
          yPercent: 8,
          scale: 1.13,
          ease: 'none',
          scrollTrigger: {
            trigger: '#hero',
            start: 'top top',
            end: 'bottom top',
            scrub: .65
          }
        });

        const motions = [
          { y: -76, x: -18, rotation: -2 },
          { y: -128, x: 18, rotation: 2.2 },
          { y: -94, x: -13, rotation: -1.4 },
          { y: -142, x: 22, rotation: 2.6 }
        ];
        document.querySelectorAll('.hero-character-parallax').forEach((node, index) => {
          gsap.fromTo(node, {
            x: 0,
            y: 0,
            rotation: 0
          }, {
            ...motions[index],
            ease: 'none',
            scrollTrigger: {
              trigger: '#hero',
              start: 'top top',
              end: 'bottom top',
              scrub: .55,
              invalidateOnRefresh: true
            }
          });
        });

        gsap.to('.hero-copy-card', {
          y: -82,
          opacity: .66,
          scale: .965,
          ease: 'none',
          scrollTrigger: {
            trigger: '#hero',
            start: '25% top',
            end: 'bottom top',
            scrub: .6
          }
        });
      });

      mm.add('(max-width: 991.98px)', () => {
        gsap.to('.hero-bg-img', {
          yPercent: 4,
          scale: 1.08,
          ease: 'none',
          scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: .75 }
        });
        gsap.fromTo('.hero-character-parallax', {
          y: 0
        }, {
          y: (i) => [-28, -52, -38, -58][i],
          ease: 'none',
          scrollTrigger: {
            trigger: '#hero',
            start: 'top top',
            end: 'bottom top',
            scrub: .75,
            invalidateOnRefresh: true
          }
        });
      });
    }
    const journeyNodes = gsap.utils.toArray('[data-journey-node]');
    if (journeyNodes.length) {
      gsap.fromTo(journeyNodes, {
        y: 34,
        opacity: 0,
        scale: .90
      }, {
        y: 0,
        opacity: 1,
        scale: 1,
        duration: .68,
        stagger: .10,
        ease: 'back.out(1.30)',
        scrollTrigger: {
          id: 'journey-node-sequence',
          trigger: '#tentang-singkat',
          start: 'top 74%',
          toggleActions: 'play none none none'
        }
      });

      gsap.fromTo('.journey-order-pill', {
        y: 20,
        opacity: 0
      }, {
        y: 0,
        opacity: 1,
        duration: .56,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '#tentang-singkat',
          start: 'top 68%',
          toggleActions: 'play none none none'
        }
      });

      gsap.to('.journey-node-figure', {
        y: (i) => [-7, -10, -8, -10, -7][i % 5],
        duration: (i) => [2.8, 3.1, 2.9, 3.2, 2.8][i % 5],
        ease: 'sine.inOut',
        repeat: -1,
        yoyo: true,
        stagger: .06
      });

      gsap.to('.journey-node-image', {
        rotate: (i) => [-2.5, 1.8, -1.8, 2.2, -1.6][i % 5],
        duration: (i) => [3.0, 3.4, 3.2, 3.5, 3.1][i % 5],
        ease: 'sine.inOut',
        repeat: -1,
        yoyo: true,
        stagger: .05
      });
    }

    gsap.utils.toArray('[data-reveal]').forEach((node) => {
      const direction = node.dataset.reveal || 'up';
      const from = { opacity: 0, y: 52 };
      if (direction === 'left') { from.x = -70; from.y = 0; }
      if (direction === 'right') { from.x = 70; from.y = 0; }
      if (direction === 'scale') { from.scale = .88; from.y = 18; }
      gsap.fromTo(node, from, {
        opacity: 1, x: 0, y: 0, scale: 1, duration: .85, ease: 'power3.out',
        scrollTrigger: { trigger: node, start: 'top 86%', toggleActions: 'play none none none' }
      });
    });

    const foodSection = document.querySelector('#pangan');
    if (foodSection) {
      gsap.fromTo('#pangan .swiper-slide', { y: 84, opacity: 0, rotation: 2 }, {
        y: 0, opacity: 1, rotation: 0, duration: .8, stagger: .065, ease: 'power3.out',
        scrollTrigger: { trigger: '#pangan .spl-food-swiper', start: 'top 84%' }
      });
    }

    // Download CTA cards already use the generic [data-reveal] motion above.
    // The former .platform-card / .availability-hill elements were removed
    // by the download CTA redesign, so no legacy GSAP selectors are retained.

    document.querySelectorAll('[data-page-hero]').forEach((hero) => {
      const bg = hero.querySelector('.internal-hero-bg');
      if (bg) {
        gsap.to(bg, {
          yPercent: 12, scale: 1.08, ease: 'none',
          scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: .8 }
        });
      }
      gsap.fromTo(hero.querySelectorAll('[data-page-hero-enter]'), { y: 40, opacity: 0 }, {
        y: 0, opacity: 1, duration: .8, stagger: .11, ease: 'power3.out'
      });
    });

    document.querySelectorAll('.footer-landscape img').forEach((img) => {
      gsap.to(img, {
        y: 4, scale: 1.08, ease: 'none',
        scrollTrigger: { trigger: img.closest('.site-footer'), start: 'top bottom', end: 'bottom bottom', scrub: .8 }
      });
    });

    ScrollTrigger.create({
      trigger: document.body,
      start: 'top top',
      end: 'max',
      onRefresh: () => document.body.dataset.motionReady = 'true'
    });
    ScrollTrigger.refresh();
  };

  // Functional fallback for offline preview when GSAP cannot load.
  const initFallbackMotion = () => {
    if (gsapReady || reduceMotionQuery.matches) return;
    const reveals = [...document.querySelectorAll('[data-reveal], [data-page-hero-enter], [data-hero-enter]')];
    if (!('IntersectionObserver' in window)) {
      showEverything();
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.animate([
          { opacity: 0, transform: 'translateY(44px)' },
          { opacity: 1, transform: 'translateY(0)' }
        ], { duration: 720, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'forwards' });
        observer.unobserve(entry.target);
      });
    }, { threshold: .12 });
    reveals.forEach((el) => observer.observe(el));

    const hero = document.querySelector('#hero');
    const about = document.querySelector('#tentang-singkat');
    const journeyCards = [...document.querySelectorAll('[data-journey-card]')];
    const bg = hero?.querySelector('.hero-bg-img');
    const chars = hero ? [...hero.querySelectorAll('.hero-character-parallax')] : [];
    const journeyTargets = [
      [-118, -150, -10], [72, -86, 8], [-95, 14, -6], [96, 86, 7], [-16, 158, -2]
    ];
    const onScroll = () => {
      if (hero) {
        const rect = hero.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, -rect.top / Math.max(rect.height, 1)));
        if (bg) bg.style.transform = `translate3d(0,${p * 54}px,0) scale(${1.035 + p * .065})`;
        chars.forEach((node, i) => { node.style.transform = `translate3d(${(i % 2 ? 1 : -1) * p * 12}px,${-p * [46,82,60,92][i]}px,0)`; });
      }
      if (about && journeyCards.length) {
        const rect = about.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, (window.innerHeight - rect.top) / Math.max(window.innerHeight * .75, 1)));
        journeyCards.forEach((card, i) => {
          const [x, y, r] = journeyTargets[i];
          card.style.transform = `translate(calc(-50% + ${x * p}px), calc(-50% + ${y * p}px)) rotate(${r * p + (i - 2) * 2.8 * (1 - p)}deg)`;
          card.style.zIndex = String(journeyCards.length - i);
        });
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  };

  const init = () => {
    initSwiper();
    initGsap();
    initFallbackMotion();
    if (reduceMotionQuery.matches) showEverything();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();

/* SPL 07 FOOD POLISH START */
(function () {
  function padFoodNumber(value) {
    return String(value).padStart(2, '0');
  }

  function getFoodCards() {
    return Array.from(document.querySelectorAll('.food-card'));
  }

  function getVisibleFoodSlideIndexes(swiper) {
    if (!swiper || !swiper.el || !swiper.slides) {
      return [];
    }

    const viewportRect = swiper.el.getBoundingClientRect();

    return Array.from(swiper.slides)
      .map((slide, index) => {
        const rect = slide.getBoundingClientRect();
        const visibleWidth = Math.max(
          0,
          Math.min(rect.right, viewportRect.right) -
          Math.max(rect.left, viewportRect.left)
        );
        const visibilityRatio = rect.width > 0
          ? visibleWidth / rect.width
          : 0;

        return {
          index,
          visibilityRatio
        };
      })
      .filter((entry) => entry.visibilityRatio >= 0.5)
      .map((entry) => entry.index);
  }

  function updateCounter(swiper) {
    const current = document.querySelector('[data-food-current]');
    const total = document.querySelector('[data-food-total]');
    const visibleIndexes = getVisibleFoodSlideIndexes(swiper);
    const totalSlides = swiper?.slides?.length || 0;

    if (current) {
      if (visibleIndexes.length > 0) {
        const firstVisible = visibleIndexes[0] + 1;
        const lastVisible = visibleIndexes[visibleIndexes.length - 1] + 1;

        current.textContent = firstVisible === lastVisible
          ? padFoodNumber(firstVisible)
          : `${padFoodNumber(firstVisible)}–${padFoodNumber(lastVisible)}`;
      }
      else {
        current.textContent = padFoodNumber((swiper?.realIndex || 0) + 1);
      }
    }

    if (total) {
      total.textContent = padFoodNumber(totalSlides);
    }
  }

  function setSelectedFood(swiper, selectedIndex, shouldCenter) {
    const root = document.querySelector('.spl-food-swiper');
    const cards = getFoodCards();

    if (!root || !cards.length) {
      return;
    }

    root.classList.add('has-selection');

    cards.forEach((card, index) => {
      const selected = index === selectedIndex;
      card.setAttribute('aria-pressed', selected ? 'true' : 'false');

      const slide = card.closest('.swiper-slide');
      if (slide) {
        slide.classList.toggle('is-selected', selected);
      }
    });

    if (shouldCenter && swiper) {
      const visibleCount = Math.max(1, Math.floor(swiper.params.slidesPerView || 1));
      const centerOffset = Math.floor((visibleCount - 1) / 2);
      const target = Math.max(0, Math.min(
        selectedIndex - centerOffset,
        swiper.slides.length - visibleCount
      ));

      swiper.slideTo(target, 520);
    }

    if (
      window.gsap &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      const selectedCard = cards[selectedIndex];
      window.gsap.fromTo(
        selectedCard,
        { scale: .97, y: 4 },
        {
          scale: 1,
          y: 0,
          duration: .38,
          ease: 'back.out(1.35)',
          overwrite: true,
          clearProps: 'scale,y'
        }
      );
    }
  }

  function openFoodDetail(card) {
    const modalElement = document.getElementById('foodDetailModal');

    if (!modalElement || !card) {
      return;
    }

    const modalImage = modalElement.querySelector('[data-food-modal-image]');
    const modalGroup = modalElement.querySelector('[data-food-modal-group]');
    const modalTitle = modalElement.querySelector('[data-food-modal-title]');
    const modalDescription = modalElement.querySelector('[data-food-modal-description]');

    const name = card.dataset.foodName || '';
    const group = card.dataset.foodGroup || '';
    const description = card.dataset.foodDescription || '';
    const image = card.dataset.foodImage || '';

    if (modalImage) {
      modalImage.src = image;
      modalImage.alt = name;
    }

    if (modalGroup) {
      modalGroup.textContent = group;
    }

    if (modalTitle) {
      modalTitle.textContent = name;
    }

    if (modalDescription) {
      modalDescription.textContent = description;
    }

    if (
      window.bootstrap &&
      typeof window.bootstrap.Modal === 'function'
    ) {
      window.bootstrap.Modal.getOrCreateInstance(modalElement).show();
    }
  }

  function bindFoodCardInteractions(swiper) {
    const cards = getFoodCards();

    cards.forEach((card, index) => {
      card.addEventListener('click', (event) => {
        if (event.target.closest('[data-food-detail]')) {
          event.stopPropagation();
          openFoodDetail(card);
          return;
        }

        setSelectedFood(swiper, index, true);
      });

      card.addEventListener('keydown', (event) => {
        if (event.target.closest('[data-food-detail]')) {
          return;
        }

        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          setSelectedFood(swiper, index, true);
        }
      });

      const detailButton = card.querySelector('[data-food-detail]');
      if (detailButton) {
        detailButton.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();
          openFoodDetail(card);
        });
      }
    });
  }

  function animateFoodSection() {
    const section = document.querySelector('.foods-section');

    if (
      !section ||
      !window.gsap ||
      !window.ScrollTrigger ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      return;
    }

    window.gsap.fromTo(
      '.foods-heading, .foods-nav-wrap',
      { y: 24, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: .7,
        stagger: .1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: section,
          start: 'top 78%',
          once: true
        }
      }
    );

    window.gsap.fromTo(
      '.spl-food-swiper .swiper-slide',
      { y: 28, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: .65,
        stagger: .055,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.foods-stage',
          start: 'top 82%',
          once: true
        }
      }
    );
  }

  function initInteractiveFoodSwiper() {
    const root = document.querySelector('.spl-food-swiper');

    if (!root || typeof window.Swiper !== 'function') {
      return;
    }

    if (root.swiper && typeof root.swiper.destroy === 'function') {
      root.swiper.destroy(true, true);
    }

    const swiper = new window.Swiper(root, {
      speed: 620,
      grabCursor: true,
      watchSlidesProgress: true,
      slidesPerView: 1.08,
      spaceBetween: 14,
      navigation: {
        nextEl: '.spl-food-next',
        prevEl: '.spl-food-prev'
      },
      pagination: {
        el: '.spl-food-pagination',
        clickable: true
      },
      keyboard: {
        enabled: true
      },
      breakpoints: {
        576: {
          slidesPerView: 1.55,
          spaceBetween: 16
        },
        768: {
          slidesPerView: 2.35,
          spaceBetween: 18
        },
        992: {
          slidesPerView: 3,
          spaceBetween: 20
        },
        1200: {
          slidesPerView: 4,
          spaceBetween: 20
        },
        1600: {
          slidesPerView: 4.4,
          spaceBetween: 22
        }
      },
      on: {
        init(instance) {
          updateCounter(instance);
        },
        slideChange(instance) {
          updateCounter(instance);
        },
        slideChangeTransitionEnd(instance) {
          updateCounter(instance);
        },
        resize(instance) {
          updateCounter(instance);
        },
        breakpoint(instance) {
          updateCounter(instance);
        }
      }
    });

    window.__splFoodSwiper = swiper;
    bindFoodCardInteractions(swiper);
    animateFoodSection();
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      initInteractiveFoodSwiper,
      { once: true }
    );
  }
  else {
    initInteractiveFoodSwiper();
  }
})();
/* SPL 07 FOOD POLISH END */

/* SPL 08 DOWNLOAD CTA START */
(function () {
  const section = document.querySelector('.download-cta-section');

  if (!section) {
    return;
  }

  const counters = Array.from(
    section.querySelectorAll('[data-download-counter]')
  );

  if (!counters.length) {
    return;
  }

  const formatter = new Intl.NumberFormat('id-ID');
  const reduceMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  function renderCounter(element, value) {
    const suffix = element.dataset.downloadSuffix || '';
    element.textContent = formatter.format(Math.round(value)) + suffix;
  }

  function setFinalValues() {
    counters.forEach((element) => {
      const target = Number(element.dataset.downloadTarget || 0);
      renderCounter(element, target);
    });
  }

  if (
    reduceMotion ||
    !window.gsap ||
    !window.ScrollTrigger
  ) {
    setFinalValues();
    return;
  }

  let played = false;

  ScrollTrigger.create({
    id: 'download-counter-sequence',
    trigger: section,
    start: 'top 72%',
    once: true,
    onEnter: function () {
      if (played) {
        return;
      }

      played = true;

      counters.forEach((element, index) => {
        const target = Number(element.dataset.downloadTarget || 0);
        const state = { value: 0 };

        gsap.to(state, {
          value: target,
          duration: 1.45 + (index * .12),
          ease: 'power2.out',
          onUpdate: function () {
            renderCounter(element, state.value);
          },
          onComplete: function () {
            renderCounter(element, target);
          }
        });
      });
    }
  });
})();
/* SPL 08 DOWNLOAD CTA END */

/* SPL 09 NAV FOOTER SCROLLSPY START */
(function () {
  const navbar = document.querySelector('[data-spl-navbar]');
  const collapseElement = document.getElementById('splNav');
  const sectionLinks = Array.from(
    document.querySelectorAll('[data-section-link]')
  );

  if (!navbar || !sectionLinks.length) {
    return;
  }

  const sections = sectionLinks
    .map((link) => {
      const selector = link.getAttribute('href');
      const section = selector ? document.querySelector(selector) : null;
      return section ? { link, section } : null;
    })
    .filter(Boolean);

  if (!sections.length) {
    return;
  }

  function setActiveSectionLink(activeLink) {
    sectionLinks.forEach((link) => {
      const active = link === activeLink;
      link.classList.toggle('active', active);

      if (active) {
        link.setAttribute('aria-current', 'page');
      }
      else {
        link.removeAttribute('aria-current');
      }
    });
  }

  function updateSectionNavActiveState() {
    const navbarHeight = navbar.getBoundingClientRect().height;
    const marker =
      window.scrollY +
      navbarHeight +
      (window.innerHeight * 0.24);

    let active = sections[0];

    sections.forEach((entry) => {
      if (entry.section.offsetTop <= marker) {
        active = entry;
      }
    });

    setActiveSectionLink(active.link);
  }

  let ticking = false;

  function scheduleSectionNavUpdate() {
    if (ticking) {
      return;
    }

    ticking = true;

    window.requestAnimationFrame(() => {
      updateSectionNavActiveState();
      ticking = false;
    });
  }

  sectionLinks.forEach((link) => {
    link.addEventListener('click', () => {
      setActiveSectionLink(link);

      if (
        collapseElement &&
        collapseElement.classList.contains('show') &&
        window.bootstrap &&
        typeof window.bootstrap.Collapse === 'function'
      ) {
        window.bootstrap.Collapse.getOrCreateInstance(collapseElement).hide();
      }
    });
  });

  document
    .querySelectorAll('.footer-nav-main a[href^="#"]')
    .forEach((link) => {
      link.addEventListener('click', () => {
        const selector = link.getAttribute('href');
        const matchingNav = sectionLinks.find(
          (navLink) => navLink.getAttribute('href') === selector
        );

        if (matchingNav) {
          setActiveSectionLink(matchingNav);
        }
      });
    });

  updateSectionNavActiveState();

  window.addEventListener(
    'scroll',
    scheduleSectionNavUpdate,
    { passive: true }
  );

  window.addEventListener(
    'resize',
    scheduleSectionNavUpdate,
    { passive: true }
  );

  window.addEventListener(
    'hashchange',
    scheduleSectionNavUpdate
  );
})();
/* SPL 09 NAV FOOTER SCROLLSPY END */
