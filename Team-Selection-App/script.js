let players = [];
let playerAvailability = {};
let selectedPlayers = {}; // To track selected players for each position

const positionMapping = {
  "Prop": [1, 3], // Player numbers 1 and 3 are both Props
  "Hooker": [2], // Player number 2 is Hooker
  "Second Row": [4, 5], // Player numbers 4 and 5 are Second Rows
  "Flanker": [6, 7], // Player numbers 6 and 7 are Flankers
  "Number 8": [8], // Player number 8 is Number 8
  "Scrum Half": [9], // Player number 9 is Scrum Half
  "Fly Half": [10], // Player number 10 is Fly Half
  "Wing": [11, 14], // Player numbers 11 and 14 are Wings
  "Centre": [12, 13], // Player numbers 12 and 13 are Centres
  "Full Back": [15], // Player number 15 is Full Back
};



// Load players from the JSON file
document.addEventListener("DOMContentLoaded", () => {
  loadPlayers();
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

function renderPositionSelect() {
  const positionSelectDiv = document.getElementById("position-select");

  // Define rows of positions, including a separate section for replacements
  const rows = [
    ["Prop", "Hooker", "Prop"], // Row 1
    ["Flanker", "Second Row", "Second Row", "Flanker"], // Row 2
    ["Number 8"], // Row 3
    ["Scrum Half"], // Row 4
    ["Fly Half"], // Row 5
    ["Centre"], // Row 6
    ["Centre"], // Row 7
    ["Wing", null, null, null, "Wing"], // Row 8
    ["Full Back"], // Row 9
  ];

  positionSelectDiv.innerHTML = ""; // Clear existing content

  // Collect all selected players in a set for filtering
  const selectedPlayerIndices = new Set(Object.values(selectedPlayers));

  // Render main positions (1-15)
  rows.forEach((rowPositions, rowIndex) => {
    const rowDiv = document.createElement("div");
    rowDiv.className = `position-row row-${rowIndex + 1}`;

    rowPositions.forEach((positionName) => {
      const positionDiv = document.createElement("div");
      positionDiv.className = "position-cell";

      if (positionName) {
        const positionLabel = document.createElement("label");
        positionLabel.textContent = positionName;

        const positionSelect = document.createElement("select");
        positionSelect.id = `select-position-${positionName}`;

        const placeholderOption = document.createElement("option");
        placeholderOption.value = "";
        placeholderOption.textContent = " - ";
        positionSelect.appendChild(placeholderOption);

        const playerNumbersForPosition = positionMapping[positionName];
        players.forEach((player, playerIndex) => {
          if (
            player.available &&
            player.position.includes(positionName) &&
            !selectedPlayerIndices.has(playerIndex.toString()) // Ensure player isn't already selected
          ) {
            const option = document.createElement("option");
            option.value = playerIndex;
            option.textContent = player.name;

            // If player was previously selected for this position, mark it as selected
            if (selectedPlayers[positionName] === playerIndex.toString()) {
              option.selected = true;
            }

            positionSelect.appendChild(option);
          }
        });

        positionDiv.appendChild(positionLabel);
        positionDiv.appendChild(positionSelect);
      } else {
        positionDiv.classList.add("empty");
      }

      rowDiv.appendChild(positionDiv);
    });

    positionSelectDiv.appendChild(rowDiv);
  });

  // Now handle replacements (players 16, 17, 18)
  const replacementsDiv = document.createElement("div");
  replacementsDiv.className = "position-row replacements";

  // Render replacement player dropdowns (16, 17, 18)
  [16, 17, 18].forEach((replacementNumber) => {
    const replacementDiv = document.createElement("div");
    replacementDiv.className = "position-cell replacement";

    const positionLabel = document.createElement("label");
    positionLabel.textContent = replacementNumber;

    const positionSelect = document.createElement("select");
    positionSelect.id = `select-replacement-${replacementNumber}`;

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = " - ";
    positionSelect.appendChild(placeholderOption);

    const availablePlayersForReplacement = players.filter(
      (player, playerIndex) => {
        return (
          player.available &&
          !selectedPlayerIndices.has(playerIndex.toString()) && // Ensure not already selected for a starting position
          !positionMapping["Prop"].includes(playerIndex + 1) && // Make sure not already selected for a starting 15 position
          playerIndex + 1 !== replacementNumber // Exclude this replacement from being selected for itself
        );
      }
    );

    availablePlayersForReplacement.forEach((player, playerIndex) => {
      const option = document.createElement("option");
      option.value = playerIndex;
      option.textContent = player.name;

      if (selectedPlayers[replacementNumber] === playerIndex.toString()) {
        option.selected = true;
      }

      positionSelect.appendChild(option);
    });

    replacementDiv.appendChild(positionLabel);
    replacementDiv.appendChild(positionSelect);
    replacementsDiv.appendChild(replacementDiv);
  });

  positionSelectDiv.appendChild(replacementsDiv);
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
            <i class="${
              player.available ? "fas fa-times" : "fas fa-check"
            }"></i>
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

// Ensure clearSelections() only resets the UI, not the selected players
function clearSelections() {
  // You can reset the dropdowns and render the UI without resetting selectedPlayers
  renderPositionSelect();
  alert(
    "All selections have been cleared! (Selections remain intact in the code.)"
  );
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
