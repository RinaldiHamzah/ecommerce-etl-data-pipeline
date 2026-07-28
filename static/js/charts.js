window.addEventListener("resize", () => {
  document.querySelectorAll(".js-plotly-plot").forEach((chart) => {
    if (window.Plotly) {
      window.Plotly.Plots.resize(chart);
    }
  });
});
