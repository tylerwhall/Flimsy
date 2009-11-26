function FlimsyMap(element) {
    /* This code makes managing markers much easier */
    var infowindow;
    (function () {

      google.maps.Map.prototype.markers = new Array();
        
      google.maps.Map.prototype.addMarker = function(marker) {
        this.markers[this.markers.length] = marker;
      };
        
      google.maps.Map.prototype.getMarkers = function() {
        return this.markers
      };
        
      google.maps.Map.prototype.clearMarkers = function() {
        if(infowindow) {
          infowindow.close();
        }
        
        for(var i=0; i<this.markers.length; i++){
          this.markers[i].set_map(null);
        }
      };
    })();

    /* Create map */
    var latlng = new google.maps.LatLng(38.215913,-85.757668);
    var options = {
        zoom: 16,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };

    this.map = new google.maps.Map(document.getElementById(element), options);

    /* Takes an array of sensor dicts */
    this.handleSensors = function(sensors) {
        this.map.clearMarkers();
        for (var i = 0; i < sensors.length; i++) {
            var content = sensors[i].name;
            if (sensors[i].flooded) {
                content += "<b><br>FLOODED</b>";
            }
            this.map.addMarker(this.createMarker(sensors[i].name,
                                           content,
                                           new google.maps.LatLng(sensors[i].lat, sensors[i].lng)));
        }
    }

    this.createMarker = function (name, caption, latlng) {
        var marker = new google.maps.Marker({position: latlng,
                                             title: name,
                                             map: this.map});
        google.maps.event.addListener(marker, "click", function() {
          if (infowindow) infowindow.close();
          infowindow = new google.maps.InfoWindow({content: caption});
          infowindow.open(this.map, marker);
        });
        return marker;
    }
}
