function onclick_subscribe(plan_id) {
    var param = {plan_id: plan_id};

    $.ajax({
        type: 'POST',
        url: 'check_current_plan',
        data: param,
        success: function (res) {
            if (res === 'error') {
                alert("Error occured");
            } else if (res === 'trial_exist') {
                alert("You already have trial plan");
            }
            else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                res = JSON.parse(res);
                var custom_plan = res.custom_plan;
                if (custom_plan) {
                    init_custom_plan_modal();
                } else {
                    $('.content-wrapper').load('/load_paypal_regular_plans',{
                        plan_id: plan_id
                    }, function () {});
                }
            }
        }
    });
}

function init_custom_plan_modal(){
    open_modal("custom_plan");
    $('#cp_r1').iCheck('check');
    $('#custom_total_price').text('0.00');
    $('#custom_account_cn').val(0);
}