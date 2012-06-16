(function($){

var baseline = null, elapsed = null, timestamp = null, update = null,
    prepare = function(timer) {
        baseline = new Date();
        timestamp = parseInt(timer.attr('id'));
        elapsed = parseInt(timer.attr('rel'));
    };

// Start not-pressed-since timer
(function(){
    var info = $('#main .info'), 
        timer = info.find('span.ago'),
        time, lastupdate = 0;

    if (timer.length === 0) {return;}
    if (timer.attr('id').length === 0) {return;}
    if (timer.attr('rel').length === 0) {return;}

    prepare(timer);

    if (timestamp === 0) { info.css({visibility: 'hidden'}); return; }

    setTimeout(function() {
        lastupdate++;
        time = Humanize.clock(elapsed + (((new Date()) - baseline) / 1000));
        timer.empty().text(time);
        setTimeout(arguments.callee, 1000);
    }, 1000);
})();

// Check for updates
(function(){
    var info = $('#main .info'),
        scores = $('#scores'),
        synchronize = $('#synchronize'),
        user = info.find('a.user'),
        timer = info.find('span.ago'),
        timeout = 60000,
        url = '/status/' + user.text().replace(/@/, '') + '/' + timestamp,
        fn;

    fn = function() {
        if (synchronize.hasClass('updating')) { return; }
        
        synchronize.stop().css('opacity', 1).addClass('updating');
        
        $.ajax({
            url: url,
            cache: false,
            dataType: 'json',
            success: function(json, status, xhr) {
                if (json.modified) {
                    info.slideDown();
                    timer.attr('id', json.timestamp);
                    timer.attr('rel', json.delta);
                    prepare(timer);
                    user.attr('href', json.user.link).attr('title', json.user.name).text(json.user.username);
                    url = '/status/' + user.text().replace(/@/, '') + '/' + timestamp;
                    if (json.html) {
                        scores.html(json.html);
                    }
                }
                update = setTimeout(fn, timeout);
                synchronize.stop().animate({opacity: 0}, 1500, function() { synchronize.animate({opacity: 1}, timeout); });
                synchronize.removeClass('updating');
            },
            error: function(xhr, status, error) {
                update = setTimeout(fn, timeout);
                synchronize.removeClass('updating');
            }
        });
    };
    update = setTimeout(fn, timeout);
    synchronize.click(function(e){ e.preventDefault(); clearTimeout(update); fn(); }).css('opacity', 0).animate({opacity: 1}, timeout);
})();

})(jQuery);