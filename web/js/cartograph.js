var CG = CG || {};



CG.init = function(layer) {
    CG.map = L.map('map');

    CG.addMapLogging(CG.map);
    CG.mapEl = $("#map");  // optimization
    CG.ttEl = $("#tooltip");

    CG.layer = Tangram.leafletLayer({
        scene: '../template/scene.yaml?layer=' + layer,
        attribution: '<a href="https://nokomis.macalester.edu/cartograph" target="_blank">Cartograph</a> | &copy; Shilad Sen & contributors'
    });
    CG.activeLayer = layer;

    CG.layer.addTo(CG.map);

    CG.cursorTimer = null;
    CG.ttShowTimer = 0;
    CG.ttHideTimer = 0;

    CG.ttEl.tooltipster({
        content: 'Loading...',
        theme: 'tooltipster-shadow',
        contentAsHTML: true,
        trigger: 'custom',
        triggerOpen: {},
        interactive: true,
        delay: [400, 1000],
        updateAnimation: 'fade',
        maxWidth: 400,
        triggerClose: {
            mouseleave: true,
            originClick: true,
            touchleave: true
        }
    });

    CG.tt = CG.ttEl.tooltipster("instance");

    CG.getLayer = function () {
        return CG.activeLayer;
    };

    CG.changeLayer = function (newLayer) {
        CG.activeLayer = newLayer;
        var changed = false;
        ["vector", "raster"].forEach(function (srcName) {
            var src = CG.layer.scene.config.sources[srcName];
            var i = src.url.indexOf('/' + srcName + '/');
            if (i < 0) {
                console.log('couldnt find srcName ' + srcName + ' in ' + src.url);
                return;
            }
            var j = i + srcName.length + 2;
            var k = src.url.indexOf('/', j + 1);
            var newUrl = src.url.substring(0, j) + newLayer + src.url.substring(k);
            if (newUrl != src.url) {
                src.url = newUrl;
                changed = true;
            }
        });
        if (changed) {
            CG.layer.scene.updateConfig();
        }
    };


// var grid = L.gridLayer({
//     attribution: 'Grid Layer',
//     tileSize: L.point(256, 256)
// });
// grid.createTile = function (coords, done) {
//     var tile = document.createElement('div');
//     tile.innerHTML = [coords.x, coords.y, coords.z].join(', ');
//     tile.style.border = '2px solid red';
// // 			tile.style.background = 'white';
//     // test async
//     setTimeout(function () {
//         done(null, tile);
//     }, 0);
//     return tile;
// };
// grid.addTo(CG.map);

// window.setTimeout(function() { CG.changeLayer('gender') }, 3000);


    CG.layer.scene.subscribe({
        load: function (e) {
            if (L.Hash) {
                CG.hash = new L.Hash(CG.map);
            }
            var container = $('.leaflet-container');

            CG.layer.setSelectionEvents({
                hover: function (selection) {
                    if (selection.feature) {
                        container.css('cursor', 'pointer');
                        if (CG.cursorTimer) {
                            clearTimeout(CG.cursorTimer);
                            CG.cursorTimer = null;
                        }
                    } else if (!CG.cursorTimer) {
                        CG.cursorTimer = setTimeout(function () {
                            container.css('cursor', '');
                        }, 50);
                    }
                },
                click: function (selection) {
                    if (selection.feature && selection.feature.properties.name) {
                        var ev = selection.leaflet_event.originalEvent;
                        CG.handleCityHover(
                            ev.clientX,
                            ev.clientY,
                            selection.feature.properties);
                    } else {
                        CG.cancelCityHover();
                    }
                }
            });
        },
        error: function (e) {
            console.log('scene error:', e);
        },
        warning: function (e) {
            console.log('scene warning:', e);
        }
    });


    CG.showRelated = function (query) {
        var url = CG.layer.scene.config.sources.related.url;
        var i = url.indexOf('q=');
        var url2 = url.substring(0, i) + 'q=' + encodeURIComponent(query) + '&n=200';
        console.log(url2);
        CG.layer.scene.config.sources.related.url = url2;
        CG.layer.scene.config.layers.related.visible = true;
        CG.layer.scene.config.layers.relatedOverlay.visible = true;
        CG.layer.scene.updateConfig();
        $("#related-label span").html(query);
        $("#related-label").show();
        CG.map.setView([0, 0], 4);

        return false;
    };

    CG.hideRelated = function () {
        CG.layer.scene.config.layers.related.visible = false;
        CG.layer.scene.config.layers.relatedOverlay.visible = false;
        CG.layer.scene.updateConfig();
        $("#related-label").hide();
        $("#search-field").val('');
        return false;
    };
    allLayers = []
    $('#test_button').on('click', function () {
        console.log("clicked on test button");


        var viewport = CG.map.getBounds()

        var x_min = viewport._southWest.lng
        var x_max = viewport._northEast.lng
        var y_min = viewport._southWest.lat
        var y_max = viewport._northEast.lat

        var n_cities = 1
        var url = "roads?xmin=" + x_min + "&xmax=" + x_max + "&ymin=" + y_min + "&ymax=" + y_max + "&n_cities=" + n_cities



        var edgeNeutralStyle = {color: 'rgb(171, 171, 171)',
                                opacity: 0.7,
                                smoothFactor: 3,
                                attribution: 'edge'};

        $.get(url, function(response){
            var duplicateEdgeCatcher = {}
            var maxWeigh = 10
            var curves = []

            $.each(response, function(city, paths) {

                for(var i = 0; i < paths.length; i ++){
                    var line = []
                    var path = paths[i]
                    line.push('M', [parseFloat(path[0][0][1]),parseFloat(path[0][0][0])])
                    line.push("L", [path[0][1][1],path[0][1][0]])
                    var newWeight = parseFloat(path[0][0][2])
                    newWeight =  Math.ceil(newWeight)
                    edgeNeutralStyle['weight'] = newWeight
                    var newCurve = L.curve(line, edgeNeutralStyle)
                    allLayers.push(newCurve)
                    curves.push(newCurve)

                    for(var j = 1; j < path.length; j ++) {
                        line = []
                        var src = path[j][0]
                        var dest = path[j][1]
                        newWeight = parseFloat(path[j][2][0])/2
                        if(newWeight > maxWeigh){
                            newWeight = maxWeigh
                        }
                        else if(newWeight < 1){
                            newWeight = 1
                        }


                        console.log(src + " " +  dest + " "+ newWeight)

                        //if(src != dest){
                            if(!duplicateEdgeCatcher[(src, dest)]){

                                line.push('M', [parseFloat(src[1]), parseFloat(src[0])])
                                line.push('L', [parseFloat(dest[1]), parseFloat(dest[0])])
                                duplicateEdgeCatcher[(src, dest)] = true
                            }

                      //  }

                        edgeNeutralStyle['weight'] = newWeight
                        newCurve = L.curve(line, edgeNeutralStyle)
                        console.log(newCurve)
                        allLayers.push(newCurve)
                        curves.push(newCurve)

                    }

                }

             });
            storedcurveslayer = L.layerGroup(curves);
            CG.map.addLayer(storedcurveslayer);

        })




    })

    function get_random_color()
{
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ )
    {
       color += letters[Math.round(Math.random() * 15)];
    }
return color;
}



    $('#test_buttonRemove').on('click', function () {
        for(var j = 0; j < allLayers.length; j ++){
            CG.map.removeLayer(allLayers[j]);
        }

        allLayers = []
    })


    $('#search-field').on('focus', CG.hideRelated);
    $('#related-label a').on('click', CG.hideRelated);
    $('#search-field').autocomplete({
        serviceUrl: '../search.json',
        paramName: 'q',
        autoSelectFirst: true,
        showNoSuggestionNotice: true,

        formatResult: function (suggestion, currentValue) {
            if (suggestion.type == 'related') {
                return 'Related to <b>"' + currentValue + '"</b>';
            } else {
                return suggestion.value;
            }
            return suggestion.value;
        },

        onSelect: function (suggestion) {
            if (suggestion.type == 'related') {
                CG.showRelated(suggestion.value);
                return;
            }
            $("img.leaflet-marker-icon").remove();
            CG.log({event: 'search', title: suggestion.value});
            var info = suggestion.data;
            CG.map.flyTo(info.loc, info.zoom + 2, {duration: 0.4});
            L.marker(info.loc).addTo(CG.map);
        }
    });


    CG.handleCityHover = function (mapX, mapY, properties) {
        var title = properties.name;
        clearTimeout(CG.ttHideTimer);
        CG.ttHideTimer = 0;

        if (CG.ttShowTimer && CG.ttEl.data("toLoad") == title) {
            return; // in progress!
        }
        CG.ttEl.data("toLoad", title);
        if (CG.ttShowTimer) {
            clearTimeout(CG.ttShowTimer);
        }
        CG.ttShowTimer = setTimeout(function () {
            CG.ttShowTimer = null;
            CG.showCityTooltip(mapX, mapY, properties);
        }, 0);
    };

    CG.cancelCityHover = function () {
        clearTimeout(CG.ttShowTimer);
        CG.ttShowTimer = 0;
        if (CG.tt.status().open && !CG.ttHideTimer) {
            CG.ttHideTimer = setTimeout(function () {
                CG.ttHideTimer = null;
                CG.tt.close();
            }, 1000);
        }
    };


    CG.showCityTooltip = function (mapX, mapY, properties) {
        var title = properties.name;

        var isOpen = CG.tt.status().open;
        if (CG.ttEl.data("loading") == title) {
            if (!isOpen) CG.tt.open();
            return;
        }
        CG.ttEl.data("loading", title);

        var offset = CG.mapEl.offset();
        CG.ttEl.offset({
            top: offset.top + mapY - CG.ttEl.height() / 2,
            left: offset.left + mapX - CG.ttEl.width() / 2,
        });

        var html = '<b>' + title + '</b><br/>loading...';
        CG.tt.content(html);
        CG.tt.open();
        if (isOpen) {
            CG.tt.reposition();
        }
        var encoded = encodeURIComponent(title);
        var uri = 'https://en.wikipedia.org/w/api.php?action=query&format=json&titles=' + encoded + '&prop=pageimages|extracts&exintro&explaintext&exchars=400&callback=?';

        CG.showEdgesCityTooltip(mapX, mapY, properties);

        $.getJSON(uri, function (json) {
            var info = null;
            for (var pageId in json.query.pages) {
                info = json.query.pages[pageId];
                break;
            }
            var text = info.extract;
            var img = info.thumbnail;
            var html = "";
            if (img) {
                html += '<img align=left src="' + img.source + '" width=' + img.width + ' height=' + img.height + '>';
            }
            html += '<b>' + title + ':</b> &nbsp; &nbsp;' + text;

            var wpUrl = 'http://en.wikipedia.org/wiki/' + encoded;
            html += '[<a target="_new" href="' + wpUrl + '">see Wikipedia article</a>]';

            if (properties.men >= 9999.0) {
                html += '&nbsp; Article is about a man.';
            } else if (properties.women >= 9999.0) {
                html += '&nbsp; Article is about a woman.';
            } else if (properties.men || properties.women) {
                html += '&nbsp; Article links to ' +
                    Math.round(properties.men) + ' men and ' +
                    Math.round(properties.women) + ' women.';
            }

            // call the 'content' method to update the content of our tooltip with the returned data
            CG.tt.content(html);

            // to remember that the data has been loaded
            CG.ttEl.data('loaded', title);

            if (!CG.ttEl.data("mouseInBound")) {
                CG.ttEl.data("mouseInBound", true);
                $(".tooltipster-base").on("mouseenter", function () {
                    clearTimeout(CG.ttHideTimer);
                    CG.ttHideTimer = null;
                });
            }
        });
    }

}