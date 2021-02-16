const url = "http://localhost:8080/"
let map;

let script = document.createElement('script');
script.src = "https://maps.googleapis.com/maps/api/js?key=YOURKEYHERE&callback=initMap"
script.async = true;

function initMap() {
   map = new google.maps.Map(document.getElementById('map'),
     { center: {lat: 0, lng: 0}, zoom: 2});
   fetchAllLocations();
}

document.head.appendChild(script);

function createLatLngs(data) {
  let geoms = [];
  if(data.allConnections && data.allConnections.edges.length > 0) {
    for(const edge of data.allConnections.edges) {
      let node = edge.node;
      map.data.add({
        geometry: new google.maps.LatLng(node.latitude, node.longitude)
      });
      let pointFeature = {
        type: "Feature",
        geometry: {
          type: "point",
          coordinates: [node.longitude, node.latitude]
        },
        properties: {}
      };

      geoms.push(pointFeature); 
    }
  }

  return geoms;
}

function fetchAllLocations() {
  let params = {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query: '{allConnections{edges{node{sourceAddress sourcePort destinationAddress destinationPort latitude longitude}}}}'}) 
  };
  
  fetch(url, params)
    .then(data => {
      return data.json();
    })
    .then(resp => {
      if(resp && resp.data) {
        let points = createLatLngs(resp.data); 
        // map.data.add(points);
      } else {
        console.log("Failed to load data from server.");
      } 
    })
    .catch(error => 
      console.log(error)
    );
}
