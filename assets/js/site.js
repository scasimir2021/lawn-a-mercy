const LOCAL_CONFIG = new URL('data/site.json', document.baseURI).href;

const ICONS = {
  lawn: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 16h12l2-5H9L7 7H4"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/><path d="M13 11V7h4"/></svg>',
  edge: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19c5-7 8-11 14-14M7 6l11 11M5 15c1 2 2 3 4 4"/></svg>',
  leaf: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 4C11 4 5 8 5 15c0 3 2 5 5 5 7 0 10-7 10-16Z"/><path d="M4 21c3-5 7-8 12-11"/></svg>',
  hedge: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="7" cy="7" r="3"/><circle cx="7" cy="17" r="3"/><path d="m9 9 10 8M9 15 19 7"/></svg>',
  wash: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 18h6l3-8 7 2M14 7l5 1M7 18v2M17 13c0 3-2 5-2 5s-2-2-2-5a2 2 0 1 1 4 0Z"/></svg>',
  instagram: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
  tiktok: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4v10.2a4.2 4.2 0 1 1-3.2-4.1M14 4c.7 2.4 2.3 3.8 5 4"/></svg>',
  linkedin: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 10v7M8 7v.1M12 17v-7m0 3c.6-2 5-2.2 5 1v3"/></svg>',
  defaultSocial: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12h8M12 8v8"/></svg>',
  photo: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="15" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m4 17 5-4 4 3 3-2 4 3"/></svg>',
};

const SOCIAL_LABELS = {
  instagram: 'Instagram',
  tiktok: 'TikTok',
  linkedin: 'LinkedIn',
};

