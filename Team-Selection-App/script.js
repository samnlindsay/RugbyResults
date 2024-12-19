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

  document
    .getElementById("player-container")
    .addEventListener("click", (event) => {
      const target = event.target;
      if (target.classList.contains("icon-edit")) {
        const playerId = target.closest(".player-info").dataset.id;
        editPlayer(playerId);
      } else if (target.classList.contains("icon-check")) {
        const playerId = target.closest(".player-info").dataset.id;
        toggleAvailability(playerId, true);
      } else if (target.classList.contains("icon-x")) {
        const playerId = target.closest(".player-info").dataset.id;
        toggleAvailability(playerId, false);
      }
    });

    document
      .getElementById("position-select")
      .addEventListener("change", (event) => {
        const target = event.target;
        if (target.tagName === "SELECT") {
          const position = target.id.replace("select-position-", ""); // Extract position name
          const playerIndex = target.value; // Get selected player index
          selectedPlayers[position] = playerIndex; // Update selectedPlayers
        }
      });


});

// Edit player name and positions (display current name/positions as default)
function editPlayer(index) {
  const player = players[index];
  const updatedName = prompt("Enter player name:", player.name);
  const updatedPositions = prompt(
    "Enter player positions (comma-separated):",
    player.position.join(", ")
  );

  if (updatedName !== null && updatedPositions !== null) {
    players[index] = {
      ...player,
      name: updatedName,
      position: updatedPositions.split(",").map((pos) => pos.trim()),
    };

    renderPlayerList();
    renderPositionSelect();
  }
}


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
  positionSelectDiv.innerHTML = ""; // Clear existing content

  // Predefined numbers for each position
  const positionNumbers = {
    Prop: [1, 3],
    Hooker: [2],
    Flanker: [6, 7],
    "Second Row": [4, 5],
    "Number 8": [8],
    "Scrum Half": [9],
    "Fly Half": [10],
    Centre: [12, 13],
    Wing: [11, 14],
    "Full Back": [15],
  };

  // Track used numbers to avoid duplication
  const usedNumbers = new Set();

  const rows = [
    ["Prop", "Hooker", "Prop"],
    ["Flanker", "Second Row", "Second Row", "Flanker"],
    ["Number 8"],
    [null, "Scrum Half"],
    [null, "Fly Half"],
    [null, "Centre", "Centre"],
    ["Wing", null, null, null, null, "Wing"],
    ["Full Back"],
  ];

  const getNextAvailableNumber = (position) => {
    const availableNumbers = positionNumbers[position].filter(
      (num) => !usedNumbers.has(num)
    );
    return availableNumbers.length > 0 ? availableNumbers[0] : null;
  };

  rows.forEach((rowPositions, rowIndex) => {
    const rowDiv = document.createElement("div");
    rowDiv.className = `position-row row-${rowIndex + 1}`;

    rowPositions.forEach((positionName) => {
      const positionDiv = document.createElement("div");
      positionDiv.className = "position-cell";

      if (positionName) {
        const assignedNumber = getNextAvailableNumber(positionName);

        if (assignedNumber !== null) {
          usedNumbers.add(assignedNumber); // Mark number as used

          const positionHeader = document.createElement("div");
          positionHeader.className = "position-header";

          const positionNumberLabel = document.createElement("span");
          positionNumberLabel.textContent = assignedNumber;
          positionNumberLabel.className = "position-number";

          const positionLabel = document.createElement("span");
          positionLabel.textContent = positionName;
          positionLabel.className = "position-label";

          positionHeader.appendChild(positionNumberLabel);
          positionHeader.appendChild(positionLabel);

          const positionSelect = document.createElement("select");
          positionSelect.id = `select-position-${assignedNumber}`;

          const placeholderOption = document.createElement("option");
          placeholderOption.value = "";
          placeholderOption.textContent = " - ";
          positionSelect.appendChild(placeholderOption);

          players.forEach((player, playerIndex) => {
            if (
              player.available &&
              player.position.includes(positionName) &&
              !Object.values(selectedPlayers).includes(playerIndex.toString())
            ) {
              const option = document.createElement("option");
              option.value = playerIndex;
              option.textContent = player.name;

              if (selectedPlayers[assignedNumber] === playerIndex.toString()) {
                option.selected = true;
              }

              positionSelect.appendChild(option);
            }
          });

          positionSelect.addEventListener("change", (event) => {
            const selectedPlayerIndex = event.target.value;
            selectedPlayers[assignedNumber] = selectedPlayerIndex; // Assign player to the number
          });

          positionDiv.appendChild(positionHeader);
          positionDiv.appendChild(positionSelect);
        } else {
          console.warn(
            `No available numbers left for position: ${positionName}`
          );
        }
      } else {
        positionDiv.classList.add("empty");
      }

      rowDiv.appendChild(positionDiv);
    });

    positionSelectDiv.appendChild(rowDiv);
  });

  // Handle replacements (16, 17, 18)
  const replacementsSelectDiv = document.getElementById("replacements-select");
  replacementsSelectDiv.innerHTML = ""; // Clear existing content

  const replacementsDiv = document.createElement("div");
  replacementsDiv.className = "replacements-row";

  [16, 17, 18].forEach((replacementNumber) => {
    const replacementDiv = document.createElement("div");
    replacementDiv.className = "replacement-cell";

    const positionNumberLabel = document.createElement("span");
    positionNumberLabel.textContent = replacementNumber;
    positionNumberLabel.className = "replacement-number";

    const positionSelect = document.createElement("select");
    positionSelect.id = `select-replacement-${replacementNumber}`;

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = " - ";
    positionSelect.appendChild(placeholderOption);

    players.forEach((player, playerIndex) => {
      if (
        player.available &&
        !Object.values(selectedPlayers).includes(playerIndex.toString())
      ) {
        const option = document.createElement("option");
        option.value = playerIndex;
        option.textContent = player.name;

        if (selectedPlayers[replacementNumber] === playerIndex.toString()) {
          option.selected = true;
        }

        positionSelect.appendChild(option);
      }
    });

    positionSelect.addEventListener("change", (event) => {
      const selectedPlayerIndex = event.target.value;
      selectedPlayers[replacementNumber] = selectedPlayerIndex; // Assign player to replacement
    });

    replacementDiv.appendChild(positionNumberLabel);
    replacementDiv.appendChild(positionSelect);
    replacementsDiv.appendChild(replacementDiv);
  });

  replacementsSelectDiv.appendChild(replacementsDiv);
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
  players[index].available = playerAvailability[index]; // Keep in sync

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
    players[index].available = true; // Keep in sync
  });
  renderPlayerList(); // Re-render the UI
  renderPositionSelect(); // Update dropdowns
}

function markAllUnavailable() {
  players.forEach((_, index) => {
    playerAvailability[index] = false; // Mark all as unavailable
    players[index].available = false; // Keep in sync
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

  // Main squad positions (1–15)
  for (let number = 1; number <= 15; number++) {
    const playerIndex = selectedPlayers[number];
    if (playerIndex !== undefined && playerIndex !== "") {
      const playerName = players[playerIndex].name;
      teamSheet += `${number}. ${playerName}\n`;
    } else {
      teamSheet += `${number}. [Unselected]\n`;
    }
  }

  // Replacements (16–18)
  teamSheet += "\n*Replacements*\n";
  for (let number = 16; number <= 18; number++) {
    const playerIndex = selectedPlayers[number];
    if (playerIndex !== undefined && playerIndex !== "") {
      const playerName = players[playerIndex].name;
      teamSheet += `${number}. ${playerName}\n`;
    } else {
      teamSheet += `${number}. [Unselected]\n`;
    }
  }

  return teamSheet.trim(); // Ensure no trailing newline
}
