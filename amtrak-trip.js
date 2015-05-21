function main() {
  cartodb.createVis('map', 'https://agustinbenassi.cartodb.com/api/v2/viz/98b8bb06-fa7f-11e4-a9fb-0e0c41326911/viz.json', {
      shareable: true,
      title: true,
      description: true,
      search: true,
      tiles_loader: true,
      center_lat: 0,
      center_lon: 0,
      zoom: 2
    })
    .done(function(vis, layers) {
      layers[1].getSubLayer(0).hide();
      layers[2].on('change:time', function(obj) {
        if (layers[2].getStep() == 1) {
          layers[2].stop();
        } else if (layers[2].getStep() == 34) {
          var rc = vis.getOverlay('text');
          rc.clean()
          layers[2].hide();
          layers[1].getSubLayer(0).show();
        }
      });

      layers[1].setInteraction(true);
      layers[1].on('featureOver', function(e, latlng, pos, data, index) {
        var sql = new cartodb.SQL({
          user: 'agustinbenassi'
        });

        sql.execute("SELECT * FROM rc_locations WHERE cartodb_id='" + data.cartodb_id + "'")
          .done(function(data) {

            // layers[2].setSQL("SELECT * FROM rc_locations_interpolated WHERE city='" + data.rows[0].city + "'");
            // var css = 'Map{-torque-frame-count:35;-torque-animation-duration:0.1;-torque-time-attribute:"step";-torque-aggregation-function:"count(cartodb_id)";-torque-resolution:1;-torque-data-aggregation:linear}#rc_location_interpolated{comp-op:lighter;marker-fill-opacity:.9;marker-line-color:#FFF;marker-line-width:.5;marker-line-opacity:.8;marker-type:ellipse;marker-width:5;marker-fill:#F90}#rc_location_interpolated[frame-offset=1]{marker-width:5;marker-fill-opacity:.6}#rc_location_interpolated[frame-offset=2]{marker-width:5;marker-fill-opacity:.55}#rc_location_interpolated[frame-offset=3]{marker-width:5;marker-fill-opacity:.5}#rc_location_interpolated[frame-offset=4]{marker-width:5;marker-fill-opacity:.45}#rc_location_interpolated[frame-offset=5]{marker-width:5;marker-fill-opacity:.4}#rc_location_interpolated[frame-offset=6]{marker-width:5;marker-fill-opacity:.35}#rc_location_interpolated[frame-offset=7]{marker-width:5;marker-fill-opacity:.3}#rc_location_interpolated[frame-offset=8]{marker-width:5;marker-fill-opacity:.25}#rc_location_interpolated[frame-offset=9]{marker-width:5;marker-fill-opacity:.2}#rc_location_interpolated[frame-offset=10]{marker-width:5;marker-fill-opacity:.15}';
            // layers[2].setCartoCSS(css);
            // layers[2].show();
            sql.execute("SELECT * FROM rc_locations WHERE city='" + data.rows[0].city + "'")
              .done(function(data) {

                overlay = vis.getOverlay('tooltip');
                overlay.width = 400
                var text = '<div class="cartodb-tooltip-content-wrapper"><div class="cartodb-tooltip-content"> <h4>' + data.rows[0].city + '</h4>';
                data.rows.forEach(function(row) {
                  text = text.concat('<p>' + row.name + ' <span class="batch">' + row.batch + '</span></p>' );
                });
                text = text.concat('</div></div>');
                overlay.el.innerHTML = text;
              })
              .error(function(errors) {
                // errors contains a list of errors
                console.log("errors:" + errors);
              });
          });
      });

      var box = vis.addOverlay({
        type: 'tooltip',
        template: '',
        width: 400, // width of the box
        position: 'bottom | right' // top, bottom, left and right are available
      });

      // you can get the native map to work with it
      var map = vis.getNativeMap();

      // map.panTo([50.5, 30.5]);
    })
    .error(function(err) {
      console.log(err);
    });
}

window.onload = main;

