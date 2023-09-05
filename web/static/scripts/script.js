$(document).ready(function () {
  const amenities = [];
  const amen_ids = [];
  const city_ids = [];
  const states = [];
  const state_ids = [];

  $('.amenities input').on('change', function () {
    // Check if the checkbox is checked
    let amen_list = '';
    if ($(this).is(':checked')) {
      // Fetch the data-name attribute and store it in a variable
      const dataName = $(this).data('name');
      const dataId = $(this).data('id');
      // check if amenity name is already in list
      if (amenities.indexOf(dataName) === -1) {
        amenities.push(dataName);
        amen_ids.push(dataId);
      }
      amen_list = amenities.join(', ');
    } else {
      // if unchecked, delete name from amenities list
      const uncheckedData = $(this).data('name');
      const uncheckedId = $(this).data('id');
      const index = amenities.indexOf(uncheckedData);
      const index_id = amen_ids.indexOf(uncheckedId);
      if (index !== -1) {
        amenities.splice(index, 1);
        amen_ids.splice(index_id, 1);
      }
      amen_list = amenities.join(', ');
    }
    // render the list to h4 element
    $('.amenities h4').text(amen_list);
  });

  $('.states').on('change', function () {
    // Check if the checkbox is checked
    let state_list = '';
    if ($(this).is(':checked')) {
      // Fetch the data-name attribute and store it in a variable
      const dataName = $(this).data('name');
      const dataId = $(this).data('id');
      // check if state name is already in list
      if (states.indexOf(dataName) === -1) {
        states.push(dataName);
        state_ids.push(dataId);
      }
      state_list = states.join(', ');
    } else {
      // if unchecked, delete name from states list
      const uncheckedData = $(this).data('name');
      const uncheckedId = $(this).data('id');
      const index = states.indexOf(uncheckedData);
      const index_id = state_ids.indexOf(uncheckedId);
      if (index !== -1) {
        states.splice(index, 1);
        state_ids.splice(index_id, 1);
      }
      state_list = states.join(', ');
    }
    console.log(state_list);
    // render the list to h4 element
    $('.locations h4').text(state_list);
  });

  $('.cities').on('change', function () {
    if ($(this).is(':checked')) {
      const dataId = $(this).data('id');
      // check if city id is already in list
      if (city_ids.indexOf(dataId) === -1) {
        city_ids.push(dataId);
      }
    } else {
      const uncheckedId = $(this).data('id');
      const indexId = city_ids.indexOf(uncheckedId);
      if (indexId !== -1) {
        city_ids.splice(indexId, 1);
      }
    }
  });

  // toggle show and hide reviews when span clicked
  $('.reviews span').on('click', function () {
    if (('.reviews span').attr('value') == 'hide') {
      // empty all reviews
    } else {
      // fetch all reviews and display
      // // change span value to hide
    }
  });

  function updateApiStatus (status) {
    const apiStatusDiv = $('#api_status');
    if (status === 'OK') {
      console.log('API status is ok');
      apiStatusDiv.addClass('available');
    } else {
      console.log('API is not live');
      apiStatusDiv.removeClass('available');
    }
  }

  // Function to fetch the API status
  function fetchApiStatus () {
    $.get('http://0.0.0.0:5001/api/v1/status/')
      .done(function (data) {
        const status = data.status;
        updateApiStatus(status);
      })
      .fail(function (error) {
        console.error('Error fetching API status:', error);
      });
  }

  function createReviewElement (review) {
    const reviewDiv = $('<div>').addClass('reviews');
    const reviewTitle = $('<h2>').text(`${review.length} Review${review.length !== 1 ? 's' : ''}`);
    const display = $('<span>'
    const reviewList = $('<ul>');

    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    review.forEach(function (item) {
	    // fetch user related to the review
	    $.ajax({
		    url: `http://0.0.0.0:5001/api/v1/users/${item.user_id}`,
		    type: 'GET',
		    dataType: 'json',
		    success: function (data) {
			    const fName = data.first_name;
			    const lName = data.last_name;
			    const listItem = $('<li>');
			    const reviewDate = new Date(item.updated_at);
			    const month = months[reviewDate.getMonth()];
			    const dateStr = `${reviewDate.getDate()} ${month} ${reviewDate.getFullYear()}`;
			    const reviewHeader = $('<h3>').text(`From ${fName} ${lName} ${dateStr}`);
			    const reviewText = $('<p>').html(item.text);

			    listItem.append(reviewHeader, reviewText);
			    reviewList.append(listItem);
		    },
		    error: function (error) {
			    console.error('Error fetching review user:', error);
		    }
	    });
    });
    reviewDiv.append(reviewTitle, reviewList);
    return reviewDiv;
  }

  function createPlaceArticle (place, review) {
    const article = $('<article>');

    const titleBox = $('<div>').addClass('title_box');
    const title = $('<h2>').text(place.name);
    const price = $('<div>').addClass('price_by_night').text('$' + place.price_by_night);
    titleBox.append(title, price);

    const information = $('<div>').addClass('information');
    const maxGuests = $('<div>').addClass('max_guest').text(place.max_guest + ' Guest' + (place.max_guest !== 1 ? 's' : ''));
    const numberRooms = $('<div>').addClass('number_rooms').text(place.number_rooms + ' Bedroom' + (place.number_rooms !== 1 ? 's' : ''));
    const numberBathrooms = $('<div>').addClass('number_bathrooms').text(place.number_bathrooms + ' Bathroom' + (place.number_bathrooms !== 1 ? 's' : ''));
    information.append(maxGuests, numberRooms, numberBathrooms);

    const description = $('<div>').addClass('description').html(place.description);
    article.append(titleBox, information, description);

    return article;
  }

  // Function to fetch places
  function fetchPlaces () {
    const filterData = {
	    states: state_ids,
	    cities: city_ids,
	    amenities: amen_ids
    };
    $.ajax({
      url: 'http://0.0.0.0:5001/api/v1/places_search',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(filterData),
      dataType: 'json',
      success: function (data) {
        const placesSection = $('section.places');
        placesSection.empty();
        if (amen_ids.length > 0) {
          console.log(`${data.length} places filtered`); // check if filter works
        }
        if (data.length > 0) {
          data.forEach(function (place) {
		  const article = createPlaceArticle(place);
		  placesSection.append(article);

		   $.ajax({
              url: `http://0.0.0.0:5001/api/v1/places/${place.id}/reviews`,
              type: 'GET',
              dataType: 'json',
              success: function (reviews) {
                const reviewsDiv = createReviewElement(reviews);
                article.append(reviewsDiv);
              },
              error: function (error) {
                console.error('Error fetching reviews:', error);
              }
		   });
	  });
        }
      },
	    error: function (error) {
		    console.error('Error fetching places:', error);
	    }
    });
  }
  $('button').on('click', fetchPlaces);
  fetchPlaces(); // fetch places regardless of filter
  fetchApiStatus();
});
