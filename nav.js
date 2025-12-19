(() => {
  const mountNav = async () => {
    try {
      const res = await fetch("nav.html");
      if (!res.ok) return;
      const html = await res.text();
      const placeholder = document.getElementById("navbar-placeholder");
      if (!placeholder) return;
      placeholder.innerHTML = html;
      const toggle = placeholder.querySelector("[data-nav-toggle]");
      const mobileMenu = placeholder.querySelector("[data-nav-mobile]");
      const header = placeholder.querySelector("[data-nav-header]");
      const links = placeholder.querySelector("[data-nav-links]");
      const mobileLinks = mobileMenu ? mobileMenu.querySelectorAll("a") : [];
      const brand = placeholder.querySelector("[data-nav-brand]");
      const logoImg = placeholder.querySelector("[data-logo-img]");
      const icon = placeholder.querySelector("[data-nav-icon]");
      const label = placeholder.querySelector("[data-nav-label]");
      const allowTransparent = document.body.dataset.navTransparent === "true";

      const closeMobile = () => {
        if (mobileMenu && !mobileMenu.classList.contains("hidden")) {
          mobileMenu.classList.add("hidden");
          if (toggle) toggle.setAttribute("aria-expanded", "false");
        }
      };

      if (toggle && mobileMenu) {
        toggle.addEventListener("click", () => {
          const isHidden = mobileMenu.classList.toggle("hidden");
          toggle.setAttribute("aria-expanded", String(!isHidden));
        });

        mobileMenu.querySelectorAll("a").forEach((link) =>
          link.addEventListener("click", () => closeMobile())
        );
      }

      window.addEventListener("resize", () => {
        if (window.innerWidth >= 768) {
          closeMobile();
        }
      });

      const handleScroll = () => {
        if (!header) return;
        const atTop = window.scrollY < 10;
        const textLight = "text-white";
        const textDark = "text-ink";
        const setLogoTone = (light) => {
          if (!logoImg) return;
          logoImg.classList.toggle("invert", light);
          logoImg.classList.toggle("brightness-0", !light);
        };

        if (!allowTransparent) {
          header.classList.add("bg-white/90", "backdrop-blur-lg");
          header.classList.remove("bg-transparent", "border-transparent");
          [links?.querySelectorAll("a") || [], mobileLinks].flat().forEach((a) => {
            a.classList.remove(textLight);
            a.classList.add(textDark);
          });
          if (brand) { brand.classList.remove(textLight); brand.classList.add(textDark); }
          setLogoTone(false);
          if (icon) { icon.classList.remove(textLight); icon.classList.add(textDark); }
          if (label) { label.classList.remove(textLight); label.classList.add(textDark); }
          if (mobileMenu) {
            mobileMenu.classList.remove("bg-black/40", "text-white");
            mobileMenu.classList.add("bg-transparent", "text-ink");
          }
          return;
        }

        header.classList.toggle("bg-white/90", !atTop);
        header.classList.toggle("backdrop-blur-2xl", true);
        header.classList.toggle("bg-transparent", atTop);
        header.classList.toggle("border-transparent", atTop);

        const applyColors = (nodeList, light) => {
          nodeList.forEach((n) => {
            n.classList.toggle(textLight, light);
            n.classList.toggle(textDark, !light);
          });
        };

        if (links) applyColors(links.querySelectorAll("a"), allowTransparent && atTop);
        applyColors(mobileLinks, allowTransparent && atTop);
        if (brand) { brand.classList.toggle(textLight, atTop); brand.classList.toggle(textDark, !atTop); }
        setLogoTone(atTop);
        if (icon) { icon.classList.toggle(textLight, atTop); icon.classList.toggle(textDark, !atTop); }
        if (label) { label.classList.toggle(textLight, atTop); label.classList.toggle(textDark, !atTop); }
        if (mobileMenu) {
          mobileMenu.classList.toggle("bg-transparent", true);
          mobileMenu.classList.toggle("text-white", allowTransparent && atTop);
          mobileMenu.classList.toggle("text-ink", !allowTransparent || !atTop);
          mobileMenu.classList.toggle("bg-white", false);
        }
      };
      handleScroll();
      window.addEventListener("scroll", handleScroll);
    } catch (err) {
      console.error("Nav load error", err);
    }
  };

  document.readyState === "loading"
    ? document.addEventListener("DOMContentLoaded", mountNav)
    : mountNav();
})();
