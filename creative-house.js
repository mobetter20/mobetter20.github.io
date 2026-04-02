const rooms = Array.from(document.querySelectorAll("[data-reveal]"));

if (rooms.length > 0) {
  const isTouchFirst = window.matchMedia("(hover: none), (pointer: coarse)").matches;

  const clearActiveRooms = () => {
    rooms.forEach((room) => room.classList.remove("is-active"));
  };

  if (isTouchFirst) {
    rooms.forEach((room) => {
      room.addEventListener("click", (event) => {
        if (!room.classList.contains("is-active")) {
          event.preventDefault();
          clearActiveRooms();
          room.classList.add("is-active");
        }
      });
    });

    document.addEventListener("click", (event) => {
      if (!event.target.closest("[data-reveal]")) {
        clearActiveRooms();
      }
    });
  }
}
