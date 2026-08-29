// Minimal drag-and-drop for the two upload zones. Each zone wraps a hidden
// <input type="file">; dropping a file (or clicking to browse) sets that
// input's files so the existing form submits it normally.
document.querySelectorAll(".dropzone").forEach((zone) => {
  const input = zone.querySelector('input[type="file"]');
  const filenameLabel = zone.querySelector(".dropzone-filename");

  const showFilename = () => {
    if (input.files && input.files.length > 0) {
      filenameLabel.textContent = input.files[0].name;
    }
  };

  zone.addEventListener("click", () => input.click());
  input.addEventListener("change", showFilename);

  ["dragenter", "dragover"].forEach((evt) =>
    zone.addEventListener(evt, (e) => {
      e.preventDefault();
      zone.classList.add("dragover");
    })
  );

  ["dragleave", "drop"].forEach((evt) =>
    zone.addEventListener(evt, (e) => {
      e.preventDefault();
      zone.classList.remove("dragover");
    })
  );

  zone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      input.files = files;
      showFilename();
    }
  });
});
