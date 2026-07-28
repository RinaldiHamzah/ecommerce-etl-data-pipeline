document.querySelectorAll(".filter-bar select").forEach((select) => {
  select.addEventListener("change", () => {
    select.closest("form").classList.add("is-dirty");
  });
});
