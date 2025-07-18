/**
 * PASSWD FORM SCRIPTS
 * Description: Custom JS script to handle the password form
 */

function getBaseUrl(fullUrl) {
  const url = new URL(fullUrl);
  const pathSegments = url.pathname.split('/');
  const punIndex = pathSegments.findIndex(segment => segment === 'pun');
  if (punIndex !== -1) {
      const basePath = pathSegments.slice(0, punIndex + 3).join('/');
      return `${url.origin}${basePath}`;
  }
  return url.origin;
}

const url = getBaseUrl(window.location.href);


function redirection(){
  window.location.href = window.location.href;
}

const dismissButton = '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';

$(document).ready(function () {
  // Toggle password visibility
  $(".toggle-password").on("click", function () {
    let input = $(this).closest(".input-group").find("input");
    let type = input.attr("type") === "password" ? "text" : "password";
    input.attr("type", type);
    $(this).find("i").toggleClass("bx-show bx-hide");
  });

  // Update password AJAX request
  $("#UpdatePassword").on("click", function () {
    let currentPassword = $("#CurrentPassword").val().trim();
    let newPassword = $("#NewPassword").val().trim();
    let repeatPassword = $("#RepeatPassword").val().trim();

    if (!currentPassword || !newPassword || !repeatPassword) {
      $("#message").html(`<div class="alert alert-warning alert-dismissible fade show" role="alert"><strong>WARNING ::</strong> All fields are required! ${dismissButton}</div>`);
      return;
    }

    if (newPassword !== repeatPassword) {
      $("#message").html(`<div class="alert alert-warning alert-dismissible fade show" role="alert"><strong>WARNING ::</strong> New password and repeat password must match! ${dismissButton}</div>`);
      return;
    }

    $.ajax({
      url: url+"/update_password",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        old_password: currentPassword,
        new_password: newPassword,
        confirm_password: repeatPassword
      }),
      success: function (response) {
        if (response.status === true) {
          $("#message").html(`<div class="alert alert-success alert-dismissible fade show" role="alert"><strong>SUCCESS ::</strong> ${response.message} ${dismissButton}</div>`);
          $("#CurrentPassword, #NewPassword, #RepeatPassword").val("");
        } else {
          $("#message").html(`<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>ERROR ::</strong> ${response.message} ${dismissButton}</div>`);
        }
      },
      error: function (xhr) {
        $("#message").html(`<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>ERROR ::</strong> `+(xhr.responseJSON?.message || 'Failed to update password')+` ${dismissButton}</div>`);
      }
    });
  });

  // Reset form fields
  $("#ResetPassword").on("click", function () {
    $("#CurrentPassword, #NewPassword, #RepeatPassword").val("");
  });

  // Navigate to home page on cancel
  $("#CancelPassword").on("click", function () {
    window.location.href = "/";
  });
});