(() => {
  const mountFooter = async () => {
    const placeholder = document.getElementById("footer-placeholder");
    if (!placeholder) return;
    try {
      const res = await fetch("/footer.html");
      if (!res.ok) return;
      placeholder.innerHTML = await res.text();
    } catch (err) {
      console.error("Footer load error", err);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountFooter);
  } else {
    mountFooter();
  }
})();
