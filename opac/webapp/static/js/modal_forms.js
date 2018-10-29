'use strict';

var ModalForms = {
    modal_id: null,
    form_id: null,
    url: "/",
    method: "POST",
    submit_btn_id: null,
    has_captcha: false,
    captcha_key: null,
    captcha_theme: "light",
    captcha_id: null,
    email_confirm_modal_id: "#modal_confirm",
    success_message: null,
    error_message: null,
    rcaptcha: null,

    submit:function(){
        var self = this;

        $.ajax({
          type: self.method,
          url: self.url,
          data: $(self.form_id).serialize(),
          success: function(data)
          {
            // Clean error message
            $.each(data.fields, function(_, name){
              var field = $('#' + name);

              field.parent().removeClass("has-error");
              $('#' + name + '_error').html('');
            });

            if (data.sent === false){

              if (self.has_captcha === true){
                $(self.submit_btn_id).attr('disabled', 'disabled');
                self.render_captcha();
              }

              // Set error message
              $.each(data.message, function(key, val){
                $('#' + key).parent().addClass("has-error");
                $('#' + key + '_error').html(val);
              });

            }else{
              $(self.modal_id).modal('toggle');
              $('.midGlyph').addClass('success');
              $('.midGlyph').html(self.success_message);
              $(self.email_confirm_modal_id).modal('show');
            }
          },
          error: function (data) {
            $(self.modal_id).modal('toggle');
            $('.midGlyph').removeClass('success').toggleClass('unsuccess');
            $('.midGlyph').html(self.error_message);
            $(self.email_confirm_modal_id).modal('show');
          }
        });

    },

    recaptcha_callback: function() {
        $(this.submit_btn_id).removeAttr('disabled');
    },

    registry_recaptcha_modal: function(){
        var self = this;

        $(this.modal_id).on('show.bs.modal', function () {

            setTimeout(function() {
                self.render_captcha(self.captcha_id, self.captcha_key,
                                    self.captcha_theme);
            }, 100);

        });

    },

    render_captcha: function(captcha_id, captcha_key, captcha_theme){

        if(this.render_captcha){
          $(this.submit_btn_id).attr('disabled', 'disabled');
        }

        if (this.rcaptcha === null){
            this.rcaptcha = grecaptcha.render(captcha_id, {
                                                sitekey: captcha_key,
                                                theme: captcha_theme,
                                                callback: this.recaptcha_callback.bind(this)
                                               });
        }else{
            grecaptcha.reset(this.rcaptcha);
        }
    },

    init: function(modal_id, form_id, url, method, submit_btn_id, has_captcha,
                   captcha_key, captcha_id, captcha_theme, email_confirm_modal_id,
                   success_message, error_message){

        this.modal_id = modal_id;
        this.form_id = form_id;
        this.url = url;
        this.method= method;
        this.submit_btn_id = submit_btn_id;
        this.has_captcha= has_captcha;
        this.captcha_key = captcha_key;
        this.captcha_theme = captcha_theme;
        this.captcha_id = captcha_id;
        this.email_confirm_modal_id = email_confirm_modal_id;
        this.success_message = success_message;
        this.error_message = error_message;
        this.rcaptcha = null;

        if (this.has_captcha === true){
            this.registry_recaptcha_modal();
        }

        var self = this;
        $(this.form_id).submit(function(e) {

            e.preventDefault();

            self.submit();
        });

        return this;
    },

};
