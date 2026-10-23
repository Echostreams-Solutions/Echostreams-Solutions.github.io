/*$(document).ready(function() {

        var tabOffset = 0;
        var priceOffset = 0;
  
        function MakeSticky(elementName, offsetValueWhenSticky, stickyClassName, initVarName) {
          var currentOffset = $(elementName).offset().top;
          var scrollTop = $(window).scrollTop();
        
          if (eval(initVarName + " == 0")) {
              eval(initVarName + " = currentOffset");
          }

          var distance = eval(initVarName + " - scrollTop");
  
        if (distance <= offsetValueWhenSticky) {
              $(elementName).addClass(stickyClassName)
            } else {
              $(elementName).removeClass(stickyClassName);
            }
      }
  
      $(document).scroll(function(){
          MakeSticky('#tab-navbar', 70, 'sticky', 'tabOffset');
          MakeSticky('#configuration-price', 100, 'sticky-pricing', 'priceOffset');
        });
  
        $(window).resize(function() {
          tabOffset = 0;
          priceOffset = 0;
          MakeSticky('#tab-navbar', 70, 'sticky', 'tabOffset');
          MakeSticky('#configuration-price', 100, 'sticky-pricing', 'priceOffset');
        });

});
*/

$(document).ready(function() {

  //blog pagination

  $('.tab-links').stick_in_parent({
    offset_top:0,
    parent: '.tab-container',
  });


   $(document).on("scroll",onScrollTabLinks);
   $(document).on("scroll",onScrollHeader);
   $(document).on("click",".tab-links a[href^='#']:not('.active')",function (e) {
        e.stopPropagation();
        e.preventDefault();
        $(document).off("scroll");
        
        $('a').each(function () {
            $(this).removeClass('active');
        })
        $(this).addClass('active');
        var target = this.hash,
            menu = target;
        $target = $(target);
        $('html, body').stop().animate({
            scrollTop: $target.offset().top
        }, 500, 'swing', function () {
            window.location.hash = target;
            prevScrollPos = window.innerHeight+window.pageYOffset;
            $(document).on("scroll", onScrollTabLinks);
            $(document).on("scroll",onScrollHeader);
           
        })
        $(this).hide().show(0);    
    })
    .on("click",".tab-links a.active",function(event){
        var list = $(this).closest('ul');

        if (list.hasClass('open'))
        $(this).closest("ul").removeClass('open');
      else
        $(this).closest("ul").addClass('open');

        if($('.tab-links').hasClass('expand'))
        $('.tab-links').removeClass('expand');
        else
          $('.tab-links').addClass('expand');
        

        
        event.stopPropagation();
        event.preventDefault();
        $('.tab-links').hide().show(0);

    });
    

$(document).click(function (event){
  var clickover = $(event.target);
  var _opened = $('.tab-links ul').hasClass('open');
  if(_opened === true && !clickover.hasClass('toggle-nav')){
    $('.tab-links ul').removeClass('open');
    $('.tab-links').removeClass('expand'); 
  }
  $(this).hide().show(0);
});

var tabPosition = [];
$('.tab-links ul li a').each(function(){
  tabPosition.push($($(this).attr("href")).position().top);
})


$(window).resize(function(){
  tabPosition = [];
  $('.tab-links ul li a').each(function(){
  tabPosition.push($($(this).attr("href")).position().top);
});

});


var prevScrollPos = window.pageYOffset;
var lastScrollTop = 0;
var delta = 5;
var navbarHeight = $('.site-header').first().outerHeight();

function onScrollHeader(event){
      var st = $(this).scrollTop();
    
    // Make sure they scroll more than delta
    if(Math.abs(lastScrollTop - st) <= delta)
        return;
    
    // If they scrolled down and are past the navbar, add class .nav-up.
    // This is necessary so you never see what is "behind" the navbar.
    if (st > lastScrollTop && st > navbarHeight){
        // Scroll Down
        
        if(st + $(window).height() < $(document).height()) {
            $('.site-header').first().css("top","-70px")
            if($('.tab-links').hasClass("is_stuck")){
              $('.tab-links').first().css("top","0");

    }
        }
    } else {
        // Scroll Up


        $('.site-header').first().css( "top", "0px")
        if($('.tab-links').hasClass("is_stuck")){
      $('.tab-links').first().css("top","70px");
    }
    }
    
    lastScrollTop = st;
    $('.tab-links').hide().show(0);

   // var currentScrollPos = window.pageYOffset;
   // console.log("prevScroll pos :" + prevScrollPos + "     > currentScrollPos   : " + currentScrollPos);
   // if(prevScrollPos > currentScrollPos){
   //  $('.site-header').first().css( "top", "0px")
   //  if($('.tab-links').hasClass("is_stuck")){
   //    $('.tab-links').first().css("top","70px");
   //  }
   // }
   // else {
   //  $('.site-header').first().css("top","-70px")
   //  if($('.tab-links').hasClass("is_stuck")){
   //    $('.tab-links').first().css("transition","top 0.3s");
   //    $('.tab-links').first().css("top","0");

   //  }
   // }
   // prevScrollPos = currentScrollPos;
}
function onScrollTabLinks(event){
var scrollPos = $(document).scrollTop();
    $('.tab-links ul li a').each(function (index) {


        var currLink = $(this);
        var refElement = $(currLink.attr("href"));



        // console.log("start href: " + $(this).attr("href"));
        // console.log($(currLink.attr("href")).position().top + "<= " + $(document).scrollTop());
        // var wid = +refElement.position().top+refElement.height();
        // console.log("position top: " +refElement.position().top + " + " +refElement.height()     + "= " +wid+" > " + scrollPos);
        
        if(tabPosition[index] <= scrollPos && tabPosition[index] + refElement.height() > scrollPos){
          $('.tab-links ul li a').removeClass("active");
            currLink.addClass("active");
          
        }
        else
        {
          currLink.removeClass("active");

        }


        // if (refElement.position().top <= scrollPos && refElement.position().top + refElement.height() > scrollPos) {
        //     $('.tab-links ul li a').removeClass("active");
        //     currLink.addClass("active");
        // }
        // else{
        //     currLink.removeClass("active");
        // }
    });
    $('.tab-links ul').removeClass("open");
     $('.tab-links').removeClass("expand");
     $('.tab-links').hide().show(0);
   }
});