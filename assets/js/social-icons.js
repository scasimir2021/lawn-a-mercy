const SOCIAL_ICONS = {
  instagram: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
  tiktok: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4v10.2a4.2 4.2 0 1 1-3.2-4.1M14 4c.7 2.4 2.3 3.8 5 4"/></svg>',
  linkedin: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 10v7M8 7v.1M12 17v-7m0 3c.6-2 5-2.2 5 1v3"/></svg>',
};

function addSocialIcons() {
  document.querySelectorAll('.social-link:not(.is-icon-ready)').forEach((link) => {
    const name = link.querySelector('strong')?.textContent?.trim().toLowerCase();
    if (!name || !SOCIAL_ICONS[name]) return;

    const icon = document.createElement('span');
    icon.className = 'social-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.innerHTML = SOCIAL_ICONS[name];

    const copy = document.createElement('span');
    copy.className = 'social-link-copy';
    while (link.firstChild) copy.appendChild(link.firstChild);
    link.append(icon, copy);
    link.classList.add('is-icon-ready');
  });
}

const socialLinks = document.getElementById('socialLinks');
if (socialLinks) {
  new MutationObserver(addSocialIcons).observe(socialLinks, { childList: true });
  addSocialIcons();
}
