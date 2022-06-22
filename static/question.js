const $questionRating = $("#question_rating");
const $questionRatingForm = $("#question_rating_form");
const $questionRatingLike = $("#question_rating_like");
const $questionRatingPictureDislike = $("#question_rating_picture_dislike");
const $questionRatingPictureLike = $("#question_rating_picture_like");
const $questionRatingRated = $("#question_rating_rated");

const csrftoken = Cookies.get("csrftoken");
$.ajaxSetup({
	beforeSend: (xhr, settings) => {
		if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	}
});

const ajax = data => $.ajax({
	data: data,
	error: response => {
		alert("Ошибка. " + response.responseText);
		console.log(response.responseText);
	},
	type: "POST"
});

if ($questionRatingRated.prop("checked")) {
	if ($questionRatingLike.prop("checked")) {
		$questionRatingPictureLike.toggleClass("text-success");
	} else {
		$questionRatingPictureDislike.toggleClass("text-danger");
	}
}

$questionRatingPictureDislike.on("click", () => {
	$questionRatingPictureDislike.toggleClass("text-danger");
	const rating = parseInt($questionRating.text(), 10);
	let ratingIsNew = true;
	if ($questionRatingPictureLike.hasClass("text-success")) { // Лайк заменён на дизлайк
		$questionRatingPictureLike.removeClass("text-success");
		if (rating === 2) {
			$questionRating.removeClass("text-success");
		} else if (rating === 1) {
			$questionRating.removeClass("text-success");
			$questionRating.addClass("text-danger");
		}
		$questionRating.text(rating - 2);
	} else if ($questionRatingPictureDislike.hasClass("text-danger")) { // Дизлайк поставлен
		if (rating === 1) {
			$questionRating.removeClass("text-success");
		} else if (rating === 0) {
			$questionRating.addClass("text-danger");
		}
		$questionRating.text(rating - 1);
	} else { //дизлайк убран
		if (rating === -1) {
			$questionRating.removeClass("text-danger");
		} else if (rating === 0) {
			$questionRating.addClass("text-success");
		}
		$questionRating.text(rating + 1);
		ratingIsNew = false;
	}
	$questionRatingLike.prop("checked", false);
	ajax($questionRatingForm.serialize());
	$questionRatingRated.prop("checked", ratingIsNew);
});
$questionRatingPictureLike.on("click", () => {
	$questionRatingPictureLike.toggleClass("text-success");
	const rating = parseInt($questionRating.text(), 10);
	let ratingIsNew = true;
	if ($questionRatingPictureDislike.hasClass("text-danger")) { // Дизлайк заменён на лайк
		$questionRatingPictureDislike.removeClass("text-danger");
		if (rating === -2) {
			$questionRating.removeClass("text-danger");
		} else if (rating === -1) {
			$questionRating.removeClass("text-danger");
			$questionRating.addClass("text-success");
		}
		$questionRating.text(rating + 2);
	} else if ($questionRatingPictureLike.hasClass("text-success")) { // Лайк поставлен
		if (rating === -1) {
			$questionRating.removeClass("text-danger");
		} else if (rating === 0) {
			$questionRating.addClass("text-success");
		}
		$questionRating.text(rating + 1);
	} else { //лайк убран
		if (rating === 1) {
			$questionRating.removeClass("text-success");
		} else if (rating === 0) {
			$questionRating.addClass("text-danger");
		}
		$questionRating.text(rating - 1);
		ratingIsNew = false;
	}
	$questionRatingLike.prop("checked", true);
	ajax($questionRatingForm.serialize());
	$questionRatingRated.prop("checked", ratingIsNew);
});

const commentFormOnSubmit = ($commentForm, $comments) => {
	const avatarUrl = $commentForm.data("avatar-url");
	const profileName = $commentForm.data("profile-name");
	const profileUrl = $commentForm.data("profile-url");
	const id = "comment_" + new Date().getTime();
	$comments.prepend("<div class='media mb-4' id='" + id + "'>\n" +
		"\t<a href='" + profileUrl + "'>\n" +
		"\t\t<img alt='Аватар пользователя' class='d-flex mr-3 rounded-circle avatar64' src='" + avatarUrl + "'>\n" +
		"\t</a>\n" +
		"\t<div class='media-body'>\n" +
		"\t\t<h5 class='mt-0'><a href='" + profileUrl + "'>" + profileName + "</a></h5>\n" +
		"\t\t" + $commentForm.find("textarea[name='text']").val() + "\n" +
		"\t</div>\n" +
		"</div>");
	ajax($commentForm.serialize());
	$commentForm.trigger("reset");
	$("html,body").animate({
		scrollTop: $("#" + id).offset().top - 66 // В будущем переделать: 1) выборка по id; 2) магические числа
	}, 500);
};
