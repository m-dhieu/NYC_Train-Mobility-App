// -----------------------------------------------------------------------------------------  
// Script Name: main.js  
// Description: Defines functionalities for the NYC Train Mobility Dashboard.  
//              Connects the frontend UI components to backend APIs to fetch and render trip  
//              summaries, tables, and various charts such as trip counts over time, duration  
//              histograms, and pickup heatmaps. Also manages interactive sliders with custom  
//              gradient colors for filtering data by distance and fare.  
// Author:      Thierry Gabin  
// Date:        2025-10-16  
// -----------------------------------------------------------------------------------------  

document.addEventListener("DOMContentLoaded", function () {
  // Get slider elements for distance and fare, and their corresponding display value elements
  const distanceSlider = document.getElementById("distance");
  const distanceValue = document.getElementById("distance-value");
  const fareSlider = document.getElementById("fare");
  const fareValue = document.getElementById("fare-value");

  // Update slider background with a linear gradient color based on distance value
  // Gradient transitions: green → yellow → orange → red, depending on slider percentage value
  function updateLinearSliderColor(slider) {
    const value = Number(slider.value);
    const max = Number(slider.max);
    const percent = (value / max) * 100;

    let color;
    // Apply color stops dynamically per percentage thresholds
    if (percent < 33) {
      color = `linear-gradient(to right, green 0%, yellow ${percent}%, #ddd ${percent}%, #ddd 100%)`;
    } else if (percent < 66) {
      color = `linear-gradient(to right, green 0%, yellow 33%, orange ${percent}%, #ddd ${percent}%, #ddd 100%)`;
    } else {
      color = `linear-gradient(to right, green 0%, yellow 33%, orange 66%, red ${percent}%, #ddd ${percent}%, #ddd 100%)`;
    }
    slider.style.background = color;
  }

  // Update slider background with a linear gradient color based on fare value
  // Similar gradient pattern to distance slider, enhancing UI feedback for fare filtering
  function updateReverseSliderColor(slider) {
    const value = Number(slider.value);
    const max = Number(slider.max);
    const percent = (value / max) * 100;

    let color;
    // Dynamic gradient stops for visual clarity
    if (percent < 33) {
      color = `linear-gradient(to right, green 0%, yellow ${percent}%, #ddd ${percent}%, #ddd 100%)`;
    } else if (percent < 66) {
      color = `linear-gradient(to right, green 0%, yellow 33%, orange ${percent}%, #ddd ${percent}%, #ddd 100%)`;
    } else {
      color = `linear-gradient(to right, green 0%, yellow 33%, orange 66%, red ${percent}%, #ddd ${percent}%, #ddd 100%)`;
    }
    slider.style.background = color;
  }

  // Event listener for distance slider input: update displayed value and slider color dynamically
  distanceSlider.oninput = function () {
    distanceValue.textContent = this.value;
    updateLinearSliderColor(this);
  };

  // Event listener for fare slider input: update displayed value and slider color dynamically
  fareSlider.oninput = function () {
    fareValue.textContent = this.value;
    updateReverseSliderColor(this);
  };

  // Initialize slider colors on page load to reflect initial values
  updateLinearSliderColor(distanceSlider);
  updateReverseSliderColor(fareSlider);

  // Attach click handler to 'Apply Filters' button to trigger data fetching and UI update
  document.getElementById("apply-filters").onclick = function () {
    fetchAndUpdate();
  };

  // Build query parameter string from current filter values for API requests
  function buildQueryParams() {
    const date = document.getElementById("date").value;
    const hour = document.getElementById("time").value;
    const distance = distanceSlider.value;
    const zone = document.getElementById("zone").value;
    const fare = fareSlider.value;

    let params = [];
    if (date) params.push(`date=${encodeURIComponent(date)}`); // Encode dates for URL safety
    if (hour) params.push(`hour=${hour}`);
    if (distance) params.push(`distance=${distance}`);
    if (zone) params.push(`zone=${encodeURIComponent(zone)}`);
    if (fare) params.push(`fare=${fare}`);
    // Return concatenated query string or empty if no filters applied
    return params.length ? "?" + params.join("&") : "";
  }

  // Fetch all relevant data from backend API endpoints and update UI components accordingly
  function fetchAndUpdate() {
    const params = buildQueryParams();

    // Fetch summary statistics like total trips, average duration, busiest hour
    fetch(`/api/trips/summary${params}`)
      .then(res => res.json())
      .then(data => {
        document.getElementById("trip-count").textContent = `Trips: ${data.total_trips}`;
        document.getElementById("avg-duration").textContent = `Avg Duration: ${data.avg_duration_sec} sec`;
        document.getElementById("busiest-hour").textContent = `Busiest Hour: ${data.busiest_hour}`;
      });

    // Fetch detailed trip data and render table
    fetch(`/api/trips${params}`)
      .then(res => res.json())
      .then(renderTripTable);

    // Fetch trips distribution over time and render line chart
    fetch(`/api/trips/time-distribution${params}`)
      .then(res => res.json())
      .then(renderTripsOverTime);

    // Fetch trip duration histogram data and render bar chart
    fetch(`/api/trips/duration-histogram${params}`)
      .then(res => res.json())
      .then(renderDurationHist);

    // Fetch pickup locations for heatmap visualization
    fetch(`/api/trips/pickup-heatmap${params}`)
      .then(res => res.json())
      .then(renderPickupHeatmap);
  }

  // Render trip details as rows in the HTML table body
  function renderTripTable(tripList) {
    const tbody = document.querySelector("#tripTable tbody");
    tbody.innerHTML = "";  // Clear existing rows
    tripList.forEach(trip => {
      let tr = document.createElement("tr");
      tr.innerHTML = `<td>${trip.pickup_location}</td>
                      <td>${trip.dropoff_location}</td>
                      <td>${trip.duration_sec}</td>
                      <td>${trip.distance_km}</td>
                      <td>${trip.fare}</td>`;
      tbody.appendChild(tr);
    });
  }

  // Chart instances to manage and destroy before re-rendering
  let tripsOverTimeChart, durationHistChart, pickupHeatmapChart;

  // Render a line chart of trips over hours of the day
  function renderTripsOverTime(data) {
    if (tripsOverTimeChart) tripsOverTimeChart.destroy();
    tripsOverTimeChart = new Chart(document.getElementById("tripsOverTime").getContext("2d"), {
      type: "line",
      data: {
        labels: data.hours,
        datasets: [{ label: "Trips per Hour", data: data.counts, fill: false, borderColor: "#444" }],
      },
    });
  }

  // Render a bar chart for distribution of trip durations
  function renderDurationHist(data) {
    if (durationHistChart) durationHistChart.destroy();
    durationHistChart = new Chart(document.getElementById("durationHist").getContext("2d"), {
      type: "bar",
      data: {
        labels: data.bins,
        datasets: [{ label: "Trip Duration (sec)", data: data.counts, backgroundColor: "#aaa" }],
      },
    });
  }

  // Render a scatter plot heatmap for pickup GPS locations
  function renderPickupHeatmap(data) {
    if (pickupHeatmapChart) pickupHeatmapChart.destroy();
    pickupHeatmapChart = new Chart(document.getElementById("pickupHeatmap").getContext("2d"), {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Pickup Locations",
            data: data.locations,
            backgroundColor: "#666",
          },
        ],
      },
      options: {
        scales: {
          x: { type: "linear", position: "bottom", title: { display: true, text: "Longitude" } },
          y: { type: "linear", title: { display: true, text: "Latitude" } },
        },
      },
    });
  }

  // Add click event listeners on table headers to allow sorting by different trip attributes
  document.querySelectorAll("#tripTable th").forEach(header => {
    header.onclick = function () {
      const sortBy = this.getAttribute("data-sort");
      fetch(`/api/trips?sort=${sortBy}`)
        .then(res => res.json())
        .then(renderTripTable);
    };
  });

  // Trigger initial fetch to populate dashboard on page load
  fetchAndUpdate();
});
