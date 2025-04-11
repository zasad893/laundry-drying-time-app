// static/script.js

let selectedLocation = { address: "", lat: null, lng: null };

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
    });
}

function formatRange(baseMinutes) {
  const min = Math.floor(baseMinutes);
  const max = Math.floor(baseMinutes + 30);
  const format = (m) => `${Math.floor(m / 60)} hr ${m % 60} mins`;
  return `${format(min)} to ${format(max)}`;
}

function displayResults() {
  const resultData = localStorage.getItem("result");

  if (!resultData) {
    document.getElementById("resultsBox").innerHTML = `
      <p class="card error">No prediction data found. Please return to the home page and try again.</p>
    `;
    return;
  }

  let data;
  try {
    data = JSON.parse(resultData);
  } catch (e) {
    document.getElementById("resultsBox").innerHTML = `
      <p class="card error">Failed to parse prediction data. Please try again later.</p>
    `;
    return;
  }

  const weatherDiv = document.getElementById("weatherCards");
  const predictionDiv = document.getElementById("predictionCards");

  if (!data.weather) {
    weatherDiv.innerHTML = `<div class='card error'>Weather data not available.</div>`;
    return;
  }

  const isRaining = data.weather.precip > 0.1;

  weatherDiv.innerHTML = `
    <div class="card metric"><strong>Temperature:</strong><br>${data.weather.temperature}&deg;C</div>
    <div class="card metric"><strong>Cloud Cover:</strong><br>${data.weather.cloud}%</div>
    <div class="card metric"><strong>Wind Speed:</strong><br>${data.weather.wind} mph</div>
    <div class="card metric"><strong>Rain Status:</strong><br>${isRaining ? "Rain is expected or ongoing." : "It is safe to dry clothes outside."}</div>
  `;

  if (isRaining) {
    predictionDiv.innerHTML = `
      <div class="card prediction warning">
        <strong>Notice:</strong><br>It is currently raining. Outdoor drying is not recommended. Please check again later.
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
    predictionDiv.innerHTML = `
      <div class="card error">Prediction data is missing. Please try again later.</div>
    `;
  }
}

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
