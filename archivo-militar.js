window.addEventListener('scroll', () => {
  const maxScroll = document.body.scrollHeight - window.innerHeight;
  const pct = maxScroll > 0 ? (window.scrollY / maxScroll) * 100 : 0;
  const progress = document.getElementById('progress');
  if (progress) progress.style.width = `${pct}%`;
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.22 });

document.querySelectorAll('.section-content').forEach((section) => observer.observe(section));
