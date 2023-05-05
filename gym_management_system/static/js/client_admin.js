// document.addEventListener("DOMContentLoaded", function () {
//   const rows = document.querySelectorAll(".results tbody tr");

//   rows.forEach((row) => {
//     const membershipStatusCell = row.querySelector("td:nth-child(4)"); // Adjust this value if the membership status column changes

//     if (membershipStatusCell) {
//       const membershipStatus = membershipStatusCell.textContent.trim();

//       if (
//         membershipStatus === "no_membership" ||
//         membershipStatus === "expired"
//       ) {
//         row.style.backgroundColor = "#ff00001c";
//       } else if (membershipStatus === "expiring_soon") {
//         row.style.backgroundColor = "#ffff003b";
//       } else {
//         row.style.backgroundColor = "#00800021";
//       }
//     }
//   });
// });
document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll(".results tbody tr");

  rows.forEach((row) => {
    const membershipStatusCell = row.querySelector("td:nth-child(6)"); // Adjust this value if the membership status column changes
    console.log(membershipStatusCell);
    if (membershipStatusCell) {
      const membershipStatusIcon = membershipStatusCell.querySelector("span");
      const iconColor = membershipStatusIcon
        ? membershipStatusIcon.style.color
        : null;

      if (iconColor) {
        let colorWithOpacity;

        switch (iconColor) {
          case "red":
            colorWithOpacity = "rgba(255, 0, 0, 0.3)";
            break;
          case "yellow":
            colorWithOpacity = "rgba(255, 255, 0, 0.3)";
            break;
          case "green":
            colorWithOpacity = "rgba(0, 255, 0, 0.3)";
            break;
          default:
            colorWithOpacity = null;
        }

        if (colorWithOpacity) {
          row.style.backgroundColor = colorWithOpacity;
        }
      }
    }
  });
});
