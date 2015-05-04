/**
 * Created by jonathan on 3/7/15.
 */

var CameraApp = function() {};

CameraApp.prototype = {
    framesPerSecond: 15,
    timeoutInMinutes: 10,

    setup: function() {
        this.startTime = new Date().getTime();
        this.image = document.getElementById('CameraImage');
        this.imageSource = 'http://104.206.193.11:49709/dcnvr/video/live/image/2?w=320&h=240';
        this.loadImage();
    },

    loadImage: function() {
        var calculatedDelay = 1000 / this.framesPerSecond;
        var currentTime = new Date().getTime();

        if (currentTime - this.startTime > this.timeoutInMinutes * 60000)
        {
            if (!confirm('Live video viewing has timed out. Do you want to continue viewing?'))
            {
                return;
            } else {
                this.startTime = new Date().getTime();
            }
        }


        if (this.lastLoadTime != undefined){
            calculatedDelay = calculatedDelay - (currentTime - this.lastLoadTime);
        }

        this.lastLoadTime = currentTime;

        if (calculatedDelay <= 0) {
            this.image.src = this.imageSource + '&random=' + Math.random();
        } else {
            var cameraApp = this;
            this.timer = setTimeout(function() {
                cameraApp.image.src = cameraApp.imageSource + '&random=' + Math.random();
            }, calculatedDelay);
        }
    }
};

var cameraApp = null;

$(document).ready(function () {
    cameraApp = new CameraApp();

    $('#CameraImage').load(function() {
        cameraApp.loadImage();
    });

    cameraApp.setup();
});