function getPath(object, path) {
  return path.split('.').reduce((value, key) => value?.[key], object);
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function mergeConfig(base, update) {
  if (!isPlainObject(update)) return base;
  const merged = { ...base };
  Object.entries(update).forEach(([key, value]) => {
    merged[key] = isPlainObject(value) && isPlainObject(base?.[key])
      ? mergeConfig(base[key], value)
      : value;
  });
  return merged;
}

function safeExternalUrl(value) {
  if (typeof value !== 'string' || !value.trim()) return '';
  try {
    const url = new URL(value);
    return url.protocol === 'https:' ? url.href : '';
  } catch {
    return '';
  }
}

function safeRouteUrl(value, routeName) {
  const allowed = {
    call: ['tel:'],
    quote: ['sms:'],
    text: ['sms:'],
    email: ['mailto:'],
    socials: ['https:'],
  }[routeName] || [];
  if (typeof value !== 'string' || !value.trim()) return '';
  try {
    const url = new URL(value, document.baseURI);
    return allowed.includes(url.protocol) ? url.href : '';
  } catch {
    return '';
  }
}

function applyTheme(theme = {}) {
  Object.entries(theme).forEach(([key, value]) => {
    if (typeof value === 'string' && /^#[0-9a-f]{3,8}$/i.test(value)) {
      document.documentElement.style.setProperty(`--${key.replaceAll('_', '-')}`, value);
    }
  });
}

function serviceIcon(name) {
  const value = name.toLowerCase();
  if (value.includes('pressure')) return ICONS.wash;
  if (value.includes('hedge')) return ICONS.hedge;
  if (value.includes('leaf') || value.includes('cleanup') || value.includes('mulch')) return ICONS.leaf;
  if (value.includes('edg') || value.includes('trimm') || value.includes('weed')) return ICONS.edge;
  return ICONS.lawn;
}

function renderServices(config) {
  const grid = document.getElementById('serviceGrid');
  if (!grid) return;
  grid.replaceChildren();
  const details = config.service_details || {};

  (config.services || []).forEach((service) => {
    const name = typeof service === 'string' ? service : service?.name;
    if (!name) return;
    const description = typeof service === 'object' ? service.description : details[name];
    const card = document.createElement('article');
    card.className = 'service-card';

    const icon = document.createElement('span');
    icon.className = 'service-icon';
    icon.innerHTML = serviceIcon(name);

    const copy = document.createElement('div');
    const heading = document.createElement('h3');
    heading.textContent = name;
    copy.appendChild(heading);
    if (description) {
      const text = document.createElement('p');
      text.textContent = description;
      copy.appendChild(text);
    }

    card.append(icon, copy);
    grid.appendChild(card);
  });
}

function placeholderCard(category) {
  const card = document.createElement('article');
  card.className = 'work-card work-card-placeholder';
  const media = document.createElement('div');
  media.className = 'work-media';
  const placeholder = document.createElement('div');
  placeholder.className = 'work-placeholder';
  placeholder.innerHTML = `${ICONS.photo}<span>Photography coming soon</span>`;
  media.appendChild(placeholder);

  const copy = document.createElement('div');
  copy.className = 'work-card-copy';
  const type = document.createElement('small');
  type.textContent = category.label || 'Work category';
  const heading = document.createElement('h3');
  heading.textContent = category.title || String(category);
  const note = document.createElement('p');
  note.textContent = category.note || 'Finished-project images will be added as the catalog grows.';
  copy.append(type, heading, note);
  card.append(media, copy);
  return card;
}

function projectCard(project) {
  const card = document.createElement('article');
  card.className = 'work-card';
  const media = document.createElement('div');
  media.className = 'work-media';
  const imagePath = String(project.image || '').replaceAll('\\', '/');
  const imageUrl = imagePath.startsWith('assets/work/') && !imagePath.split('/').includes('..')
    ? imagePath
    : '';
  if (imageUrl) {
    const image = document.createElement('img');
    image.src = imageUrl;
    image.alt = project.alt || `${project.title || 'Completed landscaping project'} in ${project.location || 'the Lawrenceville area'}`;
    image.loading = 'lazy';
    media.appendChild(image);
  } else {
    const placeholder = document.createElement('div');
    placeholder.className = 'work-placeholder';
    placeholder.innerHTML = `${ICONS.photo}<span>Photography coming soon</span>`;
    media.appendChild(placeholder);
  }

  const copy = document.createElement('div');
  copy.className = 'work-card-copy';
  const type = document.createElement('small');
  type.textContent = [project.category, project.location].filter(Boolean).join(' · ') || 'Completed property';
  const heading = document.createElement('h3');
  heading.textContent = project.title || 'Property care project';
  const note = document.createElement('p');
  note.textContent = project.description || 'Project details coming soon.';
  copy.append(type, heading, note);
  card.append(media, copy);
  return card;
}

function renderWork(config) {
  const grid = document.getElementById('workGrid');
  if (!grid) return;
  grid.replaceChildren();
  const portfolio = config.portfolio || {};
  const projects = (portfolio.items || []).filter((item) => (
    item && item.published === true && item.approved_for_public === true
  ));
  if (projects.length) {
    projects.forEach((project) => grid.appendChild(projectCard(project)));
    return;
  }
  (portfolio.categories || []).slice(0, 3).forEach((category) => grid.appendChild(placeholderCard(category)));
}

function renderSocials(config) {
  const grid = document.getElementById('socialLinks');
  if (!grid) return;
  grid.replaceChildren();
  const handles = config.social_handles || {};

  Object.entries(config.social || {}).forEach(([network, value]) => {
    const url = safeExternalUrl(value);
    if (!url) return;
    const label = SOCIAL_LABELS[network] || network.replaceAll('_', ' ');
    const link = document.createElement('a');
    link.className = `social-card social-${network}`;
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.setAttribute('aria-label', `Open Lawn-A-Mercy on ${label}`);

    const icon = document.createElement('span');
    icon.className = 'social-icon';
    icon.innerHTML = ICONS[network] || ICONS.defaultSocial;

    const copy = document.createElement('span');
    copy.className = 'social-copy';
    const name = document.createElement('strong');
    name.textContent = label;
    const handle = document.createElement('span');
    handle.textContent = handles[network] || 'Follow Lawn-A-Mercy';
    copy.append(name, handle);

    const arrow = document.createElement('span');
    arrow.className = 'social-arrow';
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '↗';

    link.append(icon, copy, arrow);
    grid.appendChild(link);
  });
}

function applyConfig(config) {
  applyTheme(config.theme);
  document.querySelectorAll('[data-bind]').forEach((element) => {
    const value = getPath(config, element.dataset.bind);
    if (value != null) element.textContent = value;
  });
  document.querySelectorAll('[data-bind-href]').forEach((element) => {
    const routeName = element.dataset.bindHref;
    const route = safeRouteUrl(config.routes?.[routeName], routeName);
    if (route) element.href = route;
  });
  const structuredData = document.getElementById('structuredData');
  if (structuredData) {
    const sameAs = Object.values(config.social || {}).map(safeExternalUrl).filter(Boolean);
    structuredData.textContent = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'HomeAndConstructionBusiness',
      name: config.brand?.name || 'Lawn-A-Mercy Landscaping',
      url: safeExternalUrl(config.base_url) || document.location.href,
      telephone: config.contact?.phone || '',
      email: config.contact?.email || '',
      address: {
        '@type': 'PostalAddress',
        addressLocality: config.contact?.city || 'Lawrenceville, GA',
        addressRegion: 'GA',
        addressCountry: 'US',
      },
      areaServed: config.contact?.service_area || 'Lawrenceville and surrounding areas',
      sameAs,
    });
  }
  renderServices(config);
  renderWork(config);
  renderSocials(config);
}

async function getJson(url) {
  const separator = url.includes('?') ? '&' : '?';
  const response = await fetch(`${url}${separator}v=${Date.now()}`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function start() {
  try {
    const local = await getJson(LOCAL_CONFIG);
    applyConfig(local);
    const remote = local.runtime?.remote_config_url;
    if (!remote) return;
    const pollSeconds = Math.max(5, Number(local.runtime?.poll_seconds || 30));
    const pull = async () => {
      try {
        applyConfig(mergeConfig(local, await getJson(remote)));
      } catch (error) {
        console.warn('Remote Trio config unavailable; keeping last good site config.', error);
      }
    };
    await pull();
    window.setInterval(pull, pollSeconds * 1000);
  } catch (error) {
    console.error('Could not load site config.', error);
  }
}

const navToggle = document.getElementById('navToggle');
const siteNav = document.getElementById('siteNav');
function setMenu(open) {
  navToggle?.setAttribute('aria-expanded', String(open));
  siteNav?.classList.toggle('is-open', open);
  document.body.classList.toggle('nav-open', open);
}
navToggle?.addEventListener('click', () => setMenu(navToggle.getAttribute('aria-expanded') !== 'true'));
siteNav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') setMenu(false);
});

const currentYear = document.getElementById('currentYear');
if (currentYear) currentYear.textContent = new Date().getFullYear();

start();
