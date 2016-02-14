/**
 * Copyright (C) 2014 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

function inRectCheck(point, rect) {
    return rect.x <= point.x && point.x <= rect.x + rect.width &&
    rect.y <= point.y && point.y <= rect.y + rect.height
}

function formatTime(millseconds) {
    if (millseconds <= 0) return "00:00:00";
    var secs = Math.ceil(millseconds / 1000)
    var hr = Math.floor(secs / 3600);
    var min = Math.floor((secs - (hr * 3600))/60);
    var sec = secs - (hr * 3600) - (min * 60);

    if (hr < 10) {hr = "0" + hr; }
    if (min < 10) {min = "0" + min;}
    if (sec < 10) {sec = "0" + sec;}
    if (!hr) {hr = "00";}
    return hr + ':' + min + ':' + sec;
}

// with milliseconds
function formatTime2(millseconds) {
    if (millseconds <= 0) return "00:00:00"

    var spareMillis = millseconds % 1000
    return formatTime(millseconds) + "." + spareMillis
}

function formatSize(capacity) {
    var teras = capacity / (1024 * 1024 * 1024 * 1024)
    capacity = capacity % (1024 * 1024 * 1024 * 1024)
    var gigas = capacity / (1024 * 1024 * 1024)
    capacity = capacity % (1024 * 1024 * 1024)
    var megas = capacity / (1024 * 1024)
    capacity = capacity % (1024 * 1024)
    var kilos = capacity / 1024

    return Math.floor(teras) ? teras.toFixed(1) + "TB" :
            Math.floor(gigas) ? gigas.toFixed(1) + "GB":
            Math.floor(megas) ? megas.toFixed(1) + "MB" :
            kilos + "KB"
}

function formatFilePath(file_path) {
    var path = file_path.replace("file://", "")
    return path
}