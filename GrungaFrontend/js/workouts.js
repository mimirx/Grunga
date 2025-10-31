document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("workout-form");
  const typeSelect = document.getElementById("type");
  const durationSection = document.getElementById("duration-section");
  const repsSection = document.getElementById("reps-section");
  const list = document.querySelector("#workout-list ul");

  // input fields based on workout type
  typeSelect.addEventListener("change", () => {
    const type = typeSelect.value;

    if (["run", "bike", "walk", "swim"].includes(type)) {
      durationSection.style.display = "block";
      repsSection.style.display = "none";
    } else if (["pushups", "squats", "lunges", "crunches"].includes(type)) {
      repsSection.style.display = "block";
      durationSection.style.display = "none";
    } else {
      repsSection.style.display = "none";
      durationSection.style.display = "none";
    }
  });


  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const type = typeSelect.value;
    let points = 0;
    let details = "";

    if (["run", "bike", "walk", "swim"].includes(type)) {
      const duration = parseInt(document.getElementById("duration").value);
      if (!duration || duration <= 0) return alert("Enter workout duration!");
      let multiplier = 1;
      if (type === "run" || type === "swim") multiplier = 2;
      else if (type === "bike" || type === "walk") multiplier = 1.5;
      points = duration * multiplier;
      details = `${duration} mins`;
    } else {
      const reps = parseInt(document.getElementById("reps").value);
      if (!reps || reps <= 0) return alert("Enter number of reps!");
      points = reps * 1; // x1 for bodyweight workouts
      details = `${reps} reps`;
    }

    const li = document.createElement("li");
    li.textContent = `${type.charAt(0).toUpperCase() + type.slice(1)} — ${details} → ${points} pts`;
    list.appendChild(li);

    form.reset();
    durationSection.style.display = "none";
    repsSection.style.display = "none";
  });
});
