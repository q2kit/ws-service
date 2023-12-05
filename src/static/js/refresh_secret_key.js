var $$ = $;

$$(document).ready(function() {
    $$(".field-secret_key").find(".readonly").append(`<i
        id='refresh_btn'
        class='fa fa-refresh'
        aria-hidden='true'
        title='Refresh'
        style='cursor: pointer; margin-left: 10px;'
    />`);
    setTimeout(function() {
        $$("#refresh_btn").click(function() {
            if (confirm("Are you sure you want to refresh the secret key?") == false) {
                return;
            }
            let project = $$("#id_name").val();
            let url = "/api/refresh_secret_key/" + project + "/";
            $$.ajax({
                url: url,
                type: "POST",
                success: function(data) {
                    location.reload();
                },
                error: function(data) {
                    alert("Failed to refresh secret key.\nPlease contact the administrator.");
                },
                timeout: 10000,
            });
        });
    }, 1000);

});