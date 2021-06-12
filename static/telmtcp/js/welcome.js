let welcome_modal;

welcome_modal = new Vue({
    delimiters: ['[[', ']]'],
    el: "#welcome_modal",
    data: {
        reg_username:'',
        reg_email:'',
        reg_phone:'',
        reg_pwd:'',
        reg_confirm_pwd:'',
        reg_email_verify: '',
        username: '',
        password: ''
    },
    methods: {
        onclick_signup: function(){
            if (this.reg_username === ''){
                alert("Please input username");return;
            }
            if (this.reg_email === ''){
                alert("Please input email");return;
            }
            if(valid_email_pattern(this.reg_email) === false){
                alert("Please input correct email pattern");return;
            }
            if (this.reg_phone === ''){
                alert("Please input phone number");return;
            }
            if (this.reg_pwd === ''){
                alert("Please input password");return;
            }
            if (this.reg_confirm_pwd === ''){
                alert("Please input confirm password");return;
            }
            if (this.reg_pwd !== this.reg_confirm_pwd){
                alert("Password doesn't match");
                return;
            }

            let phone = $('#iti-0__country-listbox li[aria-selected="true"]').attr("data-dial-code") + this.reg_phone;
            let param = {
                reg_username: this.reg_username,
                reg_email: this.reg_email,
                reg_phone: phone,
                reg_pwd: this.reg_pwd
            };
            var button = $('#signup_button');
            button.prop("disabled", true);
            $.ajax({
                url: "register",
                type: "POST",
                data: param,
                success: function(res) {
                    button.prop("disabled", false);
                    if (res === "success"){
                        $('.signup-modal').modal("hide");
                        // alert("Welcome! Sign up success, please sign in now.");
                        //$('.email-verify-modal').modal("show");
                        window.location.href = "profile";
                    } else if (res === "send_code") {
                        $('.signup-modal').modal("hide");
                        $('.email-verify-modal').modal("show");
                    }
                    else if (res === "username_exist"){
                        alert("Username exists");
                    } else if (res === "email_exist"){
                        alert("Email exists");
                    } else if (res === "phoneexist"){
                        alert("Phone number exists");
                    } else {
                        alert(res);
                    }
                }
            });
        },
        on_register: function() {
            let param = {
                username: this.reg_username,
                password: this.reg_pwd,
                email: this.reg_email,
                reg_email_verify: this.reg_email_verify};
            var button = $('#confirm_button');
            button.prop("disabled", true);
            $.ajax({
                url: "reg_email_verify",
                type: "POST",
                data: param,
                success: function(res) {
                    button.prop("disabled", false);
                    if (res === 'success'){
                        $('.email-verify-modal').modal("hide");
                        window.location.href = "profile";
                    } else {
                        alert("Verify failed, Error code:" + res);
                    }
                }
            });
        },
        on_reset: function() {
            if(valid_email_pattern(this.username) === false){
                alert("Please input correct email pattern");
                return;
            }
            let param = {email: this.username};
            $.ajax({
                url: "reset_password",
                type: "POST",
                data: param,
                success: function(res) {
                    if (res === 'success'){
                        alert("Please check your email box! We sent new password to your email address!");
                    } else {
                        alert("Reset password Failed! Error:" + res);
                    }
                }
            });
        },
        on_signin: function() {
            let param = {username: this.username, password: this.password};
            var button = $('#signin_button');
            button.prop("disabled", true);
            $.ajax({
                url: "login",
                type: "POST",
                data: param,
                success: function(res) {
                    button.prop("disabled", false);
                    if (res !== 'fail'){
                        window.location.href = res;
                    } else {
                        alert("Login failed");
                    }
                }
            });
        }
    }
});

function on_get_started() {
    $('.signup-modal').modal("show");
}