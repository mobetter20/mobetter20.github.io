const writingHouse = document.querySelector(".writing-house");

if (writingHouse) {
  const roomCards = Array.from(writingHouse.querySelectorAll(".house-grid > .room"));
  const houseGrid = writingHouse.querySelector(".house-grid");
  const stage = writingHouse.querySelector(".house-stage");
  const frame = writingHouse.querySelector(".house-frame");
  const cursor = writingHouse.querySelector(".writing-cursor");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const countLabel = writingHouse.querySelector("[data-room-count-label]");

  const countToWords = (count) => {
    const ones = [
      "Zero",
      "One",
      "Two",
      "Three",
      "Four",
      "Five",
      "Six",
      "Seven",
      "Eight",
      "Nine",
      "Ten",
      "Eleven",
      "Twelve",
      "Thirteen",
      "Fourteen",
      "Fifteen",
      "Sixteen",
      "Seventeen",
      "Eighteen",
      "Nineteen"
    ];
    const tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty"];

    if (count < 20) {
      return ones[count] || String(count);
    }

    if (count < 60) {
      const tenValue = Math.floor(count / 10);
      const oneValue = count % 10;
      return oneValue ? `${tens[tenValue]}-${ones[oneValue].toLowerCase()}` : tens[tenValue];
    }

    return String(count);
  };

  if (countLabel) {
    countLabel.textContent = countToWords(roomCards.length);
  }

  if (houseGrid) {
    houseGrid.dataset.roomCount = String(roomCards.length);
  }

  const entries = Array.from(writingHouse.querySelectorAll("[data-type-text]")).map((element) => ({
    element,
    text: element.dataset.typeText,
    kind: element.dataset.typeKind || "copy",
    room: element.closest("[data-room]")
  }));

  const state = {
    entryIndex: 0,
    timer: null,
    isSettled: false
  };

  const clearTimer = () => {
    clearTimeout(state.timer);
  };

  const clearFocus = () => {
    writingHouse.querySelectorAll(".is-writing-focus").forEach((room) => {
      room.classList.remove("is-writing-focus");
    });
  };

  const clearTypedText = () => {
    entries.forEach((entry) => {
      entry.element.textContent = "";
    });
  };

  const setSettledState = () => {
    state.isSettled = true;
    clearFocus();
    frame.classList.add("is-settled");
    cursor.classList.remove("is-visible");
  };

  const moveCursor = (entry) => {
    const stageBox = stage.getBoundingClientRect();
    const targetBox = entry.element.getBoundingClientRect();
    const fallbackBox = entry.element.parentElement.getBoundingClientRect();
    const box = targetBox.width || targetBox.height ? targetBox : fallbackBox;

    cursor.style.left = `${box.right - stageBox.left + 2}px`;
    cursor.style.top = `${box.top - stageBox.top + box.height * 0.14}px`;
  };

  const nextDelay = (entry) => {
    if (entry.kind === "meta") {
      return 36;
    }
    if (entry.kind === "footer") {
      return 42;
    }
    return 48;
  };

  const nextIncrement = (entry) => {
    if (entry.kind === "meta") {
      return 1;
    }
    return 1;
  };

  const typeStep = () => {
    const entry = entries[state.entryIndex];

    if (!entry) {
      state.timer = setTimeout(setSettledState, 420);
      return;
    }

    clearFocus();
    if (entry.room) {
      entry.room.classList.add("is-writing-focus");
    }

    moveCursor(entry);

    const current = entry.element.textContent;
    if (current.length < entry.text.length) {
      entry.element.textContent = entry.text.slice(
        0,
        Math.min(entry.text.length, current.length + nextIncrement(entry))
      );
      cursor.classList.add("is-visible");
      state.timer = setTimeout(typeStep, nextDelay(entry));
      return;
    }

    state.entryIndex += 1;
    state.timer = setTimeout(typeStep, entry.kind === "meta" ? 260 : 180);
  };

  const startWriting = () => {
    clearTimer();
    clearTypedText();
    clearFocus();
    state.entryIndex = 0;
    state.isSettled = false;
    frame.classList.remove("is-settled");

    if (reduceMotion) {
      entries.forEach((entry) => {
        entry.element.textContent = entry.text;
      });
      setSettledState();
      return;
    }

    cursor.classList.add("is-visible");
    typeStep();
  };

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(startWriting);
  } else {
    window.addEventListener("load", startWriting, { once: true });
  }
}
