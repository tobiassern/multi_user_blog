jQuery(function($) {
	$(window).scroll(function(){
	  	if ($(this).scrollTop() > 50) {
	      	$('#subHeader').addClass('fixed'); // when scrolling down more than 50 px add class fixed
	  	} else {
	      	$('#subHeader').removeClass('fixed'); // when scrolling less than 50 px remove class fixed
	  	}
	});
	if ($(window).scrollTop() > 50) {
		$('#subHeader').addClass('fixed'); // add the class fixed to the subheader if scrolled down 50px or more from top when pages loaded
	}
	function loadBgImg() {
		// Checks for all divs with the class .lazybg
		var bgLazy = $('.lazybg');

		$.each(bgLazy, function() {
			// Goes through each one
				var imgDiv = $(this);
				// Checks if it is in view by using isOnScreen
			if (imgDiv.isOnScreen() === true) {
				var bgImg = imgDiv.attr('data-bgimg'); // fetch the img url
				if(bgImg) {
					imgDiv.css('opacity', '0');
					$('<img src="'+ bgImg +'">').load(function() {
						imgDiv.removeClass("lazybg"); // remove the class so we don't check this one next time
						imgDiv.css('background-image', 'url(' + bgImg + ')').animate({
						    opacity: 1
						  }, 1000); // add the img as background image and add som fancy transition
					});
				}
			}
		});
	}
	$( window ).scroll(function() {
		// Calling the loadBgImg funtion on scroll
		loadBgImg();
	});
	$( window ).resize(function() {
		// Calling the loadBgImg funtion on resizing of the window
		loadBgImg();
	});
	// Calling the loadBgImg when document is ready
	loadBgImg();

	$('body').on('click', '.btn-delete', function(e) {
		 if(!confirm('Are you sure you want to delete this?')){
		     e.preventDefault();
		 }
	});

	// Lisetning to changes in the input file upload field for images
	$('.img-file-upload').bind('change', function() {
	  // Checkes so the size is not over 1 mb
	  $('.image-error').remove(); // If user already uploaded a file that is to big remove the image-error
	  if (this.files[0].size/1000000 > 1) {
	  	$(this).after('<p class="image-error">The image is to large</p>'); // add warning below input field
	  	$(this).val(''); // empties input field
	  }

	});

});
jQuery.fn.isOnScreen = function(){

    var win = $(window); // defines var win to the window

    var viewport = {
        top : win.scrollTop(),
        left : win.scrollLeft()
    }; // defines the viewport
    viewport.right = viewport.left + win.width(); // defines the width of the viewport
    viewport.bottom = viewport.top + win.height(); // defines the height of the viewport

    var bounds = this.offset(); // defines the bounds
    bounds.right = bounds.left + this.outerWidth(); // defines the width of the bounds
    bounds.bottom = bounds.top + this.outerHeight(); // defines the height of the bounds

    // Checks if the div is on screen by checking if the bounds is inside the viewport
    return (!(viewport.right < bounds.left || viewport.left > bounds.right || viewport.bottom < bounds.top || viewport.top > bounds.bottom));

};