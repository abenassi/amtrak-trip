function main() {
  cartodb.createVis('map', 'https://agustinbenassi.cartodb.com/api/v2/viz/a8032d7e-ffdb-11e4-ba81-0e853d047bba/viz.json', {
      shareable: true,
      title: true,
      description: true,
      search: true,
      tiles_loader: true,
      // center_lat: 0,
      // center_lon: 0,
      zoom: 5
    })

}

window.onload = main;

