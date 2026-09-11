(() => {
  'use strict';

  window.SPL_SITE_CONFIG = Object.freeze({
    brand: Object.freeze({
      name: 'Sahabat Pangan Lokal',
      home: '/'
    }),
    sections: Object.freeze([
      Object.freeze({
        key: 'hero',
        label: 'Beranda',
        hash: '#hero'
      }),
      Object.freeze({
        key: 'journey',
        label: 'Petualangan',
        hash: '#tentang-singkat'
      }),
      Object.freeze({
        key: 'food',
        label: 'Pangan',
        hash: '#pangan'
      }),
      Object.freeze({
        key: 'download',
        label: 'Unduh',
        hash: '#ketersediaan'
      })
    ]),
    pages: Object.freeze([
      Object.freeze({
        key: 'tentang',
        label: 'Tentang',
        href: '/tentang/'
      }),
      Object.freeze({
        key: 'status',
        label: 'Kabar',
        href: '/status/'
      })
    ]),
    legal: Object.freeze({
      privacy: Object.freeze({
        label: 'Privasi',
        href: '/privasi/'
      })
    }),
    footer: Object.freeze({
      institution: 'Universitas PGRI Silampari',
      copyright: '© 2026 Sahabat Pangan Lokal',
      tagline: 'Petualangan mengenal pangan lokal melalui pengalaman bermain.'
    })
  });
})();
