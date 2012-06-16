(function($) {

$(function() {
    function lookup(time, score) {
        try {
            var username = data.reference[time][score]
            if (username === undefined) { return ''; }
            return username;
        } catch(error) {
            return '';
        }
    }
    
//    var r = Raphael('scores-graph'), scores;
//    r.g.txtattr.font = "12px 'Fontin Sans', Fontin-Sans, sans-serif";
//    scores = r.g.linechart(50, 30, 860, 550, data.x, data.y, {nostroke: false, axis: "0 0 0 1", symbol: "o", width: 1, legened: ['acosta', 'wvega']});
//    scores.hoverColumn(function() {
//        this.tags = r.set();
//        for (var i = 0, ii = this.y.length; i < ii; i++) {
//            this.tags.push(r.g.popup(this.x, this.y[i], lookup(this.axis, this.values[i]) + ': ' + this.values[i]).insertBefore(this).attr([{fill: "#DDD"}, {fill: this.symbols[i].attr("fill")}]))
//        }
//    }, function() {
//        this.tags && this.tags.remove();
//    });

    var scoresgraph = $('#scores-graph'),
        tooltip = $('<div id="tooltip"/>').appendTo($('body')),
        width = scores.end - scores.start,
        height = scores.max - scores.min,
        options = {
            series: { 
                lines: { show: true },
                points: { show: true },
                sahdowSize: 0
            },
            grid: { hoverable: true, clickable: true },
            legend: {
                show: true,
                position: 'nw'
            },
            xaxis: { 
                mode: 'time',
                min: scores.start,
                max: scores.end,
                zoomRange: [1, width],
                panRange: [scores.start, scores.end]
            },
            yaxis: {
                min: scores.min,
                max: scores.max,
                zoomRange: [1, height],
                panRange: [scores.min, scores.max] },
            zoom: { interactive: true },
            pan: { interactive: true }
        },
        scoresplot, point = null;

    scoresplot = $.plot(scoresgraph, scores.data, options);
    
    scoresgraph.bind('plothover', function(event, pos, item) {
        if (item) {
            if (point === null || point[0] != item.datapoint[0] || point[1] != item.datapoint[1]) {
                point = item.datapoint;
                tooltip.html(item.series.label + ': ' + parseInt(point[1].toFixed(2))).css('background-color', item.series.color);
                var x = item.pageX - (tooltip.width() / 2),
                    y = item.pageY - tooltip.height() - 18;
                if (tooltip.css('opacity') < 0.2) {
                    tooltip.stop().css({top: y, left: x}).animate({ opacity: 1}, 400);
                } else {
                    tooltip.stop().animate({ opacity: 1, top: y, left: x}, 600);
                }
            }
        } else {
            tooltip.stop().animate({opacity: 0}, 400);
            point = null;
        }
    });
});

})(jQuery);