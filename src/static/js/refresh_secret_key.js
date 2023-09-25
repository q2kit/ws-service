var $$ = $;

$$(document).ready(function () {
    $$(".field-secret_key > div > div").attr("style", "display: inline-block;");
    $$(".field-secret_key > div").append("<i id='refresh_btn' class='fa fa-refresh' aria-hidden='true' title='Refresh'></i>");
    setTimeout(function () {
        $$("#refresh_btn").click(function () {
            if (confirm("Are you sure you want to refresh the secret key?") == false) {
                return;
            }
            let project = $$(".field-name > div > input").val();
            let url = "/admin/api/refresh_secret_key/" + project + "/";
            $$.ajax({
                url: url,
                type: "POST",
                success: function (data) {
                    location.reload();
                }
            });
        });
    }, 1000);

});