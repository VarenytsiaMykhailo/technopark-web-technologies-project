const $paginationForm = $("#pagination_form");
const $paginationPage = $("#pagination_page");
const paginationFormSubmit = page => {
	$paginationPage.val(page);
	$paginationForm.submit();
};