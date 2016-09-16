var month = new Array();
month[0] = "Jan";
month[1] = "Feb";
month[2] = "Mar";
month[3] = "Apr";
month[4] = "May";
month[5] = "Jun";
month[6] = "Jul";
month[7] = "Aug";
month[8] = "Sep";
month[9] = "Oct";
month[10] = "Nov";
month[11] = "Dec";

jQuery(function($) {
	$(window).scroll(function(){
	  	if ($(this).scrollTop() > 50) {
	      	$('#subHeader').addClass('fixed');
	  	} else {
	      	$('#subHeader').removeClass('fixed');
	  	}
	});
	if ($(window).scrollTop() > 50) {
		$('#subHeader').addClass('fixed');
	}
	function loadBgImg() {
		var bgLazy = $('.lazybg');

		$.each(bgLazy, function() {
				var imgDiv = $(this);
			if (imgDiv.isOnScreen() == true) {
				var bgImg = imgDiv.attr('data-bgimg');
				if(bgImg) {
					imgDiv.css('opacity', '0');
					$('<img src="'+ bgImg +'">').load(function() {
						imgDiv.removeClass("lazybg");
						imgDiv.css('background-image', 'url(' + bgImg + ')').animate({
						    opacity: 1
						  }, 1000);
					});
				}
			}
		});
	}
	$( window ).scroll(function() {
		loadBgImg();
	});
	$( window ).resize(function() {
		loadBgImg();
	});
	loadBgImg();

	$('body').on('click', '.btn-delete', function(e) {
		 if(!confirm('Are you sure you want to delete this?')){
		     e.preventDefault();
		 }
	});

	//binds to onchange event of your input field
	$('.img-file-upload').bind('change', function() {
	  //this.files[0].size gets the size of your file.
	  if (this.files[0].size/1000000 > 1) {
	  	$(this).after('<p class="image-error">The image is to large</p>');
	  	$(this).val('');
	  }
	  else {
	  	$('.image-error').remove();
	  }

	});

	$('body').on('click', '.like-icon', function() {
		likeBtn = $(this);
		likesCount = likeBtn.next('.likes-count');
		likesCountNum = parseInt(likesCount.text());
		if(likeBtn.hasClass('liked')) {
			likeBtn.removeClass('liked');
			likeBtn.attr('title', 'Like this post');
			likesCountNum--;
			likesCount.text(likesCountNum);
		} else {
			likeBtn.addClass('liked');
			likeBtn.attr('title', 'Unlike this post');
			likesCountNum++;
			likesCount.text(likesCountNum);
		}
	});

});
jQuery.fn.isOnScreen = function(){

    var win = $(window);

    var viewport = {
        top : win.scrollTop(),
        left : win.scrollLeft()
    };
    viewport.right = viewport.left + win.width();
    viewport.bottom = viewport.top + win.height();

    var bounds = this.offset();
    bounds.right = bounds.left + this.outerWidth();
    bounds.bottom = bounds.top + this.outerHeight();

    return (!(viewport.right < bounds.left || viewport.left > bounds.right || viewport.bottom < bounds.top || viewport.top > bounds.bottom));

};