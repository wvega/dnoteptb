/**
 * Javascript Humane Dates
 * Copyright (c) 2008 Dean Landolt (deanlandolt.com)
 * Re-write by Zach Leatherman (zachleat.com)
 *
 * Adopted from the John Resig's pretty.js
 * at http://ejohn.org/blog/javascript-pretty-date
 * and henrah's proposed modification
 * at http://ejohn.org/blog/javascript-pretty-date/#comment-297458
 *
 * Licensed under the MIT license.
 */

// TODO: License... this is yours

Humanize = {
    periods: {'years': 31556926, 'months': 2629743, 'weeks': 604800, 'days': 86400, 'hours': 3600, 'minutes': 60, 'seconds': 1},
    segmentate: function(seconds, skip) {
        var i, segments = {};
        skip = skip || {};
        for (i in this.periods) {
            if ((i in skip) === false) {
                segments[i] = Math.floor(seconds / this.periods[i]);
                seconds = seconds % this.periods[i];
            }
        }
        return segments;
    },
    humanize: function(seconds) {
        var segments = this.segmentate(seconds),
            strings = [],
            i;
        for (i in segments) {
            if (segments[i] > 0) {
                if (segments[i] > 2) {
                    strings.push(segments[i] + ' ' + i);
                } else {
                    strings.push(segments[i] + ' ' + i.slice(0, -1));
                }
            }
        }
        return strings.join(', ');
    },
    clock: function(seconds) {
        var segments = this.segmentate(seconds, {'years':1, 'months':1, 'weeks':1, 'days':1}),
            strings = [],
            i;
        for (i in segments) {
            strings.push(segments[i] > 9 ? segments[i] : ('0' + segments[i]));
        }
        return strings.join(':');
    }
};