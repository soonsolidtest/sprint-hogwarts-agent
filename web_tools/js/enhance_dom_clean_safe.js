
(function () {
  const start = performance.now();

  function getPageSource() {
    const bodyClone = document.body.cloneNode(true);
    const end = performance.now();
    console.log("⏱ DOM snapshot time:", (end - start).toFixed(2), "ms");
    return bodyClone.outerHTML;
  }

  return getPageSource();
})();
