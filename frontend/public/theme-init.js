(function() {
  try {
    const theme = localStorage.getItem('theme');
    let shouldBeDark;
    if (theme) {
      shouldBeDark = theme === 'dark';
      if (shouldBeDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      shouldBeDark = prefersDark;
      if (prefersDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }

    // Updating the logo to use in the website's header (the top part of the browser tab)
    const favicon = document.getElementById('favicon');
    if (favicon) {
      favicon.href = shouldBeDark ? '/MERIT-white-transparent-logo.jpg' : '/MERIT-black-transparent-logo.png';
    }
  } catch (e) {}
})();

