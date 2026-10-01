// Nav dropdowns open on hover in CSS. Touch screens have no hover, so a tap on
// the button toggles the menu here instead; tapping elsewhere or pressing
// Escape closes it, and so does the mouse leaving the dropdown.
const dropdowns = document.querySelectorAll('.nav-dropdown');

function setOpen(dropdown, open) {
  dropdown.classList.toggle('is-open', open);
  dropdown.querySelector('button').setAttribute('aria-expanded', open);
}

dropdowns.forEach((dropdown) => {
  dropdown.querySelector('button').addEventListener('click', () => {
    setOpen(dropdown, !dropdown.classList.contains('is-open'));
  });
  dropdown.addEventListener('mouseleave', () => setOpen(dropdown, false));
});

document.addEventListener('click', (event) => {
  dropdowns.forEach((dropdown) => {
    if (!dropdown.contains(event.target)) setOpen(dropdown, false);
  });
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') dropdowns.forEach((dropdown) => setOpen(dropdown, false));
});
