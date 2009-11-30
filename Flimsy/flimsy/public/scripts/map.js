function FlimsyMap(element, lat, lng) {
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
    var latlng = new google.maps.LatLng(lat,lng);
    var options = {
        zoom: 16,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };

    this.map = new google.maps.Map(document.getElementById(element), options);

    /* Takes an array of sensor dicts */
    this.handleSensors = function(sensors) {
        for (var i = 0; i < sensors.length; i++) {
            var markers = this.map.getMarkers()
            var makeNew = true;
            for (var j = 0; j < markers.length; j++) {
                if (sensors[i].id == markers[j].id) {
                    makeNew = false;
                    if (sensors[i].flooded != markers[j].flooded) {
                        markers[j].set_map(null);
                        markers.splice(j,1); //Remove from array
                        makeNew = true;
                    }
                }
            }
            if (makeNew) {
                var content = sensors[i].name;
                this.map.addMarker(this.createMarker(sensors[i].id, sensors[i].name,
                                       content,
                                       sensors[i].flooded,
                                       new google.maps.LatLng(sensors[i].lat, sensors[i].lng)));
            }
        }
    }

    this.createMarker = function (id, name, caption, flooded, latlng) {
        var image = "/images/marker.png"
        if (flooded) {
            caption += "<b><br>FLOODED</b>";
            image = "/images/marker_blue.png"
        }
        var image = new google.maps.MarkerImage(image,
        // This marker is 20 pixels wide by 32 pixels tall.
        new google.maps.Size(20, 34),
        // The origin for this image is 0,0.
        new google.maps.Point(0, 0),
        // The anchor for this image is the base of the flagpole at 0,32.
        new google.maps.Point(10,34));

        var marker = new google.maps.Marker({position: latlng,
                                             title: name,
                                             icon: image,
                                             map: this.map});
        marker.id = id;
        marker.flooded = flooded;
        google.maps.event.addListener(marker, "click", function() {
          if (infowindow) infowindow.close();
          infowindow = new google.maps.InfoWindow({content: caption});
          infowindow.open(this.map, marker);
        });
        return marker;
    }
}
