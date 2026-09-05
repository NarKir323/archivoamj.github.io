"use strict";

const progress = document.getElementById("progress");

if (progress) {
  const updateProgress = () => {
    const maxScroll = document.body.scrollHeight - window.innerHeight;
    const percentage = maxScroll > 0 ? (window.scrollY / maxScroll) * 100 : 0;
    progress.style.width = `${percentage}%`;
  };

  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();
}

const reveals = document.querySelectorAll(".reveal");

if (reveals.length) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        window.setTimeout(() => entry.target.classList.add("visible"), index * 100);
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  reveals.forEach((element) => revealObserver.observe(element));
}

document.querySelectorAll(".flip-card").forEach((card) => {
  card.addEventListener("click", () => card.classList.toggle("flipped"));
});
