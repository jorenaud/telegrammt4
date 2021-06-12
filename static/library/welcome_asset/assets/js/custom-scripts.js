(function($) {
    "use strict";
    
      $.fn.andSelf = function() {
        return this.addBack.apply(this, arguments);
      }
      
      
       /* 
        TwinMax Code Start          
       */
  
      var controller = new ScrollMagic.Controller,
      addScene = function(e, t) {
          var o = new ScrollMagic.Scene({
              triggerElement: e,
              triggerHook: "onEnter",
              offset: 100
          }).setTween(t);
          return o = o.addTo(controller)
      };
  

      TweenMax.from(".mh-nav", 0.1, {y:'80', opacity: 0, ease: Power1.easeOut}), 
      TweenMax.from(".header-overlay-img", 0.1, {opacity: 0,scale: "0.1", ease: Elastic.easeInOut}), 
      TweenMax.from(".header-content-inner h2", 1, {y:'80', opacity: 0, ease: Power1.easeOut}), 
      TweenMax.from(".header-content-inner p", 1.5, {y:'80', opacity: 0, ease: Power1.easeOut}), 
      TweenMax.from(".header-content-inner .btn", 2, {y:'80', opacity: 0, ease: Power1.easeOut}), 
      TweenMax.from("#imac", 2.3, { y:'80', opacity: 0, ease: Power1.easeOut});

  
      addScene("#section2", new TweenMax.from(".section2 .ev-content-title span",3, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
      addScene("#section2", new TweenMax.from(".section2 .ev-content-title h3", 1.2, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.3)),
      addScene("#section2", new TweenMax.from(".section2 .ev-content-title p", 1.5, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
      addScene("#section2", new TweenMax.from(".section2 #pr-item1", 1, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.4)),
      addScene("#section2", new TweenMax.from(".section2 #pr-item2", 1.5, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
      addScene("#section2", new TweenMax.from(".section2 #pr-item3", 1.8, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.6)),
      addScene("#section2", new TweenMax.from(".section2 #pr-item4", 2, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.7));


  
      addScene("#section3", new TweenMax.from(".section3 .taingle-shape", 1, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.2)),
      addScene("#section3", new TweenMax.from(".section3 .each-feature-img", 1.5, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.3)),
      addScene("#section3", new TweenMax.from(".section3 .ev-content-title h3", 1.8, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
      addScene("#section3", new TweenMax.from(".section3 .ev-content-title span", 3, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
      addScene("#section3", new TweenMax.from(".section3 .each-content-inner li", 2, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
  
      addScene("#section4", new TweenMax.from(".section4 .ev-content-title span", 3 , {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
      addScene("#section4", new TweenMax.from(".section4 .ev-content-title h3", 1.5, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.6)),
      addScene("#section4", new TweenMax.from(".section4 .ev-content-title p", 2, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.6)),
      addScene("#section4", new TweenMax.from(".section4 .lo-discover-content", 2, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(1)),
  
  
      addScene("#section5", new TweenMax.from(".section5 .ev-content-title span", 5, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.5)),
      addScene("#section5", new TweenMax.from(".section5 .ev-content-title h3", 1.5, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.6)),
      addScene("#section5", new TweenMax.from(".section5 .ev-content-title p", 1.8, {
          opacity: 0,
          y: 70,
          ease: Power1.easeOut
      }).delay(.9)),
      addScene("#section5", new TweenMax.from(".section5 #process-item1", 2, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.4)),
    addScene("#section5", new TweenMax.from(".section5 #process-item2", 2, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.5)),
    addScene("#section5", new TweenMax.from(".section5 #process-item3", 2.1, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.6)),
  
  
    addScene("#section6", new TweenMax.from(".section6 .ev-content-title span", 5, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.5)),
    addScene("#section6", new TweenMax.from(".section6 .ev-content-title h3", 1.5, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.6)),
    addScene("#section6", new TweenMax.from(".section6 .ev-content-title p", 2, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.9)),
    addScene("#section6", new TweenMax.from(".section6 .testimonial-inner", 2.1, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.6)),
  
    addScene("#section7", new TweenMax.from(".section7 .ev-content-title span", 1, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.5)),
    addScene("#section7", new TweenMax.from(".section7 .ev-content-title h3", 1.5, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.6)),
    addScene("#section7", new TweenMax.from(".section7 .ev-content-title p", 1.8, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.9)),
    addScene("#section7", new TweenMax.from(".section7 #price-item1", 1, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.4)),
    addScene("#section7", new TweenMax.from(".section7 #price-item2", 1.5, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.5)),
    addScene("#section7", new TweenMax.from(".section7 #price-item3", 2, {
        opacity: 0,
        y: 70,
        ease: Power1.easeOut
    }).delay(.6)),
  
  
    addScene("#ev-footer", new TweenMax.from(".ev-footer .ev-footer-links", 1, {
        opacity: 0,
        y: 10,
        ease: Power1.easeOut
    }).delay(0.2)),
    addScene("#ev-footer", new TweenMax.from(".ev-footer .ev-footer-bottom", 1.5, {
        opacity: 0,
        y: -10,
        ease: Power1.easeOut
    }).delay(0.2)),
  
  
        /* Loader Code Start 
        $(window).on("load", function() { 
          $(".section-loader").fadeOut("slow");
          
          var $container = $('.portfolioContainer');
          $container.isotope({
              filter: '*',
              animationOptions: {
                  queue: true
              }
          });
       
          $('.portfolio-nav li').click(function(){
              $('.portfolio-nav .active').removeClass('active');
              $(this).addClass('active');
       
              var selector = $(this).attr('data-filter');
              $container.isotope({
                  filter: selector,
                  animationOptions: {
                      queue: true
                  }
               });
               return false;
          });
        });
      /* Loader Code End */
  
      /*
      |====================
      | Mobile NAv trigger
      |=====================
      */
      
      $('.navbar-nav>li>a').on('click', function(){
          $('.navbar-collapse').collapse('hide');
      });
  
      /* counter 
      $('.counter').counterUp({
          delay: 12,
          time: 1200
      });
    */
    
      
  
      /*
      |=================
      | Onepage Nav
      |================
      */
          
        // $('#zb-header').onePageNav({
        //     currentClass: 'active', 
        //     changeHash: false,
        //     scrollSpeed: 750,
        //     scrollThreshold: 0.5,
        // });
  
  
          /***********************************************************/
          /* COUNT DOWN                                              */
          /********************************************************** 
            
          $('.name').countdown({
            end_time: "2019/05/21 14:27:28 +0600",
            wrapper: function(unit){
                var wrpr = $('<div></div>').
                    addClass(unit.toLowerCase()+'_wrapper').
                    addClass('col-sm-3').
                    addClass('col-xs-3').
                    addClass('col-md-3').
                    addClass('custom');
                var background = $('<div></div>').
                    addClass('background').
                    addClass('time').
                    appendTo(wrpr);
  
                $('<span class="counter style_all"></span>').appendTo(background);
                $('<span class="title">'+unit+'</span>').appendTo(background);
                return wrpr;
            }
        });
  
        */ 
      
      /*
      |=================
      | fancybox
      |================
      */
   
      $('#play-pause-button'). on("click", function() {
            var mediaVideo = $("#bgdvid").get(0);
            var mediap = $("#bgdvid");
            var playbtn = $("#play-pause-button");
            if (mediaVideo.paused) {
                mediaVideo.play();
                mediap.parent().addClass("gobottom");
            } else {
                mediaVideo.pause();
                mediap.parent().removeClass("gobottom");
            }
  
          });
      
      
      $(".uv-accordinaton-list") . on("click", function() {
          $(this).closest("ul").find(".uv-accordition-detail").each(function() {
              if ($(this).css("display") == 'block') {
                  $(this).slideUp(200);
                  $(this).closest("li").find("h2").removeClass("hilighted");
                  $(this).closest("li").find("h2").removeClass("color");
                  $(this).closest("li").find(".uv-right-arrow").text("+");
                  $(this).closest("li").removeClass("shadow-1");
                  return false;
              }
          });
          $(this).next().slideToggle(200);
          $(this).find(">:first-child");
          if ($(this).find(">:first-child").text() == "+") {
              $(this).find(">:first-child").text("-");
              $(this).find("h2").addClass("hilighted");
              $(this).find("h2").addClass("color");
              $(this).parent().addClass("shadow-1");
          } else {
              $(this).find(">:first-child").text("+");
              $(this).find("h2").removeClass("hilighted");
              $(this).parent().removeClass("shadow-1");
          }
      });
        
        
      /*
      |=====================
      | package tab
      |=====================
      */
  
      $('#zbTab a').on('click', function (e) {
        e.preventDefault()
        $(this).tab('show')
      });
        
        
      /*
      |===============
      | WOW ANIMATION
      |==================
  
          var wow = new WOW({
            mobile: false  // trigger animations on mobile devices (default is true)
        });
        wow.init();
      */
        
      /*
      | ==========================
      | NAV FIXED ON SCROLL
      | ==========================
      */
      $(window).on('scroll', function() {
          var scroll = $(window).scrollTop();
          if (scroll >= 50) {
              $(".nav-scroll").addClass("nav-strict");
          } else {
              $(".nav-scroll").removeClass("nav-strict");
          }
      });
      
  
      /*
      |=================
      | Client review
      |================
      */   
       $('#mh-client-review').owlCarousel({
          loop: true,
          responsiveClass: true,
          nav: true,
          autoplay: false,
          smartSpeed: 450,
          navText: ["<i class='fa fa-angle-left'></i>", "<i class='fa fa-angle-right'></i>"],
          margin: 10,
          stopOnHover : true,
          animateIn: 'slideInRight',
          animateOut: 'slideOutLeft',
          autoplayHoverPause: true,
          responsive: {
            0: {
              items: 1,
            },
            768: {
              items: 1,
            },
            1170: {
              items: 1,
            }
          }
      });  
  
      
      
      // // Smooth Scroll
      //     $(function() {
      //       $('a[href*=#]:not([href=#])').click(function() {
      //         if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      //           var target = $(this.hash);
      //           target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      //           if (target.length) {
      //             $('html,body').animate({
      //               scrollTop: target.offset().top
      //             }, 600);
      //             return false;
      //           }
      //         }
      //       });
      //     });
          
          
          
      /*
      |=================
      | CONTACT FORM
      |=================
      */
          
        $("#contactForm").validator().on("submit", function (event) {
            if (event.isDefaultPrevented()) {
              // handle the invalid form...
              formError();
              submitMSG(false, "Did you fill in the form properly?");
            } else {
              // everything looks good!
              event.preventDefault();
              submitForm();
            }
         });
      
          function submitForm(){
            var name = $("#name").val();
            var email = $("#email").val();
            var message = $("#message").val();
            $.ajax({
                type: "POST",
                url: "process.php",
                data: "name=" + name + "&email=" + email + "&message=" + message,
                success : function(text){
                    if (text == "success"){
                        formSuccess();
                      } else {
                        formError();
                        submitMSG(false,text);
                      }
                  }
              });
          }
          function formSuccess(){
              $("#contactForm")[0].reset();
              submitMSG(true, "Message Sent!")
          }
            function formError(){   
              $("#contactForm").removeClass().addClass('shake animated').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
                  $(this).removeClass();
              });
            }
          function submitMSG(valid, msg){
            if(valid){
              var msgClasses = "h3 text-center fadeInUp animated text-success";
            } else {
              var msgClasses = "h3 text-center shake animated text-danger";
            }
            $("#msgSubmit").removeClass().addClass(msgClasses).text(msg);
          } 
  }(jQuery));
  