const url = "http://localhost:8080/"
let map;

let script = document.createElement('script');
script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyA0P5XjTSHj7t2nmNL7_x8d5TGaxQYse4s&callback=initMap"
script.async = true;

function initMap() {
   myMap = new google.maps.Map(document.getElementById('map'),
     { center: {lat: 0, lng: 0}, zoom: 2});
   fetchAllLocations();
}

document.head.appendChild(script);

function getContentHTML(node) {

  let content = "<div>"
  for(const key of Object.keys(node)) {
     if(node[key]) {
       content += `<div>${key.toUpperCase()}: ${node[key]}</div>`;
     }
  }

  content += "</div>";
  return content;
}

function createLatLngs(data) {
  if(data.allConnections && data.allConnections.edges.length > 0) {
    for(const edge of data.allConnections.edges) {
      let node = edge.node;

      let geom = new google.maps.LatLng(node.latitude, node.longitude);
      let marker = new google.maps.Marker({
        position: geom,
        map: myMap,
      });

      let information = new google.maps.InfoWindow({
        content: getContentHTML(node),
      });

      marker.addListener('click', () => {
        information.open(myMap, marker);
      });

    }
  }
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
      } else {
        console.log("Failed to load data from server.");
      } 
    })
    .catch(error => 
      console.log(error)
    );
}
