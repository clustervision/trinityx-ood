/**
 * PASSWD FORM SCRIPTS
 * Description: Custom JS script to handle the password form
 */
// document.addEventListener("DOMContentLoaded", function () {
//   // Toggle password visibility
//   document.querySelectorAll(".input-group-text").forEach(span => {
//     span.addEventListener("click", function () {
//       const input = this.previousElementSibling;
//       console.log(input);
//       if (input.type === "password") {
//         input.type = "text";
//         this.innerHTML = '<i class="bx bx-hide"></i>'; // Change icon
//       } else {
//         input.type = "password";
//         this.innerHTML = '<i class="bx bx-show"></i>'; // Reset icon
//       }
//     });
//   });

//   // Navigate to home page on Cancel
//   document.querySelector("button[type='cancel']").addEventListener("click", function () {
//     window.location.href = window.location.href;
//   });

//   // Reset form fields
//   document.querySelector("button[type='reset']").addEventListener("click", function () {
//     document.getElementById("currentPassword").value = "";
//     document.getElementById("NewPassword").value = "";
//     document.getElementById("RepeatPassword").value = "";
//   });
// });


function color_message(message=null){
  if  (message.includes('error') || message.includes('undefined') || message.includes('failed')){
      message = "<span style='color:red;'>" + message + "</span><br />";
  } else {
      message = "<span style='color:yellow;'>" + message + "</span><br />";
  }
  return message
}

function redirection(){
  window.location.href = window.location.href;
}








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
      alert("All fields are required!");
      return;
    }

    if (newPassword !== repeatPassword) {
      alert("New password and repeat password must match!");
      return;
    }

    $.ajax({
      
      url: "/update_password",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        old_password: currentPassword,
        new_password: newPassword,
        confirm_password: repeatPassword
      }),
      success: function (response) {
        console.log(currentPassword);
      console.log(newPassword);
      console.log(repeatPassword);
        alert("Password updated successfully!");
        $("#CurrentPassword, #newPassword, #repeatPassword").val("");
      },
      error: function (xhr) {
        alert("Error: " + (xhr.responseJSON?.message || "Failed to update password"));
      }
    });
  });

  // Reset form fields
  $("#ResetPassword").on("click", function () {
    $("#CurrentPassword, #NewPassword, #RepeatPassword").val("");
  });

  // Navigate to home page on cancel
  $("#CancelPassword").on("click", function () {
    window.location.href = window.location.href ;
  });
});