// static/script.js

let selectedLocation = { address: "", lat: null, lng: null };

// Google Maps Autocomplete
function initAutocomplete() {
  const autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("autocomplete")
  );
  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();
    if (!place.geometry) return;
    selectedLocation.address = place.formatted_address || place.name;
    selectedLocation.lat = place.geometry.location.lat();
    selectedLocation.lng = place.geometry.location.lng();
  });
}

// Get location from device
function useMyLocation() {
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const lat = pos.coords.latitude;
    const lng = pos.coords.longitude;
    selectedLocation.lat = lat;
    selectedLocation.lng = lng;

    const res = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=AIzaSyD_e586xKwm-WdtAArTRz-zkQLabOGYiV4`
    );
    const data = await res.json();
    if (data.results && data.results.length > 0) {
      const address = data.results[0].formatted_address;
      document.getElementById("autocomplete").value = address;
      selectedLocation.address = address;
    }
  });
}

// Submit location and get prediction
function handleFormSubmit(e) {
  e.preventDefault();

  if (!selectedLocation.address) {
    selectedLocation.address = document.getElementById("autocomplete").value;
  }

  fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      location: selectedLocation.address,
      lat: selectedLocation.lat,
      lng: selectedLocation.lng,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      localStorage.setItem("result", JSON.stringify(data));
      window.location.href = "/result";
    })
    .catch((err) => {
      alert("Something went wrong. Try again later.");
      console.error(err);
    });
}

// Format drying time into readable range
function formatRange(baseMinutes) {
  const min = Math.floor(baseMinutes);
  const max = Math.floor(baseMinutes + 30);
  const format = (m) => `${Math.floor(m / 60)} hr ${m % 60} mins`;
  return `${format(min)} to ${format(max)}`;
}

// Show results page content
function displayResults() {
  const resultData = localStorage.getItem("result");
  if (!resultData) {
    document.getElementById("resultsBox").innerHTML =
      "<p class='card error'>No prediction data found. Please return to the home page.</p>";
    return;
  }

  let data;
  try {
    data = JSON.parse(resultData);
  } catch {
    document.getElementById("resultsBox").innerHTML =
      "<p class='card error'>Error parsing result data.</p>";
    return;
  }

  const weatherDiv = document.getElementById("weatherCards");
  const predictionDiv = document.getElementById("predictionCards");

  if (!data.weather) {
    weatherDiv.innerHTML = "<div class='card error'>No weather data.</div>";
    return;
  }

  const isRaining = data.weather.precip > 0.1;

  weatherDiv.innerHTML = `
    <div class="card metric"><strong>Temperature:</strong><br>${data.weather.temperature}°C</div>
    <div class="card metric"><strong>Cloud Cover:</strong><br>${data.weather.cloud}%</div>
    <div class="card metric"><strong>Wind Speed:</strong><br>${data.weather.wind} mph</div>
    <div class="card metric"><strong>Rain Status:</strong><br>${isRaining ? "Rain expected" : "Safe for drying"}</div>
  `;

  if (isRaining) {
    predictionDiv.innerHTML = `
      <div class="card prediction warning">
        <strong>Notice:</strong><br>It is currently raining. Outdoor drying is not recommended.
      </div>
    `;
  } else if (data.prediction) {
    predictionDiv.innerHTML = `
      <div class="card prediction">
        <strong>Light Fabric Drying Time:</strong><br>${formatRange(data.prediction.tshirt_minutes)}
      </div>
      <div class="card prediction">
        <strong>Heavy Fabric Drying Time:</strong><br>${formatRange(data.prediction.towel_minutes)}
      </div>
    `;
  } else {
    predictionDiv.innerHTML =
      "<div class='card error'>No drying predictions available.</div>";
  }
}

// Run on page load
window.onload = () => {
  if (document.getElementById("locationForm")) {
    initAutocomplete();
    document
      .getElementById("locationForm")
      .addEventListener("submit", handleFormSubmit);
  }
  if (document.getElementById("resultsBox")) {
    displayResults();
  }
};
