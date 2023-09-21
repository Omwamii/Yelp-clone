$(document).ready(function () {
  // const likeBtn = $(".like-btn");

  // function updateLikes () {
  //   console.log("Like btn clicked");
  //   const currentLikes = parseInt($.trim($("#likes").text()));

  //   console.log($.trim($("#likes").text())); //test likes number

  //   let updatedLikes = currentLikes + 1;
  //   btn_status = likeBtn.css("color"); // if yellow, button was already clicked, if white not yet

  //   console.log(btn_status);
  //   if (btn_status === "rgb(255, 255, 0)") {
  //     // reduce like count
  //     updatedLikes = currentLikes - 1;
  //   } else {
  //     // increase like count
  //     updatedLikes = currentLikes + 1;
  //   }
  //   console.log(`New likes count: ${updatedLikes}`);

  //   const update_data = {
  //     'found_useful': updatedLikes 
  //   };
  //   const reviewId = likeBtn.val(); // id of the review object

  //   console.log(`Review id: ${reviewId}`);

  //   $.ajax({
  //     url: `http://192.168.230.101:5500/update_review/${reviewId}`,
  //     type: 'GET',
  //     contentType: 'application/json',
  //     data: JSON.stringify(update_data),
  //     dataType: 'json',
  //     success: function (data) {
  //       console.log(data.status_code);
  //       // update the likes count
  //       $("#likes").text(updatedLikes);
  //       // change the color of the like button to Yellow permanently
  //       if (btn_status !== "rgb(255, 255, 0)") {
  //         likeBtn.css("color", "rgb(255, 255, 0)");
  //       } else {
  //         likeBtn.css("color", "rgb(0, 0, 0)"); // review is unliked
  //       }
  //     },
	//     error: function (error) {
	// 	    console.error('Error updating likes :(', error);
	//     }
  //   });
  // }
  // likeBtn.on('click', updateLikes);
});
