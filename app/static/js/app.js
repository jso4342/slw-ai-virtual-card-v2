// Google Cloud x Seoul SLW Booth - AI Digital Business Card Generator JS

document.addEventListener("DOMContentLoaded", () => {
  // Form & Input Elements
  const cardForm = document.getElementById("cardForm");
  const btnSubmitForm = document.getElementById("btnSubmitForm");
  const inputName = document.getElementById("inputName");
  const inputCompany = document.getElementById("inputCompany");
  const inputRole = document.getElementById("inputRole");
  const inputCustomTag = document.getElementById("inputCustomTag");
  const btnAddTag = document.getElementById("btnAddTag");
  const keywordsGrid = document.getElementById("keywordsGrid");
  const themeCards = document.querySelectorAll(".theme-card");

  // Webcam Elements
  const btnStartWebcam = document.getElementById("btnStartWebcam");
  const btnSnapPhoto = document.getElementById("btnSnapPhoto");
  const btnRetakePhoto = document.getElementById("btnRetakePhoto");
  const webcamVideo = document.getElementById("webcamVideo");
  const webcamCanvas = document.getElementById("webcamCanvas");
  const photoCapturedImg = document.getElementById("photoCapturedImg");
  const webcamPlaceholder = document.getElementById("webcamPlaceholder");

  // Preview Card Elements
  const cardWrapper = document.getElementById("cardWrapper");
  const personaCard = document.getElementById("personaCard");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingStep = document.getElementById("loadingStep");

  const cardQrImg = document.getElementById("cardQrImg");
  const btnNewCard = document.getElementById("btnNewCard");

  // State: Dynamically gather active tag values and active theme from DOM
  let selectedKeywords = Array.from(document.querySelectorAll(".tag-btn.active")).map(btn => btn.dataset.value);
  let selectedTheme = document.querySelector(".theme-card.active")?.dataset.theme || "hangang";
  let capturedPhotoBase64 = null;
  let mediaStream = null;
  let currentCardId = "";
  let isComposingHangul = false;

  // 1. Keyword Tag Selection & Custom Tag Addition
  function attachTagEvents(tag) {
    tag.addEventListener("click", () => {
      const val = tag.dataset.value;
      if (tag.classList.contains("active")) {
        tag.classList.remove("active");
        selectedKeywords = selectedKeywords.filter(k => k !== val);
      } else {
        if (selectedKeywords.length >= 6) {
          alert("You can select up to 6 lifestyle keywords!");
          return;
        }
        tag.classList.add("active");
        if (!selectedKeywords.includes(val)) {
          selectedKeywords.push(val);
        }
      }
    });
  }

  document.querySelectorAll(".tag-btn").forEach(attachTagEvents);

  function handleAddCustomTag() {
    const customVal = inputCustomTag.value.trim();
    if (!customVal) return;

    if (selectedKeywords.length >= 6) {
      alert("You can select up to 6 lifestyle keywords.");
      return;
    }

    if (selectedKeywords.includes(customVal)) {
      inputCustomTag.value = "";
      return;
    }

    const newTag = document.createElement("span");
    newTag.className = "tag-btn active custom-user-tag";
    newTag.dataset.value = customVal;
    newTag.innerHTML = `✨ ${customVal}`;
    attachTagEvents(newTag);

    keywordsGrid.appendChild(newTag);
    selectedKeywords.push(customVal);

    inputCustomTag.value = "";
    inputCustomTag.blur();
    setTimeout(() => {
      inputCustomTag.value = "";
      inputCustomTag.focus();
    }, 15);
  }

  btnAddTag.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleAddCustomTag();
  });

  inputCustomTag.addEventListener("compositionstart", () => {
    isComposingHangul = true;
  });

  inputCustomTag.addEventListener("compositionend", () => {
    isComposingHangul = false;
  });

  inputCustomTag.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      if (e.isComposing || isComposingHangul || e.keyCode === 229) {
        return;
      }
      e.preventDefault();
      e.stopPropagation();
      handleAddCustomTag();
      return false;
    }
  });

  // 2. Theme Selector Logic
  themeCards.forEach(theme => {
    theme.addEventListener("click", () => {
      themeCards.forEach(t => t.classList.remove("active"));
      theme.classList.add("active");
      selectedTheme = theme.dataset.theme;
      personaCard.className = `persona-card theme-${selectedTheme}`;
    });
  });

  // 3. Webcam Capture Functionality
  btnStartWebcam.addEventListener("click", async () => {
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 640 }, facingMode: "user" }
      });
      webcamVideo.srcObject = mediaStream;
      webcamVideo.style.display = "block";
      webcamPlaceholder.style.display = "none";
      photoCapturedImg.style.display = "none";

      btnStartWebcam.style.display = "none";
      btnSnapPhoto.style.display = "inline-flex";
      btnRetakePhoto.style.display = "none";
    } catch (err) {
      console.error(err);
      alert("Unable to access camera. (A default 3D avatar will be generated instead).");
    }
  });

  btnSnapPhoto.addEventListener("click", () => {
    if (!mediaStream) return;

    webcamCanvas.width = webcamVideo.videoWidth || 400;
    webcamCanvas.height = webcamVideo.videoHeight || 400;
    const ctx = webcamCanvas.getContext("2d");
    ctx.drawImage(webcamVideo, 0, 0, webcamCanvas.width, webcamCanvas.height);

    capturedPhotoBase64 = webcamCanvas.toDataURL("image/jpeg", 0.85);

    photoCapturedImg.src = capturedPhotoBase64;
    photoCapturedImg.style.display = "block";
    webcamVideo.style.display = "none";

    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
    }

    btnSnapPhoto.style.display = "none";
    btnRetakePhoto.style.display = "inline-flex";
  });

  btnRetakePhoto.addEventListener("click", () => {
    capturedPhotoBase64 = null;
    photoCapturedImg.style.display = "none";
    btnStartWebcam.click();
  });

  // 4. 3D Card Tilt Effect
  if (cardWrapper) {
    cardWrapper.addEventListener("mousemove", (e) => {
      const rect = cardWrapper.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      const rotateX = (-y / rect.height) * 20;
      const rotateY = (x / rect.width) * 20;

      personaCard.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    cardWrapper.addEventListener("mouseleave", () => {
      personaCard.style.transform = "rotateX(0deg) rotateY(0deg)";
    });
  }

  // 5. Submit Form -> Call Gemini AI API
  async function submitCardForm() {
    const name = inputName.value.trim();
    const company = inputCompany.value.trim();
    const roleVal = inputRole.value.trim();
    const email = document.getElementById("inputEmail").value.trim();
    const phone = document.getElementById("inputPhone").value.trim();
    const marketingConsent = document.getElementById("inputConsent").checked;

    if (!name || !company || !roleVal) {
      alert("Please fill in your Name, Company, and Role.");
      return;
    }

    if (!marketingConsent) {
      alert("⚠️ Please agree to the personal data processing terms to generate your AI business card.");
      document.getElementById("inputConsent").focus();
      return;
    }

    loadingOverlay.classList.add("active");
    loadingStep.textContent = "Connecting to Google Cloud Gemini Engine...";

    const steps = [
      "Analyzing facial features and style preferences...",
      "Rendering personalized 3D avatar artwork...",
      "Finalizing digital card assets & QR code..."
    ];

    let stepIdx = 0;
    const interval = setInterval(() => {
      if (stepIdx < steps.length) {
        loadingStep.textContent = steps[stepIdx];
        stepIdx++;
      }
    }, 700);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          company,
          role: roleVal,
          email,
          phone,
          lifestyle: selectedKeywords,
          theme: document.querySelector(".theme-card.active")?.dataset.theme || selectedTheme || "hangang",
          photo_base64: capturedPhotoBase64,
          marketing_consent: marketingConsent
        })
      });

      const data = await res.json().catch(() => ({ success: false, error: `Server error (HTTP ${res.status})` }));
      clearInterval(interval);
      loadingOverlay.classList.remove("active");

      if (res.ok && data.success && data.card) {
        renderCard(data.card);
        triggerConfetti();
      } else {
        alert("Card Generation Failed: " + (data.error || `Unknown error (HTTP ${res.status})`));
      }
    } catch (err) {
      clearInterval(interval);
      loadingOverlay.classList.remove("active");
      console.error(err);
      alert("Network Error: " + (err.message || "Please check your network connection."));
    }
  }

  btnSubmitForm.addEventListener("click", submitCardForm);

  // 6. Render Generated Card
  function renderCard(card) {
    currentCardId = card.id;

    const generatedCardImageWrapper = document.getElementById("generatedCardImageWrapper");
    const generatedCardImg = document.getElementById("generatedCardImg");
    const defaultCardTextWrapper = document.getElementById("defaultCardTextWrapper");
    const cardHeaderRow = document.getElementById("cardHeaderRow");

    if (card.avatar_image && generatedCardImg && generatedCardImageWrapper) {
      generatedCardImg.src = card.avatar_image;
      generatedCardImageWrapper.style.display = "block";
      if (defaultCardTextWrapper) defaultCardTextWrapper.style.display = "none";
      if (cardHeaderRow) cardHeaderRow.style.display = "none";

      personaCard.style.padding = "0";
      personaCard.style.background = "transparent";
      personaCard.style.border = "none";
      personaCard.style.boxShadow = "none";
    }

    // Theme update
    personaCard.className = `persona-card theme-${card.theme}`;

    // Show QR Code & Action buttons ONLY AFTER Card Generation
    const cardFooterRow = document.getElementById("cardFooterRow");
    if (cardFooterRow) {
      cardFooterRow.style.display = "flex";
      if (cardQrImg) cardQrImg.src = `/api/qr/${card.id}`;
    }

    const btnPrintCard = document.getElementById("btnPrintCard");
    if (btnPrintCard) btnPrintCard.style.display = "flex";

    if (btnNewCard) btnNewCard.style.display = "flex";
  }

  // 7. Print Business Card
  const btnPrintCard = document.getElementById("btnPrintCard");
  if (btnPrintCard) {
    btnPrintCard.addEventListener("click", () => {
      window.print();
    });
  }

  // 8. Reset / New Card
  if (btnNewCard) {
    btnNewCard.addEventListener("click", () => {
      // Form reset
      cardForm.reset();

      // Remove custom user tags added dynamically
      document.querySelectorAll(".custom-user-tag").forEach(el => el.remove());

      // Reset all remaining tag buttons (deactivate all tags)
      document.querySelectorAll(".tag-btn").forEach(btn => btn.classList.remove("active"));
      selectedKeywords = [];

      // Clear custom tag input
      if (inputCustomTag) inputCustomTag.value = "";

      // Clear webcam capture state
      capturedPhotoBase64 = null;
      photoCapturedImg.style.display = "none";
      webcamVideo.style.display = "none";
      webcamPlaceholder.style.display = "block";

      btnStartWebcam.style.display = "inline-flex";
      btnSnapPhoto.style.display = "none";
      btnRetakePhoto.style.display = "none";

      // Reset preview card layout
      const generatedCardImageWrapper = document.getElementById("generatedCardImageWrapper");
      const defaultCardTextWrapper = document.getElementById("defaultCardTextWrapper");
      const cardHeaderRow = document.getElementById("cardHeaderRow");
      const cardFooterRow = document.getElementById("cardFooterRow");

      if (generatedCardImageWrapper) generatedCardImageWrapper.style.display = "none";
      if (defaultCardTextWrapper) defaultCardTextWrapper.style.display = "block";
      if (cardHeaderRow) cardHeaderRow.style.display = "flex";
      if (cardFooterRow) cardFooterRow.style.display = "none";

      personaCard.style.padding = "1.5rem";
      personaCard.style.background = "";
      personaCard.className = "persona-card theme-seoul";

      if (btnPrintCard) btnPrintCard.style.display = "none";
      btnNewCard.style.display = "none";

      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }

      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // 9. Confetti Celebration
  function triggerConfetti() {
    if (typeof confetti === "function") {
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
    }
  }
});
