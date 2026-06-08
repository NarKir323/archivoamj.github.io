"use strict";
const entries = {
 1: { title: ['El inicio de ', 'la insurgencia'], meta: 'Septiembre-octubre de 1810 · Dolores, Celaya, Guanajuato, Valladolid y Toluca', body: 'Del Grito de Dolores a la llegada al valle de México, la insurgencia pasó de estallido local a amenaza real contra el virreinato. Este primer tramo agrupa el ascenso vertiginoso de Hidalgo antes del Monte de las Cruces.', link: 'batalla-insurgencia.html' },
 2: { title: ['Monte de ', 'las Cruces'], meta: '30 de octubre de 1810 · Sierra de las Cruces', body: 'La victoria insurgente más cercana a la capital. Monte de las Cruces muestra el punto más alto del impulso de Hidalgo y la gran decisión que no llegó: entrar o no a la Ciudad de México.', link: 'batalla-monte-cruces.html' },
 3: { title: ['Batalla de ', 'Aculco'], meta: '7 de noviembre de 1810 · San Jerónimo Aculco', body: 'Primera derrota decisiva del ejército insurgente. La batalla reveló que el entusiasmo popular no bastaba frente a un mando profesional como el de Calleja y abrió una nueva etapa de repliegue y reorganización.', link: 'batalla-aculco.html' },
 4: { title: ['Guadalajara y la ', 'reorganización'], meta: 'Noviembre-diciembre de 1810 · Occidente novohispano', body: 'En Guadalajara la insurgencia ensayó gobierno, decretos y legitimidad política. Fue el momento de máxima ambición institucional antes del gran desastre militar de enero de 1811.', link: 'batalla-guadalajara.html' },
 5: { title: ['Puente de ', 'Calderón'], meta: '17 de enero de 1811 · Jalisco', body: 'La gran batalla final de la primera campaña. Tras horas de combate, la explosión en las municiones insurgentes convirtió una posibilidad de triunfo en derrota total y cerró la etapa militar de Hidalgo.', link: 'batalla-calderon.html' },
 6: { title: ['Acatita de ', 'Baján'], meta: '21 de marzo de 1811 · Coahuila', body: 'La traición de Ignacio Elizondo y la captura de Hidalgo marcaron el fin de la primera fase insurgente. Ya no fue una gran batalla, sino la clausura amarga de una campaña entera.', link: 'batalla-acatitla.html' }
 };

 const title = document.getElementById('info-title');
 const meta = document.getElementById('info-meta');
 const body = document.getElementById('info-body');
 const link = document.getElementById('info-link');
 const markers = [...document.querySelectorAll('.marker')];
 const timelineButtons = [...document.querySelectorAll('.timeline button')];

 function setActive(id) {
 const entry = entries[id];
 if (!entry) return;
 title.replaceChildren(document.createTextNode(entry.title[0]));
 const emphasis = document.createElement('em');
 emphasis.textContent = entry.title[1];
 title.append(emphasis);
 meta.textContent = entry.meta;
 body.textContent = entry.body;
 link.href = entry.link;
 markers.forEach((marker) => marker.classList.toggle('active', marker.dataset.id === String(id)));
 timelineButtons.forEach((button) => button.classList.toggle('active', button.dataset.id === String(id)));
 }
 markers.forEach((marker) => {
 marker.addEventListener('click', () => setActive(marker.dataset.id));
 });

 timelineButtons.forEach((button) => button.addEventListener('click', () => setActive(button.dataset.id)));
