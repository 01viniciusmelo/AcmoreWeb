/**
 * Created by moon on 16-12-10.
 */
var languageName = ["C", "C++", "Pascal", "Java 1.7", "Ruby",
                 "Bash", "Python 2.7", "PHP", "Perl", "C#",
                 "Obj-C", "Free Basic", "Schema", "Clang", "Clang++",
                 "Lua", "JavaScript (ES6)", "Python 3.5", "Go", "Other Language"];

var judgeResult = ["Waiting...",      "Waiting Rejudging",    "Compiling",    "Running",
                "Accepted",     "Presentation Error",   "Wrong Answer", "Time Limit Exceed",
                "Memory Limit Exceed", "Output Limit Exceed", "Runtime Error", "Compile Error",
                "Compile Completed"];

var judgeResultType = [
                    "active",   "active",   "active",     "active",
                    "success",  "info",  "danger",   "info",
                    "info",  "info",  "warning",   "warning",
                    ""];

var orderNumber = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

var staticUrl = "static/";

var loadingImg = staticUrl + "img/loading.gif";

var sourceCodeOj = "/s/oj/";

var isMobile = function() {
    return (screen.width < 768);
}();

var checkUsername = function(str) {
    var reg =
    /^[\u4E00-\u9FA5a-zA-Z0-9_]{6,32}$/;
    return reg.test(str);
};

var checkUsernameFormat = checkUsername;

var checkEmailFormat = function (str) {
    var reg =
    /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,8}$/;
    return reg.test(str);
};

/**
 * Local timezone name.
 */
var timezoneName = function() {
    var minute = (new Date()).getTimezoneOffset();
    return (minute == 0) ? " UTC" : " UTC" + ((minute < 0) ? "+":"") + (-minute/60);
}();

/**
 * secNum is time seconds, if type is undefined return long time format else return short.
 */
var sec2time = function(secNum, type) {
    var result = "";
    var hour, minute, second;
    var fillTwoFormat = function() {
        hour = (hour<10)?"0"+hour:hour;
        minute = (minute<10)?"0"+minute:minute;
        second = (second<10)?"0"+second:second;
    };
    if (type == undefined) {
        var day = Math.floor(secNum/86400);
        hour = Math.floor((secNum-day*86400)/3600);
        minute = Math.floor((secNum-day*86400-hour*3600)/60);
        second = secNum-day*86400-hour*3600-minute*60;
        if (day > 0) {
            result += day;
            result += (day==1)?" day ":" days ";
        }
        result += hour+" hours " + minute+" minutes "+second+" seconds";
    }else {
        hour = Math.floor(secNum/3600);
        minute = Math.floor((secNum-hour*3600)/60);
        second = secNum-hour*3600-minute*60;
        fillTwoFormat();
        result += "" + hour + ":" + minute+":"+second;
    }

    return result;
};

var timestamp2time = function(timestamp) {
    var d = new Date(timestamp);
    var year = d.getFullYear();
    var month = d.getMonth()+1;
    month = (month<10)?"0"+month:month;
    var day = d.getDate();
    day = (day<10)?"0"+day:day;
    var hour = d.getHours();
    hour = (hour<10)?"0"+hour:hour;
    var minute = d.getMinutes();
    minute = (minute<10)?"0"+minute:minute;
    var second = d.getSeconds();
    second = (second<10)?"0"+second:second;
    //return d.toUTCString()
    return ""+year+"-"+month+"-"+day+" "+hour+":"+minute+":"+second +timezoneName;
};

var vjudge_problem_url_list = {
    HDU:'http://acm.hdu.edu.cn/showproblem.php?pid=',
};


var markdownTag = '<!--Markdown-->';
