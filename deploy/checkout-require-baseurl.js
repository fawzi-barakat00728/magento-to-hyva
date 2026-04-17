(function () {
    'use strict';

    if (typeof window === 'undefined') {
        return;
    }

    var current = document.currentScript;
    var src = current && current.src ? current.src : '';
    var marker = '/js/checkout-require-baseurl.js';
    var idx = src.indexOf(marker);

    if (idx === -1) {
        return;
    }

    var base = src.slice(0, idx + 1);
    var requireConfig = window.require || {};
    var map = requireConfig.map || {};
    var globalMap = map['*'] || {};

    if (!requireConfig.baseUrl) {
        requireConfig.baseUrl = base;
    }

    if (!globalMap['Mollie_Payment/js/view/payment/method-renderer']) {
        globalMap['Mollie_Payment/js/view/payment/method-renderer'] =
            'Mollie_Payment/js/view/payment/method-renderer-safe';
    }

    map['*'] = globalMap;
    requireConfig.map = map;
    window.require = requireConfig;
})();
