/* Match WorldParticle: preload one viewport ahead; autoplay on entry and loop. */
const videos = [...document.querySelectorAll('video.auto-video')];
const visible = new Set();

function play(video) {
  const rect = video.getBoundingClientRect();
  if (!document.hidden && rect.bottom > 0 && rect.top < window.innerHeight) {
    video.play().catch(() => {});
  }
}
videos.forEach(video => {
  video.muted = true;
  video.defaultMuted = true;
  video.loop = true;
  video.playsInline = true;
  video.autoplay = false;
  video.preload = 'none';
  const errorMessage = video.parentElement.querySelector('.video-error');
  video.addEventListener('error', () => { errorMessage.hidden = false; });
  video.querySelector('source').addEventListener('error', () => { errorMessage.hidden = false; });
});

if ('IntersectionObserver' in window) {
  const preload = new IntersectionObserver((entries, observer) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (!isIntersecting) return;
      // Setting preload starts loading without resetting an in-flight play request.
      target.preload = 'auto';
      observer.unobserve(target);
    });
  }, { rootMargin: '100% 0px', threshold: 0 });
  const playback = new IntersectionObserver(entries => {
    let playIndex = 0;
    entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting) {
        visible.add(target);
        setTimeout(() => play(target), playIndex++ * 50);
      } else {
        visible.delete(target);
        target.pause();
      }
    });
  }, { threshold: 0 });
  videos.forEach(video => { preload.observe(video); playback.observe(video); });
} else {
  videos.forEach(video => { video.preload = 'auto'; play(video); });
}

document.addEventListener('visibilitychange', () => {
  if (document.hidden) videos.forEach(video => video.pause());
  else visible.forEach(play);
});

const sections = [...document.querySelectorAll('main > section[id]')];
const links = [...document.querySelectorAll('.nav-links a')];
let scheduled = false;
function updateNavigation() {
  const current = sections.filter(section => section.getBoundingClientRect().top <= 160).at(-1);
  links.forEach(link => {
    if (current && link.hash === `#${current.id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  scheduled = false;
}
window.addEventListener('scroll', () => {
  if (!scheduled) { scheduled = true; requestAnimationFrame(updateNavigation); }
}, { passive: true });
updateNavigation();
