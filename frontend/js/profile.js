document.addEventListener("DOMContentLoaded", () => {
  const pdfItems = document.querySelectorAll(".pdf-item");

  pdfItems.forEach(item => {
    item.addEventListener("click", () => {
      item.classList.add("active");
      setTimeout(() => item.classList.remove("active"), 250);
    });
  });
});
