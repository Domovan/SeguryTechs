const body = document.querySelector("body");
const darkLight = document.querySelector("#darkLight");
const sidebar = document.querySelector(".sidebar");
const submenuItems = document.querySelectorAll(".submenu_item");
const sidebarOpen = document.querySelector("#sidebarOpen");
const sidebarClose = document.querySelector(".collapse_sidebar");
const sidebarExpand = document.querySelector(".expand_sidebar");
const logo = document.querySelector(".navbar-brand img"); // Seleccionar la imagen del logo

// Alternar el estado de la barra lateral
sidebarOpen.addEventListener("click", () => sidebar.classList.toggle("close"));
sidebarClose.addEventListener("click", () => {
  sidebar.classList.add("close", "hoverable");
});
sidebarExpand.addEventListener("click", () => {
  sidebar.classList.remove("close", "hoverable");
});

// Cambiar estado de la barra lateral al pasar el ratón
sidebar.addEventListener("mouseenter", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.remove("close");
  }
});
sidebar.addEventListener("mouseleave", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.add("close");
  }
});

// Cambiar entre tema claro y oscuro
darkLight.addEventListener("click", () => {
  body.classList.toggle("dark");
  
  // Cambiar el ícono del botón de modo claro/oscuro
  if (body.classList.contains("dark")) {
    darkLight.classList.replace("bx-sun", "bx-moon");

    // Cambiar el logo al de tema oscuro
    logo.src = "static/img/logo-white.png"; // Reemplaza con la ruta de tu logo oscuro
  } else {
    darkLight.classList.replace("bx-moon", "bx-sun");

    // Cambiar el logo al de tema claro
    logo.src = "static/img/logo.png"; // Reemplaza con la ruta de tu logo claro
  }
});

// Submenús
submenuItems.forEach((item, index) => {
  item.addEventListener("click", () => {
    item.classList.toggle("show_submenu");
    submenuItems.forEach((item2, index2) => {
      if (index !== index2) {
        item2.classList.remove("show_submenu");
      }
    });
  });
});

// Ajustar el estado de la barra lateral según el tamaño de la ventana
if (window.innerWidth < 768) {
  sidebar.classList.add("close");
} else {
  sidebar.classList.remove("close");
}
