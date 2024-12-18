let players = [];
let playerAvailability = {};
let selectedPlayers = {}; // To track selected players for each position

const positions = [
  "1 - Prop",
  "2 - Hooker",
  "3 - Prop",
  "4 - Second Row",
  "5 - Second Row",
  "6 - Flanker",
  "7 - Flanker",
  "8 - Number 8",
  "9 - Scrum Half",
  "10 - Fly Half",
  "11 - Wing",
  "12 - Centre",
  "13 - Centre",
  "14 - Wing",
  "15 - Full Back",
];

// Load players from the JSON file
document.addEventListener("DOMContentLoaded", () => {
  loadPlayers();
  generatePositionSelect();
  document
    .getElementById("save-availability")
    .addEventListener("click", saveAvailabilityToFile);

  document
    .getElementById("mark-all-available")
    .addEventListener("click", markAllAvailable);

  document
    .getElementById("mark-all-unavailable")
    .addEventListener("click", markAllUnavailable);

  document
    .getElementById("clear-selections")
    .addEventListener("click", clearSelections);

  document
    .getElementById("save-selection")
    .addEventListener("click", saveSelectionToFile);

  document
    .getElementById("copy-to-clipboard")
    .addEventListener("click", copyToClipboard);
});

// Load players from the JSON file
function loadPlayers() {
  fetch("players.json")
    .then((response) => response.json())
    .then((data) => {
      players = data;
      initializePlayerAvailability();
      renderPlayerList();
      renderPositionSelect(); // Call to render the dropdowns for positions
    })
    .catch((error) => {
      console.error("Error loading players:", error);
    });
}

function initializePlayerAvailability() {
  players.forEach((player, index) => {
    playerAvailability[index] = player.available || false; // Use actual availability
  });
}

function renderPlayerList() {
  // Sort players alphabetically by name
  players.sort((a, b) => a.name.localeCompare(b.name));

  const availablePlayersDiv = document.getElementById("available-players");
  const unavailablePlayersDiv = document.getElementById("unavailable-players");

  availablePlayersDiv.innerHTML = "";
  unavailablePlayersDiv.innerHTML = "";

  players.forEach((player, index) => {
    const playerDiv = document.createElement("div");
    playerDiv.className = `player-info ${
      player.available ? "available" : "unavailable"
    }`;

    playerDiv.innerHTML = `
      <div class="player-info">
        <button class="icon icon-edit" title="Edit player info" onclick="editPlayer(${index})">
            <i class="fas fa-pencil-alt"></i>
        </button>
        <span class="player-name">${player.name}</span>
        <button class="icon ${player.available ? "icon-x" : "icon-check"}" 
          title="${player.available ? "Mark unavailable" : "Mark available"}" 
          onclick="toggleAvailability(${index})">
            <i class="${player.available ? "fas fa-times" : "fas fa-check"}"></i>
        </button>
    </div>
    `;

    if (player.available) {
      availablePlayersDiv.appendChild(playerDiv);
    } else {
      unavailablePlayersDiv.appendChild(playerDiv);
    }
  });
}

function renderPositionSelect() {
  const positionSelectDiv = document.getElementById("position-select");

  // Save current selections
  const currentSelections = { ...selectedPlayers };

  // Define rows of positions
  const rows = [
    [1, 2, 3], // Row 1
    [6, 4, 5, 7], // Row 2
    [null, 8], // Row 3
    [9], // Row 4
    [10], // Row 5
    [12], // Row 6
    [13], // Row 7
    [11, null, null, null, 14], // Row 8
    [null, null, 15, null, null], // Row 9
  ];

  positionSelectDiv.innerHTML = ""; // Clear existing content

  rows.forEach((rowPositions, rowIndex) => {
    const rowDiv = document.createElement("div");
    rowDiv.className = `position-row row-${rowIndex + 1}`;

    rowPositions.forEach((positionNumber) => {
      const positionDiv = document.createElement("div");
      positionDiv.className = "position-cell";

      if (positionNumber) {
        const positionLabel = document.createElement("label");
        positionLabel.textContent = positions[positionNumber - 1];

        const positionSelect = document.createElement("select");
        positionSelect.id = `select-position-${positionNumber}`;

        // Add a placeholder option
        const placeholderOption = document.createElement("option");
        placeholderOption.value = "";
        placeholderOption.textContent = " - ";
        positionSelect.appendChild(placeholderOption);

        // Filter players: by position and exclude already selected
        const selectedPlayerIndices = Object.values(currentSelections);
        players.forEach((player, playerIndex) => {
          if (
            player.position.includes(
              positions[positionNumber - 1].split(" - ")[1]
            ) && // Matches position
            !selectedPlayerIndices.includes(playerIndex.toString()) // Not already selected
          ) {
            const option = document.createElement("option");
            option.value = playerIndex;
            option.textContent = player.name;

            // Preserve previously selected player for this position
            if (currentSelections[positionNumber] === playerIndex.toString()) {
              option.selected = true;
            }

            positionSelect.appendChild(option);
          }
        });

        // Event listener to track selections and re-render dropdowns
        positionSelect.addEventListener("change", () => {
          currentSelections[positionNumber] = positionSelect.value;
          selectedPlayers = { ...currentSelections }; // Update the global selections
          renderPositionSelect(); // Re-render dropdowns
        });

        positionDiv.appendChild(positionLabel);
        positionDiv.appendChild(positionSelect);
      }

      rowDiv.appendChild(positionDiv);
    });

    positionSelectDiv.appendChild(rowDiv);
  });

  renderReplacements(); // Render the replacements dropdowns
}

