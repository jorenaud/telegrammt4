var qrcode = null;
var crypto_expire = 0;
var crypto_order_id = "";
var time_interval = null;
var order_checker = null;

function valid_email_pattern(string){
    if (string.trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) === null) {
        return false;
    }
    return true;
}

function ajax_common_result_handler(ret_code){
    if (ret_code === "success"){
        alert("Operation success");
    } else if (ret_code === "error"){
        alert("Error occured");
    }
}

// *************** Get Cookie *************** //
function getCooke(name) {
	var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// *************** Get CSRF Token *************** //
function getCsrfToken() {
	return getCooke("csrftoken");
}

$( document ).ajaxSend(function( event, jqxhr, settings ) {
    jqxhr.setRequestHeader("X-CSRFToken", getCsrfToken());
});

function open_modal(modal_id) {
    $("#" + modal_id).modal({
        backdrop: 'static',
        keyboard: false
    });
    $("#" + modal_id).modal("show");
    $("#" + modal_id).draggable({
        handle: ".modal-content",
        create: function( event, ui ) {
            $(this).css({top: 0, left: 0});
        }
    });
}

function close_modal(modal_id) {
    if (modal_id === 'crypto_order') {
        clearInterval(time_interval);
        clearInterval(order_checker);
        qrcode.clear();
        qrcode = null;
        crypto_expire = 0;
        crypto_order_id = "";
    }
    $("#" + modal_id).modal("hide");
    $("#" + modal_id).draggable("destroy");
}

function init_crypto_order_modal(order_id, crypto, address, amount, price, expire){
    crypto_expire = expire;
    crypto_order_id = order_id;
    document.getElementById("qrcode").innerHTML = "";
    document.getElementById("countdown").innerHTML = "";
    document.getElementById("close_crypto_button").disabled = false;
    open_modal("crypto_order");
    $('#eth_address').val(address);
    $('#eth_amount').val(amount.toString());
    document.getElementById("usd_amount").innerHTML = "$" + price.toString() + " USD";
    let qr_code = 'ethereum:' + address.toString() + '?value=' + (amount * 1000000000000000000).toString();
    if (qrcode !== null)
    {
        qrcode.clear();
        qrcode.makeCode(qr_code);
    }
    else
    {
        qrcode = new QRCode(document.getElementById("qrcode"), {
            text: qr_code,
            width: 150,
            height: 150
          });
    }
}
function init_crypto_order_clock() {
        let tries = 0;
        let pointstr = ".";
        time_interval = setInterval(function () {
            // Display the result in the element with id="demo"
            if (crypto_expire < 0) return;
            let minutes = (Math.floor(crypto_expire / 60)).toString();
            let seconds = (crypto_expire % 60).toString();
            if (minutes.length === 1)
                minutes = "0" + minutes;
            if (seconds.length === 1)
                seconds = "0" + seconds;
            document.getElementById("countdown").innerHTML = minutes + ":" + seconds + "  Awaiting payment";
            crypto_expire -= 1;
            // If the count down is finished, write some text
            if (crypto_expire < 0 && tries !== 0) {
                document.getElementById("countdown").innerHTML = "We're constantly monitoring the network and didn't detect a payment. Try again.";
                if (qrcode != null)
                    qrcode.clear();
                document.getElementById("qrcode").innerHTML = "";
                qrcode = null;
                $('#eth_address').val('');
                $('#eth_amount').val('');
                tries = 0;
                clearInterval(time_interval);
            }
            tries++;
        }, 1000);

        order_checker = setInterval(function () {
            // Display the result in the element with id="demo"
            if (crypto_order_id === "") return;
            if (tries === 0) return;
            if (crypto_expire <= 0) return;
            $.ajax({
                type: "GET",
                url: "verify_crypto_order",
                data: {
                    order_id: crypto_order_id
                },
                success: function (res) {
                    let result = JSON.parse(res);
                    res = result['status'];
                    if (res === 1)
                    {
                        clearInterval(time_interval);
                        document.getElementById("close_crypto_button").disabled = true;
                        if (pointstr.length >= 4) pointstr = '.';
                        document.getElementById("countdown").innerHTML = "Confirming Payment" + pointstr;
                        pointstr += ".";
                    }
                    else if (res === 2)
                    {
                        clearInterval(order_checker);
                        window.location.href = 'order';
                    }
                    else if (res === -1)
                    {
                        clearInterval(time_interval);
                        clearInterval(order_checker);
                        document.getElementById("countdown").innerHTML = "We're constantly monitoring the network and didn't detect a payment. Try again.";
                        if (qrcode != null)
                            qrcode.clear();
                        document.getElementById("qrcode").innerHTML = "";
                        qrcode = null;
                        $('#eth_address').val('');
                        $('#eth_amount').val('');
                        tries = 0;
                    }
                    else if (res === -2)
                    {
                        clearInterval(time_interval);
                        clearInterval(order_checker);
                        if (result['ref_code'] === 0)
                        {
                            document.getElementById("countdown").innerHTML = "We received underpayment from you. Just refunded. Sorry for the inconvenience.";
                            document.getElementById("qrcode").innerHTML = "ref_tx:" + result['ref_tx'];
                        }
                        else
                        {
                            document.getElementById("countdown").innerHTML = "We received underpayment from you. Trying to refund, but failed please contact support.";
                            document.getElementById("qrcode").innerHTML = "Error Code:" + result['ref_code'] + " Message:" + result['ref_message']
                        }
                        if (qrcode != null)
                            qrcode.clear();
                        qrcode = null;
                        tries = 0;
                    }
                    else if (res === -3)
                    {
                        clearInterval(time_interval);
                        clearInterval(order_checker);
                        document.getElementById("countdown").innerHTML = "We received mini payment, we can't refund because of gas limit, Sorry for the inconvenience.";
                        if (qrcode != null)
                            qrcode.clear();
                        document.getElementById("qrcode").innerHTML = "";
                        qrcode = null;
                        tries = 0;
                    }
                }
            });
        }, 10000);
    }

function copy_function(obj_id) {
    var copyText = document.getElementById(obj_id);
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
}

function copy_from_button_function(obj_id) {
    var copyText = document.getElementById(obj_id);
    navigator.clipboard.writeText(copyText.textContent)
}