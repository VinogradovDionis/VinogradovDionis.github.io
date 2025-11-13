function scrollToSection() {
  const section = document.getElementById("main-section");
  const offset = 120; // На сколько пикселей выше прокрутить

  const sectionPosition = section.offsetTop - offset;

  window.scrollTo({
    top: sectionPosition,
    behavior: "smooth",
  });
}
