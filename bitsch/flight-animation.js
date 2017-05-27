var mapstyle = new ol.style.Style({
    fill: new ol.style.Fill({
        color: 'rgba(66, 66, 66, 0.6)'
    }),
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 1
    }),
    text: new ol.style.Text({
        font: '12px Calibri,sans-serif',
        fill: new ol.style.Fill({
            color: '#000'
        }),
        stroke: new ol.style.Stroke({
            color: '#fff',
            width: 3
        })
    })
});

var map = new ol.Map({
    layers: [
        /*
         new ol.layer.Tile({
         source: // new ol.source.Stamen({
         // layer: 'toner'
         // })
         new ol.source.OSM({
         "url": "http://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
         }),
         }) */
        new ol.layer.Vector({
            source: new ol.source.Vector({
                url: './countries.geojson',
                format: new ol.format.GeoJSON()
            }),
            style: function(feature, resolution) {
                mapstyle.getText().setText(resolution < 5000 ? feature.get('name') : '');
                return mapstyle;
            }
        })
    ],
    controls: ol.control.defaults().extend([
        new ol.control.FullScreen()
    ]),
    target: 'map',
    view: new ol.View({
        center: ol.proj.fromLonLat([0, 17.5]),
        zoom: 3
    })
});

var style = new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#EAE911',
        width: 2,
        // lineDash: [8, 10] //or other combinations
    })
});

var flightsSource;
var addLater = function(feature, timeout) {
    window.setTimeout(function() {
        feature.set('start', new Date().getTime());
        flightsSource.addFeature(feature);
    }, timeout);
};

var deleteLater = function(feature) {
    window.setTimeout(function() {
        flightsSource.removeFeature(feature);
    }, 0);
};

var pointsPerMs = 0.1;
var animateFlights = function(event) {
    var vectorContext = event.vectorContext;
    var frameState = event.frameState;
    vectorContext.setStyle(style);

    var features = flightsSource.getFeatures();
    for (var i = 0; i < features.length; i++) {
        var feature = features[i];
        if (!feature.get('finished')) {
            // only draw the lines for which the animation has not finished yet
            var coords = feature.getGeometry().getCoordinates();
            var elapsedTime = frameState.time - feature.get('start');
            var elapsedPoints = elapsedTime * pointsPerMs;

            if (elapsedPoints >= coords.length) {
                feature.set('finished', true);
            }

            var maxIndex = Math.min(elapsedPoints, coords.length);
            var currentLine = new ol.geom.LineString(coords.slice(0, maxIndex));

            // directly draw the line with the vector context
            vectorContext.drawGeometry(currentLine);
        }
        //else {
        //  deleteLater(feature);
        ////flightsSource.removeFeature(feature);
        // }
    }
    // tell OpenLayers to continue the animation
    map.render();
};




flightsSource = new ol.source.Vector({
    wrapX: false,
    attributions: '#gpn2017',
    loader: function() {
        //nothin
    }
});
(function()  {
    setInterval(update_layer, 1000);
    var current = {}

    function update_layer(){

        var url = '/data';
        fetch(url).then(function(response) {
            var ret = response.json()
            return ret;
        }).then(function(json) {
            var newState = {}
            for (var i = 0; i < json.length; i++) {
                var src_lat = json[i]['src_lat'];
                var src_long = json[i]['src_long'];
                var dst_lat = json[i]['dst_lat'];
                var dst_long = json[i]['dst_long'];
                var conid = src_lat + ':' +  src_long + ':' + dst_long + ':' + dst_lat;
                if(current[conid]) {
                    newState[conid] = current[conid];
                    continue;
                }
                // create an arc circle between the two locations
                var arcGenerator = new arc.GreatCircle(
                    {y: src_lat, x: src_long},
                    {y: dst_lat, x: dst_long});

                var arcLine = arcGenerator.Arc(100, {offset: 10});
                if (arcLine.geometries.length === 1) {
                    var line = new ol.geom.LineString(arcLine.geometries[0].coords);
                    line.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));

                    var feature = new ol.Feature({
                        geometry: line,
                        finished: false
                    });
                    // add the feature with a delay so that the animation
                    // for all features does not start at the same time

                    feature.set('start', new Date().getTime());
                    flightsSource.addFeature(feature);
                    newState[conid] = feature;
                    current[conid] = feature;
                }
            }
            for(var key in current) {
                if(!newState[key]) {
                    deleteLater(current[key]);
                    delete current[key];
                }
            }
            map.on('postcompose', animateFlights);
        });

    }
})();

var flightsLayer = new ol.layer.Vector({
    source: flightsSource,
    style: function(feature) {
        // if the animation is still active for a feature, do not
        // render the feature with the layer style
        if (feature.get('finished')) {
            return style;
            // return null;
        } else {
            return style;
        }
    }
});

/*
 flightsSource = new ol.source.Vector({
 wrapX: false,
 attributions: 'Flight data by <a href="http://openflights.org/data.html">OpenFlights</a>,',
 loader: function() {
 var url = 'data/openflights/flights.json';
 fetch(url).then(function(response) {
 return response.json();
 }).then(function(json) {
 var flightsData = json.flights;
 for (var i = 0; i < flightsData.length; i++) {
 var flight = flightsData[i];
 var from = flight[0];
 var to = flight[1];

 // create an arc circle between the two locations
 var arcGenerator = new arc.GreatCircle(
 {x: from[1], y: from[0]},
 {x: to[1], y: to[0]});

 var arcLine = arcGenerator.Arc(100, {offset: 10});
 if (arcLine.geometries.length === 1) {
 var line = new ol.geom.LineString(arcLine.geometries[0].coords);
 line.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));

 var feature = new ol.Feature({
 geometry: line,
 finished: false
 });
 // add the feature with a delay so that the animation
 // for all features does not start at the same time

 addLater(feature, i * 50);
 }
 }
 map.on('postcompose', animateFlights);
 });
 }
 });*/


map.addLayer(flightsLayer);