function renderReplacements() {
  const replacementsDiv = document.getElementById("replacements-row");
  replacementsDiv.innerHTML = ""; // Clear existing content

  // Save current selections
  const currentSelections = { ...selectedPlayers };

  [16, 17, 18].forEach((replacementNumber) => {
    const replacementCell = document.createElement("div");
    replacementCell.className = "position-cell";

    const replacementLabel = document.createElement("label");
    replacementLabel.textContent = `Replacement ${replacementNumber}`;

    const replacementSelect = document.createElement("select");
    replacementSelect.id = `select-replacement-${replacementNumber}`;

    // Add a placeholder option
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = " - ";
    replacementSelect.appendChild(placeholderOption);

    // Filter players: exclude already selected players
    const selectedPlayerIndices = Object.values(currentSelections);
    players.forEach((player, playerIndex) => {
      if (
        playerAvailability[playerIndex] && // Player is available
        !selectedPlayerIndices.includes(playerIndex.toString()) // Not already selected
      ) {
        const option = document.createElement("option");
        option.value = playerIndex;
        option.textContent = player.name;

        // Preserve previously selected player for this replacement
        if (currentSelections[replacementNumber] === playerIndex.toString()) {
          option.selected = true;
        }

        replacementSelect.appendChild(option);
      }
    });

    // Event listener to track selections and re-render dropdowns
    replacementSelect.addEventListener("change", () => {
      currentSelections[replacementNumber] = replacementSelect.value;
      selectedPlayers = { ...currentSelections }; // Update the global selections
      renderReplacements(); // Re-render the replacements dropdowns
    });

    replacementCell.appendChild(replacementLabel);
    replacementCell.appendChild(replacementSelect);
    replacementsDiv.appendChild(replacementCell);
  });
}


// Toggle player availability and persist dropdown selections
function toggleAvailability(index) {
  playerAvailability[index] = !playerAvailability[index];

  // Remove any invalid selections
  Object.keys(selectedPlayers).forEach((position) => {
    if (!playerAvailability[selectedPlayers[position]]) {
      delete selectedPlayers[position];
    }
  });

  renderPlayerList();
  renderPositionSelect();
}

function markAllAvailable() {
  players.forEach((_, index) => {
    playerAvailability[index] = true; // Mark all as available
  });

  renderPlayerList(); // Re-render the UI
  renderPositionSelect(); // Update dropdowns
}

function markAllUnavailable() {
  players.forEach((_, index) => {
    playerAvailability[index] = false; // Mark all as unavailable
  });

  renderPlayerList();
  renderPositionSelect();
}

function saveAvailabilityToFile() {
  const updatedPlayers = players.map((player, index) => ({
    ...player,
    available: playerAvailability[index] || false, // Add availability field
  }));

  const jsonData = JSON.stringify(updatedPlayers, null, 2);

  // Simulate file download
  const blob = new Blob([jsonData], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "players.json";
  a.click();
  URL.revokeObjectURL(url);

  alert("Availability saved to players.json!");
}

function clearSelections() {
  selectedPlayers = {}; // Reset selections
  renderPositionSelect(); // Re-render the dropdowns
  alert("All selections have been cleared!");
}


function saveSelectionToFile() {
  let teamSheet = generateTeamSheet();
  const blob = new Blob([teamSheet], { type: "text/plain" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "team-sheet.txt";
  a.click();
  URL.revokeObjectURL(url);

  alert("Team sheet saved to team-sheet.txt!");
}

function copyToClipboard() {
  let teamSheet = generateTeamSheet();
  navigator.clipboard.writeText(teamSheet).then(
    () => alert("Team sheet copied to clipboard!"),
    (err) => alert("Failed to copy to clipboard: " + err)
  );
}

function generateTeamSheet() {
  let teamSheet = "*1st XV Squad*\n";

  // Generate main squad positions
  Object.keys(selectedPlayers).forEach((position) => {
    const playerIndex = selectedPlayers[position];
    if (playerIndex !== undefined && playerIndex !== "" && playerIndex < 16) {
      const playerName = players[playerIndex].name;
      teamSheet += `${position} - ${playerName}\n`;
    }
  });

  // Generate replacements section
  teamSheet += "\n*Replacements*\n";
  [16, 17, 18].forEach((replacementNumber) => {
    const playerIndex = selectedPlayers[replacementNumber];
    if (playerIndex !== undefined && playerIndex !== "") {
      const playerName = players[playerIndex].name;
      teamSheet += `${replacementNumber} - ${playerName}\n`;
    }
  });

  return teamSheet.trim(); // Remove trailing newline
}


